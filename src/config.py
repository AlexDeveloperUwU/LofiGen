import json
import logging
import os

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class Config:
    HA_HOSTNAME: str = os.getenv("HA_HOSTNAME", "homecore")
    HA_USER: str = os.getenv("HA_USER", "root")
    HA_PASSWORD: str = os.getenv("HA_PASSWORD", "")
    HA_PATH: str = os.getenv("HA_PATH", "/ha/media/LoFi.mp3")

    SESSION_FILE: str = os.getenv("TIDAL_SESSION_FILE", "./data/tidal_session.json")
    HISTORY_FILE: str = os.getenv("HISTORY_FILE", "./data/play_history.json")

    LOCAL_MUSIC_DIR: str = os.getenv("LOCAL_MUSIC_DIR", "./data/downloads")
    PROCESSED_MUSIC_DIR: str = os.getenv("PROCESSED_MUSIC_DIR", "./data/processed")
    OUTPUT_MIX_PATH: str = os.getenv("OUTPUT_MIX_PATH", "./data/output/LoFi.mp3")

    DOWNLOAD_MAX: int = int(os.getenv("TIDAL_DOWNLOAD_MAX", "50"))
    DURATION_HOURS: float = float(os.getenv("DURATION_HOURS", "4.0"))

    COVER_ART_PATH: str = os.getenv("COVER_ART_PATH", "./assets/cover.jpg")
    DAEMON_RUN_AT: str = os.getenv("DAEMON_RUN_AT", "03:00")

    @staticmethod
    def get_playlists() -> dict:
        playlists_raw = os.getenv("TIDAL_PLAYLISTS", "{}")
        try:
            return json.loads(playlists_raw)
        except json.JSONDecodeError:
            logging.error("Invalid JSON format for TIDAL_PLAYLISTS in .env")
            return {}

    @classmethod
    def initialize_directories(cls):
        directories = [
            os.path.dirname(cls.SESSION_FILE),
            os.path.dirname(cls.HISTORY_FILE),
            cls.LOCAL_MUSIC_DIR,
            cls.PROCESSED_MUSIC_DIR,
            os.path.dirname(cls.OUTPUT_MIX_PATH),
        ]

        for directory in directories:
            if directory:
                os.makedirs(directory, exist_ok=True)
