import logging
import os
import shutil

from config import Config
from downloader import TidalDownloader
from history import HistoryManager
from mixer import AudioMixer
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
            logging.error(
                f"Failed to clean directory {Config.PROCESSED_MUSIC_DIR}: {e}"
            )


def main():
    logging.info("--- LofiGen Initialization ---")

    Config.initialize_directories()

    playlists = Config.get_playlists()
    if not playlists:
        logging.error("No playlists configured. Exiting.")
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
            uploader = SFTPUploader()
            uploader.upload(Config.OUTPUT_MIX_PATH)

        cleanup_processed_directory()
        logging.info("--- Execution Finished ---")

    else:
        logging.error("Could not authenticate with Tidal. Exiting.")


if __name__ == "__main__":
    main()
