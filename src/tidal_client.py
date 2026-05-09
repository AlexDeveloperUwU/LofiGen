import json
import os
from datetime import datetime

import tidalapi

from config import Config


class TidalClient:
    def __init__(self):
        self.session = tidalapi.Session()

    def authenticate(self) -> bool:
        if os.path.exists(Config.SESSION_FILE):
            print("[Info] Loading saved Tidal session...")
            if self._load_saved_session():
                return True
            print("[Warning] Saved session invalid or expired. Re-authenticating...")

        return self._authenticate_new_session()

    def _load_saved_session(self) -> bool:
        try:
            with open(Config.SESSION_FILE, "r") as f:
                data = json.load(f)

            expiry_time = data.get("expiry_time")
            if expiry_time:
                expiry_time = datetime.fromisoformat(expiry_time)

            self.session.load_oauth_session(
                data["token_type"],
                data["access_token"],
                data.get("refresh_token"),
                expiry_time,
            )
            return self.session.check_login()
        except Exception as e:
            print(f"[Error] Failed to load saved session: {e}")
            return False

    def _authenticate_new_session(self) -> bool:
        print("[Info] Starting new Tidal authentication...")
        self.session.login_oauth_simple()

        if self.session.check_login():
            print("[Success] Login successful! Saving session...")

            expiry = getattr(self.session, "expiry_time", None)

            data = {
                "token_type": self.session.token_type,
                "access_token": self.session.access_token,
                "refresh_token": self.session.refresh_token,
                "expiry_time": expiry.isoformat() if expiry else None,
            }
            with open(Config.SESSION_FILE, "w") as f:
                json.dump(data, f)
            return True

        return False
