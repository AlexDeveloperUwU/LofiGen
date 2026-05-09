import logging
import os

from mutagen.id3 import APIC, ID3, ID3NoHeaderError, TPE1, TIT2

from config import Config


def apply_tags(mp3_path: str) -> None:
    try:
        try:
            tags = ID3(mp3_path)
        except ID3NoHeaderError:
            tags = ID3()

        tags["TIT2"] = TIT2(encoding=3, text="Nightly LoFi Mix")
        tags["TPE1"] = TPE1(encoding=3, text="LofiGen")

        cover_path = Config.COVER_ART_PATH
        if os.path.exists(cover_path):
            with open(cover_path, "rb") as f:
                tags["APIC"] = APIC(encoding=3, mime="image/jpeg", type=3, desc="Cover", data=f.read())
            logging.info(f"Cover art embedded from: {cover_path}")
        else:
            logging.warning(f"Cover art not found at {cover_path}, skipping.")

        tags.save(mp3_path, v2_version=3)
        logging.info(f"ID3 tags applied to: {mp3_path}")
    except Exception as e:
        logging.error(f"Failed to apply ID3 tags: {e}")
