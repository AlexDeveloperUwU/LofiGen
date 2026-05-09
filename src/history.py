import json
import logging
import os
from datetime import datetime, timedelta

from config import Config


class HistoryManager:
    def __init__(self):
        self.history_file = Config.HISTORY_FILE
        self.played_tracks = self._load_history()
        self._cleanup_old_history()

    def _load_history(self) -> dict:
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Failed to load history: {e}")
        return {}

    def _cleanup_old_history(self):
        """Removes tracks from history that were played more than 7 days ago."""
        now = datetime.now()
        cutoff = now - timedelta(days=7)
        cleaned = {}

        for tid, date_str in self.played_tracks.items():
            try:
                dt = datetime.fromisoformat(date_str)
                if dt >= cutoff:
                    cleaned[tid] = date_str
            except ValueError:
                pass

        self.played_tracks = cleaned
        self._save_history()

    def is_played(self, track_id: str) -> bool:
        return str(track_id) in self.played_tracks

    def mark_as_played(self, track_ids: list):
        now_str = datetime.now().isoformat()
        for t in track_ids:
            self.played_tracks[str(t)] = now_str
        self._save_history()

    def _save_history(self):
        try:
            with open(self.history_file, "w") as f:
                json.dump(self.played_tracks, f)
            logging.info(
                f"History updated. Tracking {len(self.played_tracks)} songs played in the last 7 days."
            )
        except Exception as e:
            logging.error(f"Failed to save history: {e}")
