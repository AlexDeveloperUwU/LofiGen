import logging
import time

import paramiko

from config import Config


class SFTPUploader:
    def __init__(self, max_retries: int = 3, retry_delay: int = 5):
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def upload(self, local_path: str):
        remote_path = Config.HA_PATH
        host = Config.HA_HOSTNAME
        user = Config.HA_USER
        password = Config.HA_PASSWORD

        for attempt in range(1, self.max_retries + 1):
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                logging.info(
                    f"Uploading {local_path} to {host}:{remote_path} (Attempt {attempt}/{self.max_retries})"
                )
                ssh.connect(hostname=host, username=user, password=password)

                sftp = ssh.open_sftp()
                sftp.put(local_path, remote_path)
                sftp.close()

                logging.info("Upload successful.")
                return True

            except Exception as e:
                logging.warning(f"Upload failed: {e}")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
            finally:
                ssh.close()

        logging.error("Upload failed after all retries.")
        return False
