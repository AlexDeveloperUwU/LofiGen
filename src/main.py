import argparse
import logging
import os
import shutil
import signal
import sys
import time

import schedule

from config import Config
from downloader import TidalDownloader
from history import HistoryManager
from mixer import AudioMixer
from tagger import apply_tags
from tidal_client import TidalClient
from uploader import SFTPUploader


def cleanup_processed_directory():
    logging.info("Cleaning up temporary processing files...")
    if os.path.exists(Config.PROCESSED_MUSIC_DIR):
        try:
            shutil.rmtree(Config.PROCESSED_MUSIC_DIR)
            os.makedirs(Config.PROCESSED_MUSIC_DIR, exist_ok=True)
            logging.info("Successfully purged processing cache.")
        except Exception as e:
            logging.error(f"Failed to clean directory {Config.PROCESSED_MUSIC_DIR}: {e}")


def run_pipeline():
    logging.info("--- LofiGen Pipeline Start ---")
    Config.initialize_directories()

    playlists = Config.get_playlists()
    if not playlists:
        logging.error("No playlists configured.")
        return

    logging.info(f"Loaded {len(playlists)} playlist(s) from config.")

    client = TidalClient()
    if client.authenticate():
        logging.info(f"Logged in to Tidal as: {client.session.user.id}")

        history_manager = HistoryManager()
        downloader = TidalDownloader(client.session, history_manager)
        downloader.download_playlists(playlists)

        mixer = AudioMixer(history_manager)
        mixer.generate_mix()

        if os.path.exists(Config.OUTPUT_MIX_PATH):
            apply_tags(Config.OUTPUT_MIX_PATH)
            uploader = SFTPUploader()
            uploader.upload(Config.OUTPUT_MIX_PATH)

        cleanup_processed_directory()
        logging.info("--- Pipeline Finished ---")
    else:
        logging.error("Could not authenticate with Tidal.")


def _handle_signal(signum, frame):
    logging.info(f"Received signal {signum}. Shutting down.")
    sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="LofiGen — LoFi mix generator")
    parser.add_argument("--daemon", action="store_true", help="Run continuously, regenerating mix daily.")
    args = parser.parse_args()

    if args.daemon:
        signal.signal(signal.SIGINT, _handle_signal)
        signal.signal(signal.SIGTERM, _handle_signal)

        run_at = Config.DAEMON_RUN_AT
        logging.info(f"Daemon mode active. Running now, then daily at {run_at}.")

        run_pipeline()
        schedule.every().day.at(run_at).do(run_pipeline)

        while True:
            schedule.run_pending()
            time.sleep(30)
    else:
        run_pipeline()


if __name__ == "__main__":
    main()
