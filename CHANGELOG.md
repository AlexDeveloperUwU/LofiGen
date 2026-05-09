# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-05-09

### Added

**Core pipeline**
- Automated end-to-end pipeline: authenticate → download → mix → tag → upload
- Orchestrated via `src/main.py` with clean separation between stages

**Tidal integration**
- OAuth device-flow authentication via `tidalapi`
- Session persistence to `data/tidal_session.json` — no re-auth on subsequent runs
- Multi-playlist support via `TIDAL_PLAYLISTS` JSON config

**Smart download system**
- Parallel playlist downloads with 8 concurrent workers
- Local M4A cache with configurable size per playlist (`TIDAL_DOWNLOAD_MAX`)
- Cache rotation: evicts oldest 25% of tracks when the limit is reached, keeping mixes fresh
- 7-day rolling play history (`data/history.json`) prevents track repetition across runs

**Audio mixing**
- EBU R128 loudness normalization (−16 LUFS, −1.5 TP, 11 LRA) for consistent volume
- Dynamic fade in/out scaled to track length (up to 3 seconds)
- MP3 encoding at 96 kbps / 44.1 kHz via `libmp3lame`
- Parallel per-track processing with 4 workers
- Lossless concatenation via FFmpeg concat demuxer (`-c copy`)
- Target duration configurable via `DURATION_HOURS`

**ID3 metadata & cover art**
- Title ("Nightly LoFi Mix") and Artist ("LofiGen") tags embedded in the output MP3
- Custom cover image (JPEG) embedded as APIC front-cover frame (ID3v2.3)
- Cover path configurable via `COVER_ART_PATH`; skipped gracefully if not present

**Home Assistant upload**
- SFTP upload to a configurable remote path via Paramiko
- Automatic retry logic (3 attempts, 5-second delay) on connection or transfer failure

**Docker support**
- `Dockerfile` based on `ghcr.io/astral-sh/uv:python3.14-bookworm-slim` with FFmpeg and `tzdata`
- Non-root container user for safety
- `docker-compose.yml` with `./data` volume mount for full persistence across restarts
- Daemon mode enabled by default in Compose

**Built-in daemon mode**
- `--daemon` flag runs the pipeline immediately on start, then repeats daily at the configured time
- Schedule configurable via `DAEMON_RUN_AT` (default `03:00`)
- Full timezone support via `TZ` env var (e.g. `Europe/Madrid` handles CET/CEST automatically)
- Graceful shutdown on `SIGINT` / `SIGTERM`
