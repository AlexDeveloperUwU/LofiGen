import json
import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    HA_HOSTNAME: str = os.getenv("HA_HOSTNAME", "homecore")
    HA_USER: str = os.getenv("HA_USER", "root")
    HA_PATH: str = os.getenv("HA_PATH", "/ha/media/LoFi.m4a")

    SESSION_FILE: str = os.getenv("TIDAL_SESSION_FILE", "./data/tidal_session.json")

    LOCAL_MUSIC_DIR: str = os.getenv("LOCAL_MUSIC_DIR", "./data/downloads")
    OUTPUT_MIX_PATH: str = os.getenv("OUTPUT_MIX_PATH", "./data/output/LoFi.m4a")

    DOWNLOAD_MAX: int = int(os.getenv("TIDAL_DOWNLOAD_MAX", "50"))

    @staticmethod
    def get_playlists() -> dict:
        playlists_raw = os.getenv("TIDAL_PLAYLISTS", "{}")
        try:
            return json.loads(playlists_raw)
        except json.JSONDecodeError:
            print("[Error] Invalid JSON format for TIDAL_PLAYLISTS in .env")
            return {}

    @classmethod
    def initialize_directories(cls):
        directories = [
            os.path.dirname(cls.SESSION_FILE),
            cls.LOCAL_MUSIC_DIR,
            os.path.dirname(cls.OUTPUT_MIX_PATH),
        ]

        for directory in directories:
            if directory:
                os.makedirs(directory, exist_ok=True)
