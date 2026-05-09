import os
import random

import requests
import tidalapi

from config import Config


class TidalDownloader:
    def __init__(self, session):
        self.session = session
        self.session.audio_quality = tidalapi.Quality.low_320k

    def download_playlists(self, playlists: dict):
        print(
            f"[Info] Starting download process. Max tracks per playlist: {Config.DOWNLOAD_MAX}"
        )

        selected_tracks = []

        for playlist_name, playlist_id in playlists.items():
            print(f"[Info] Processing playlist: {playlist_name}")
            try:
                playlist = self.session.playlist(playlist_id)
                tracks = playlist.tracks()

                if not tracks:
                    print(f"[Warning] No tracks found in {playlist_name}. Skipping.")
                    continue

                random.shuffle(tracks)
                tracks_to_download = tracks[: Config.DOWNLOAD_MAX]

                for track in tracks_to_download:
                    safe_title = "".join(
                        c for c in track.name if c.isalnum() or c in " -_"
                    ).strip()
                    file_name = f"{playlist_name}_{track.id}_{safe_title}.m4a"
                    selected_tracks.append((file_name, track))

            except Exception as e:
                print(f"[Error] Failed to process playlist {playlist_name}: {e}")

        expected_files = [f[0] for f in selected_tracks]
        self._clean_old_downloads(expected_files)
        self._download_tracks(selected_tracks)

    def _clean_old_downloads(self, expected_files: list):
        print("\n[Info] Cleaning up unused audio files...")
        try:
            for file_name in os.listdir(Config.LOCAL_MUSIC_DIR):
                file_path = os.path.join(Config.LOCAL_MUSIC_DIR, file_name)
                if os.path.isfile(file_path) and file_name not in expected_files:
                    os.remove(file_path)
                    print(f"  [Deleted] {file_name}")
        except Exception as e:
            print(f"[Error] Failed during cleanup: {e}")

    def _download_tracks(self, selected_tracks: list):
        print("\n[Info] Verifying and downloading tracks...")
        for i, (file_name, track) in enumerate(selected_tracks):
            try:
                file_path = os.path.join(Config.LOCAL_MUSIC_DIR, file_name)

                if os.path.exists(file_path):
                    print(
                        f"  [{i + 1}/{len(selected_tracks)}] Skipping (already exists): {file_name}"
                    )
                    continue

                print(
                    f"  [{i + 1}/{len(selected_tracks)}] Downloading (320kbps): {file_name}..."
                )

                stream_url = track.get_url()

                if not stream_url:
                    print(
                        f"  [Warning] No stream URL available for {file_name}. Skipping."
                    )
                    continue

                response = requests.get(stream_url, stream=True)
                response.raise_for_status()

                with open(file_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

            except Exception as e:
                print(f"  [Error] Failed to download {track.name}: {e}")
