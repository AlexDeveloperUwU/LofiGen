import logging
import os
import random
import subprocess
from concurrent.futures import ThreadPoolExecutor

from config import Config
from history import HistoryManager


class AudioMixer:
    def __init__(self, history_manager: HistoryManager):
        self.target_duration_sec = Config.DURATION_HOURS * 3600
        self.history = history_manager

    def get_track_duration(self, file_path: str) -> float:
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            file_path,
        ]
        try:
            output = subprocess.check_output(cmd).decode("utf-8").strip()
            return float(output)
        except Exception as e:
            logging.error(f"Could not get duration for {file_path}: {e}")
            return 0.0

    def select_optimal_tracks(self, pool: list) -> list:
        selected = []
        current_duration = 0.0

        for i, (path, duration, file_name) in enumerate(pool):
            if current_duration >= self.target_duration_sec:
                break

            if current_duration + duration > self.target_duration_sec:
                remaining = pool[i:]
                valid_candidates = [
                    x
                    for x in remaining
                    if current_duration + x[1] >= self.target_duration_sec
                ]

                if valid_candidates:
                    best_fit = min(
                        valid_candidates,
                        key=lambda x: (
                            (current_duration + x[1]) - self.target_duration_sec
                        ),
                    )
                else:
                    best_fit = max(remaining, key=lambda x: x[1])

                selected.append(best_fit)
                current_duration += best_fit[1]
                break
            else:
                selected.append((path, duration, file_name))
                current_duration += duration

        logging.info(
            f"Target duration: {self.target_duration_sec}s | Actual duration: {current_duration}s"
        )
        return selected

    def _process_single_track(self, args):
        input_path, duration, file_name = args
        output_path = os.path.join(Config.PROCESSED_MUSIC_DIR, file_name)

        if os.path.exists(output_path):
            return output_path

        fade_dur = min(3.0, duration / 3.0)
        fade_out_start = duration - fade_dur

        audio_filter = f"loudnorm=I=-16:TP=-1.5:LRA=11,afade=t=in:st=0:d={fade_dur},afade=t=out:st={fade_out_start}:d={fade_dur}"

        cmd = [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-i",
            input_path,
            "-af",
            audio_filter,
            "-c:a",
            "aac",
            "-b:a",
            "96k",
            "-ar",
            "44100",
            output_path,
        ]

        try:
            subprocess.run(cmd, check=True)
            logging.info(f"Processed (Normalized + Fades): {file_name}")
            return output_path
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to process {file_name}: {e}")
            return None

    def generate_mix(self):
        logging.info(f"Selecting tracks for {Config.DURATION_HOURS}h mix...")

        all_files = [
            f
            for f in os.listdir(Config.LOCAL_MUSIC_DIR)
            if f.endswith(".m4a") and "_" in f
        ]

        if not all_files:
            logging.error("No downloaded tracks available to mix.")
            return

        pool = []
        for f in all_files:
            file_path = os.path.join(Config.LOCAL_MUSIC_DIR, f)
            duration = self.get_track_duration(file_path)
            if duration > 0:
                pool.append((file_path, duration, f))

        random.shuffle(pool)
        selected_tracks = self.select_optimal_tracks(pool)

        logging.info("Applying normalization, fades, and encoding in parallel...")
        processed_paths = []

        with ThreadPoolExecutor(max_workers=4) as executor:
            results = executor.map(self._process_single_track, selected_tracks)
            processed_paths = [res for res in results if res is not None]

        if not processed_paths:
            logging.error("No tracks were successfully processed. Aborting mix.")
            return

        used_track_ids = []
        concat_file_path = os.path.join(Config.PROCESSED_MUSIC_DIR, "concat.txt")

        with open(concat_file_path, "w", encoding="utf-8") as concat_file:
            for track_path in processed_paths:
                file_name = os.path.basename(track_path)

                parts = file_name.split("_")
                for part in parts:
                    if part.isdigit():
                        used_track_ids.append(part)
                        break

                safe_path = os.path.abspath(track_path).replace("'", "'\\''")
                concat_file.write(f"file '{safe_path}'\n")

        logging.info("Merging processed tracks instantly with FFmpeg copy...")
        cmd = [
            "ffmpeg",
            "-y",
            "-v",
            "error",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            concat_file_path,
            "-c",
            "copy",
            Config.OUTPUT_MIX_PATH,
        ]

        try:
            subprocess.run(cmd, check=True)
            logging.info(f"Mix generated successfully at: {Config.OUTPUT_MIX_PATH}")
            self.history.mark_as_played(used_track_ids)
        except subprocess.CalledProcessError as e:
            logging.error(f"FFmpeg failed to merge the mix: {e}")
