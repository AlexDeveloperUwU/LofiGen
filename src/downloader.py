import logging
import os
import random
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import requests
import tidalapi
from requests.adapters import HTTPAdapter, Retry
from tidalapi.exceptions import TooManyRequests

from config import Config
from history import HistoryManager

_HTTP_RETRY = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])


class TidalDownloader:
    _rate_limit_until: float = 0.0
    _rate_limit_lock = threading.Lock()

    def __init__(self, session, history_manager: HistoryManager):
        self.session = session
        self.session.audio_quality = tidalapi.Quality.low_96k
        self.history = history_manager

    def _wait_if_rate_limited(self):
        with self._rate_limit_lock:
            remaining = self._rate_limit_until - time.time()
        if remaining > 0:
            logging.info(f"Global rate-limit cooldown: waiting {remaining:.0f}s before next request...")
            time.sleep(remaining)

    def _set_rate_limited(self):
        deadline = time.time() + Config.RATE_LIMIT_COOLDOWN
        with self._rate_limit_lock:
            if deadline > self._rate_limit_until:
                self._rate_limit_until = deadline

    def download_playlists(self, playlists: dict):
        max_str = Config.DOWNLOAD_MAX if Config.DOWNLOAD_MAX > 0 else "Unlimited"
        logging.info(f"Starting cache sync. Max tracks per playlist: {max_str}")

        selected_tracks = []
        rotation_needed = set()

        for playlist_name, playlist_id in playlists.items():
            logging.info(f"Syncing playlist: {playlist_name}")

            prefix = f"{playlist_name}_"
            local_files = [
                f for f in os.listdir(Config.LOCAL_MUSIC_DIR) if f.startswith(prefix)
            ]

            current_local_ids = []
            for f in local_files:
                remainder = f[len(prefix):]
                track_id = remainder.split("_")[0]
                if track_id.isdigit():
                    current_local_ids.append(track_id)

            if Config.DOWNLOAD_MAX > 0:
                if len(local_files) >= Config.DOWNLOAD_MAX:
                    # Cache full — download a replacement batch first, rotate old tracks after
                    needed = max(1, int(Config.DOWNLOAD_MAX * 0.25))
                    rotation_needed.add(playlist_name)
                else:
                    needed = Config.DOWNLOAD_MAX - len(local_files)
            else:
                needed = float("inf")

            try:
                playlist = self.session.playlist(playlist_id)
                all_tracks = playlist.tracks()

                if not all_tracks:
                    logging.warning(
                        f"No tracks found in {playlist_name} on Tidal. Skipping."
                    )
                    continue

                fresh_tracks = [
                    t
                    for t in all_tracks
                    if str(t.id) not in current_local_ids
                    and not self.history.is_played(t.id)
                ]

                if not fresh_tracks:
                    logging.warning(
                        f"No unplayed tracks available for {playlist_name}. Exhausted 7-day pool."
                    )
                    continue

                random.shuffle(fresh_tracks)

                if needed != float("inf"):
                    tracks_to_download = fresh_tracks[:needed]
                else:
                    tracks_to_download = fresh_tracks

                for track in tracks_to_download:
                    safe_title = "".join(
                        c for c in track.name if c.isalnum() or c in " -_"
                    ).strip()
                    file_name = f"{playlist_name}_{track.id}_{safe_title}.m4a"
                    selected_tracks.append((file_name, track))

            except Exception as e:
                logging.error(f"Failed to process playlist {playlist_name}: {e}")

        if not selected_tracks:
            logging.info("No new tracks needed. Cache is fully up to date.")
            return

        self._download_tracks(selected_tracks)

        # Post-download rotation: only remove old tracks when new ones landed,
        # and never remove the files we just downloaded.
        if Config.DOWNLOAD_MAX > 0 and rotation_needed:
            for playlist_name in playlists:
                if playlist_name not in rotation_needed:
                    continue

                prefix = f"{playlist_name}_"
                playlist_fns = {fn for fn, _ in selected_tracks if fn.startswith(prefix)}

                newly_downloaded = {
                    fn for fn in playlist_fns
                    if os.path.exists(os.path.join(Config.LOCAL_MUSIC_DIR, fn))
                }

                if not newly_downloaded:
                    logging.info(
                        f"No new tracks downloaded for {playlist_name}; "
                        f"preserving existing cache for mix."
                    )
                    continue

                local_files_now = [
                    f for f in os.listdir(Config.LOCAL_MUSIC_DIR) if f.startswith(prefix)
                ]
                rotatable = [f for f in local_files_now if f not in newly_downloaded]
                num_to_remove = min(
                    max(1, int(Config.DOWNLOAD_MAX * 0.25)),
                    len(rotatable),
                )
                if num_to_remove > 0:
                    to_remove = random.sample(rotatable, num_to_remove)
                    for f in to_remove:
                        os.remove(os.path.join(Config.LOCAL_MUSIC_DIR, f))
                    logging.info(
                        f"Rotated out {num_to_remove} old cached tracks from {playlist_name}."
                    )

    def _download_single_track(self, args):
        file_name, track = args
        file_path = os.path.join(Config.LOCAL_MUSIC_DIR, file_name)

        if os.path.exists(file_path):
            return True

        for attempt in range(Config.MAX_RETRIES):
            try:
                self._wait_if_rate_limited()

                stream_url = track.get_url()
                if not stream_url:
                    logging.warning(f"No stream URL for {file_name}. Skipping.")
                    return False

                with requests.Session() as s:
                    s.mount("https://", HTTPAdapter(max_retries=_HTTP_RETRY))
                    response = s.get(stream_url, stream=True, timeout=30)
                    response.raise_for_status()
                    with open(file_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                logging.info(f"Downloaded (96kbps): {file_name}")
                return True

            except TooManyRequests:
                self._set_rate_limited()
                wait = Config.INITIAL_BACKOFF * (2 ** attempt)
                logging.warning(f"Rate limited on {track.name}, waiting {wait}s...")
                time.sleep(wait)

            except Exception as e:
                if attempt < Config.MAX_RETRIES - 1:
                    wait = 5 * (2 ** attempt)
                    logging.warning(
                        f"Attempt {attempt + 1}/{Config.MAX_RETRIES} failed for {track.name} ({e}), retrying in {wait}s..."
                    )
                    time.sleep(wait)
                else:
                    logging.error(
                        f"Failed to download {track.name} after {Config.MAX_RETRIES} attempts: {e}"
                    )
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    return False

        logging.error(
            f"Failed to download {track.name} after {Config.MAX_RETRIES} attempts: rate limited."
        )
        if os.path.exists(file_path):
            os.remove(file_path)
        return False

    def _download_tracks(self, selected_tracks: list):
        if Config.TIDAL_SEQUENTIAL:
            logging.info("Fetching missing tracks sequentially...")
            failed = []
            succeeded = 0
            for args in selected_tracks:
                if self._download_single_track(args):
                    succeeded += 1
                else:
                    failed.append(args)
                time.sleep(random.uniform(Config.REQUEST_DELAY_MIN, Config.REQUEST_DELAY_MAX))

            if failed and succeeded > 0:
                logging.info(
                    f"Retrying {len(failed)} rate-limited track(s) after "
                    f"{Config.RATE_LIMIT_COOLDOWN}s cooldown..."
                )
                time.sleep(Config.RATE_LIMIT_COOLDOWN)
                for args in failed:
                    self._download_single_track(args)
                    time.sleep(random.uniform(Config.REQUEST_DELAY_MIN, Config.REQUEST_DELAY_MAX))
        else:
            logging.info("Fetching missing tracks in parallel...")
            with ThreadPoolExecutor(max_workers=2) as executor:
                executor.map(self._download_single_track, selected_tracks)
