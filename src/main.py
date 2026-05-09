from config import Config
from downloader import TidalDownloader
from tidal_client import TidalClient


def main():
    print("--- LofiGen Initialization ---")

    Config.initialize_directories()

    playlists = Config.get_playlists()
    if not playlists:
        print("[Error] No playlists configured. Exiting.")
        return

    print(f"[Info] Loaded {len(playlists)} playlist(s) from config.")

    client = TidalClient()
    if client.authenticate():
        print(f"[Success] Logged in to Tidal as: {client.session.user.id}")

        downloader = TidalDownloader(client.session)
        downloader.download_playlists(playlists)

        print("\n[Success] Download phase completed!")
    else:
        print("[Error] Could not authenticate with Tidal. Exiting.")


if __name__ == "__main__":
    main()
