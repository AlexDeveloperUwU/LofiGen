# 🎵 LofiGen

[![Python Version](https://img.shields.io/badge/python-3.14%2B-blue)](https://www.python.org/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Status: Active](https://img.shields.io/badge/Status-Active-brightgreen)]()

> **Automated lofi music mix generator** that intelligently selects tracks from your Tidal playlists, processes them with audio normalization and professional fading, and uploads continuous mixes to your Home Assistant media server—all hands-free.

Generate fresh, ready-to-play lofi mixes on demand or on a schedule. Perfect for ambient background music, meditation, or creating a personal music library.

---

## 📋 Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Docker (Recommended)](#docker-recommended)
  - [Run Once](#run-once-no-docker)
  - [Daemon Mode](#daemon-mode-no-docker)
- [Examples & Use Cases](#examples--use-cases)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Technology Stack](#technology-stack)
- [Development](#development)
- [Performance Tips](#performance-tips)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)
- [License & Support](#license--support)

---

## ✨ Features

🎯 **Smart Track Selection**
- Intelligently chooses tracks from multiple Tidal playlists to fill your target mix duration
- Avoids repetition with a 7-day rolling play history
- Automatically rotates cache to keep mixes fresh

🔊 **Professional Audio Processing**
- EBU R128 loudness normalization (-16 LUFS) for consistent volume
- Dynamic fade in/out based on track length
- MP3 encoding at 96 kbps for quality audio at reasonable file sizes
- Parallel processing for faster mix generation

⬆️ **Seamless Cloud Upload**
- Automatic SFTP upload to Home Assistant media server
- Retry logic with configurable attempts and delays
- Validates connection before upload

🔄 **Fully Automated**
- Orchestrated workflow: authenticate → download → mix → upload
- Scheduled execution support (cron, Home Assistant automation)
- Session caching prevents repeated Tidal authentication

📊 **Transparent History Tracking**
- 7-day rolling window prevents song repetition
- Auto-cleanup of old history records
- Detailed logging for debugging

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.14+** with `uv` package manager
- **FFmpeg** (for audio processing)
- **Tidal Account** with access to desired playlists
- **Home Assistant** instance with SFTP enabled

### Installation (3 Steps)

```bash
# 1. Clone and enter the project
git clone https://github.com/AlexDeveloperUwU/LofiGen
cd LofiGen

# 2. Install dependencies with uv
uv sync

# 3. Configure environment
cp .env.example .env
# Edit .env with your Tidal and Home Assistant credentials
nano .env
```

### Run It

```bash
# First run (interactive, logs to console)
uv run python src/main.py

# Or use the installed script
python src/main.py
```

That's it! Your first mix is being generated and will upload to Home Assistant.

---

## 📥 Installation

### Step 1: Install FFmpeg

<details>
<summary><b>🪟 Windows</b></summary>

**Option A: Winget (Recommended)**
```powershell
winget install FFmpeg
```

**Option B: Chocolatey**
```powershell
choco install ffmpeg
```

**Option C: Manual Download**
- Download from [ffmpeg.org](https://ffmpeg.org/download.html)
- Extract to `C:\Program Files\ffmpeg`
- Add to PATH: `C:\Program Files\ffmpeg\bin`
- Verify: `ffmpeg -version`

</details>

<details>
<summary><b>🍎 macOS</b></summary>

**Homebrew (Recommended)**
```bash
brew install ffmpeg
```

**Verify:**
```bash
ffmpeg -version
```

</details>

<details>
<summary><b>🐧 Linux</b></summary>

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Fedora/RHEL:**
```bash
sudo dnf install ffmpeg
```

**Verify:**
```bash
ffmpeg -version
```

</details>

### Step 2: Install Python & Dependencies

```bash
# Install uv (modern Python package manager)
# Visit https://docs.astral.sh/uv/getting-started/installation/

# Clone the project
git clone https://github.com/AlexDeveloperUwU/LofiGen
cd LofiGen

# Sync dependencies (creates virtual environment)
uv sync
```

### Step 3: Set Up Tidal

You'll need to authenticate with Tidal. The app will guide you through:

1. Visit the link provided on first run
2. Scan the QR code or open the URL
3. Authorize LofiGen access
4. Session is saved locally (no need to re-auth)

### Step 4: Configure Home Assistant

Enable SFTP on your Home Assistant instance:

1. **Install SSH & Web Terminal Add-on** (if not already installed)
   - Settings → Add-ons → Add-on Store
   - Search "SSH & Web Terminal"
   - Install and start

2. **Note your credentials:**
   - Hostname: Your Home Assistant IP or hostname
   - Username: Usually `root`
   - Password: Your SSH password

3. **Identify media folder:**
   - Default: `/ha/media/`
   - Can be customized in config

### Step 5: Create & Edit `.env` File

```bash
cp .env.example .env
nano .env  # or your preferred editor
```

See [Configuration](#configuration) section for all variables.

---

## ⚙️ Configuration

All configuration is handled through a `.env` file in the project root. Create one using the template:

```bash
cp .env.example .env
```

### Configuration Variables

| Variable | Type | Required | Default | Description |
|----------|------|----------|---------|-------------|
| **TIDAL_PLAYLISTS** | JSON | ✅ | — | Playlist IDs mapping: `{"name": "ID", ...}` |
| **TIDAL_SESSION_FILE** | Path | ✅ | `./data/tidal_session.json` | Where to cache Tidal auth session |
| **TIDAL_DOWNLOAD_MAX** | Integer | ❌ | `2` | Max tracks to keep per playlist (cache size) |
| **LOCAL_MUSIC_DIR** | Path | ✅ | `./data/downloads` | Where to store downloaded tracks |
| **OUTPUT_MIX_PATH** | Path | ✅ | `./data/output/LoFi.mp3` | Where to save the final mix |
| **HISTORY_FILE** | Path | ✅ | `./data/history.json` | Where to track played songs |
| **HA_HOSTNAME** | String | ✅ | — | Home Assistant IP or hostname |
| **HA_USER** | String | ✅ | — | SSH username (usually `root`) |
| **HA_PASSWORD** | String | ✅ | — | SSH password |
| **HA_PATH** | Path | ✅ | `/ha/media/LoFi.mp3` | Remote destination path on HA |
| **DURATION_HOURS** | Float | ❌ | `4` | Target mix length in hours |
| **COVER_ART_PATH** | Path | ❌ | `./assets/cover.jpg` | Cover image embedded in the output MP3 |
| **DAEMON_RUN_AT** | Time | ❌ | `03:00` | Daily run time in `HH:MM` format (local time per `TZ`) |
| **TZ** | String | ❌ | `UTC` | Container timezone (e.g. `Europe/Madrid`) |
| **TIDAL_SEQUENTIAL** | Boolean | ❌ | `false` | Download tracks one at a time — prevents Tidal 429 rate limiting |

### Complete Example

```env
# === TIDAL Configuration ===
# Get playlist IDs from Tidal app or URL: https://listen.tidal.com/playlist/<ID>
TIDAL_PLAYLISTS={"chill_lofi": "12345abcde", "lo-fi_beats": "67890fghij"}
TIDAL_SESSION_FILE=./data/tidal_session.json
TIDAL_DOWNLOAD_MAX=2

# === Local Storage ===
LOCAL_MUSIC_DIR=./data/downloads
OUTPUT_MIX_PATH=./data/output/LoFi.mp3
HISTORY_FILE=./data/history.json

# === Home Assistant (SFTP) ===
HA_HOSTNAME=192.168.1.100          # or homecore.local
HA_USER=root
HA_PASSWORD=your_ssh_password
HA_PATH=/ha/media/LoFi.mp3

# === Mix Parameters ===
DURATION_HOURS=4                    # 4-hour mix (24 for daily)

# === Daemon / Docker ===
DAEMON_RUN_AT=20:30
TZ=Europe/Madrid
COVER_ART_PATH=./assets/cover.jpg
TIDAL_SEQUENTIAL=true               # Recommended: avoids Tidal rate limiting
```

### Finding Your Tidal Playlist IDs

1. **In Tidal App:**
   - Open a playlist
   - Click share → copy link
   - ID is the long string in the URL

2. **From Web:**
   - Visit https://listen.tidal.com/playlist/YOUR_ID
   - ID is in the URL

---

## 🎮 Usage

### Docker (Recommended)

The easiest way to run LofiGen permanently — no Python or FFmpeg setup needed on the host.

```bash
# 1. Clone the repo
git clone https://github.com/AlexDeveloperUwU/LofiGen
cd LofiGen

# 2. Add your cover art (optional)
cp your-cover.jpg assets/cover.jpg

# 3. Configure
cp .env.example .env
nano .env  # fill in Tidal playlists + Home Assistant credentials

# 4. Start (runs immediately, then every day at DAEMON_RUN_AT)
docker compose up -d
```

**First run:** Tidal will ask you to authorize via a link printed in the logs. Open it once:

```bash
docker compose logs -f
# → Visit https://tidal.com/activate?code=XXXX
# Authorize, then the pipeline starts automatically.
```

**Useful commands:**

```bash
docker compose logs -f          # Follow logs
docker compose restart          # Restart the container
docker compose down             # Stop
docker compose up -d --build    # Rebuild after code changes
```

All state (downloads, session, history, output) persists in `./data/` on your host.

---

### Run Once (no Docker)

```bash
uv run python src/main.py
```

### Daemon Mode (no Docker)

```bash
uv run python src/main.py --daemon
```

Runs the pipeline immediately, then repeats daily at the time set by `DAEMON_RUN_AT` in `.env`.

### Schedule with Cron

Generate a fresh mix every day at 6 AM:

```bash
# Edit crontab
crontab -e

# Add this line
0 6 * * * cd /path/to/LofiGen && uv run python src/main.py
```

### Schedule with Home Assistant

Create an automation in Home Assistant:

```yaml
automation:
  - alias: "Generate Fresh Lofi Mix Daily"
    trigger:
      platform: time
      at: "06:00:00"
    action:
      service: shell_command.generate_lofi_mix

shell_command:
  generate_lofi_mix: "ssh root@<HA_IP> 'cd /path/to/LofiGen && uv run python src/main.py'"
```

### Output Locations

After running, you'll have:

```
LofiGen/
├── data/
│   ├── downloads/           # Downloaded tracks (.m4a)
│   ├── output/
│   │   └── LoFi.mp3        # Final mix (uploaded to HA)
│   ├── tidal_session.json   # Cached auth session
│   └── history.json         # Play history (last 7 days)
└── logs/                    # Execution logs (if configured)
```

---

## 📚 Examples & Use Cases

### Example 1: Daily Fresh Lofi Mix (4 Hours)

```env
TIDAL_PLAYLISTS={"lofi_hip_hop": "5926949641", "lofi_girl": "3819640372"}
DURATION_HOURS=4
TIDAL_DOWNLOAD_MAX=3
```

**Result:** Fresh 4-hour mix daily, pulling from 2 playlists, rotating tracks.

---

### Example 2: Extended Ambient Mix (24 Hours)

```env
TIDAL_PLAYLISTS={
  "lofi_hip_hop": "5926949641",
  "ambient_lofi": "6789013456", 
  "sleep_lofi": "2468135790"
}
DURATION_HOURS=24
TIDAL_DOWNLOAD_MAX=5
```

**Result:** Full day of continuous background music, less frequent repeats.

---

### Example 3: Cron Schedule

```bash
# Generate 3-hour mix every 12 hours
0 0,12 * * * cd ~/LofiGen && DURATION_HOURS=3 uv run python src/main.py

# Weekly refresh (Sunday 10 AM)
0 10 * * 0 cd ~/LofiGen && uv run python src/main.py
```

---

## 🏗️ How It Works

### Workflow Overview

```
┌─────────────────────────────────────────────────────┐
│ 1. AUTHENTICATE                                     │
│    → Tidal OAuth (cached if possible)              │
└─────────────┬───────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────┐
│ 2. DOWNLOAD TRACKS                                  │
│    → Fetch from Tidal playlists                    │
│    → Sequential (recommended) or parallel (2x)    │
│    → Skip already cached tracks                    │
│    → Rotate cache (keep fresh)                     │
│    → Filter by 7-day play history                  │
└─────────────┬───────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────┐
│ 3. GENERATE MIX                                     │
│    → Select random tracks to fill duration         │
│    → Process each (normalize, fade, encode)        │
│    → Concatenate with FFmpeg                       │
│    → Mark as played in history                     │
└─────────────┬───────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────┐
│ 4. UPLOAD TO HOME ASSISTANT                        │
│    → SFTP to configured HA path                    │
│    → Retry on failure (3 attempts default)         │
│    → Verify upload success                        │
└─────────────┬───────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────┐
│ 5. CLEANUP                                          │
│    → Remove temporary processed files              │
│    → Update history with new songs                 │
└─────────────────────────────────────────────────────┘
```

### Component Details

#### 🔐 Tidal Authentication (`tidal_client.py`)
- **Method:** OAuth with device flow
- **Session Caching:** Saves to `TIDAL_SESSION_FILE` to avoid repeated auth
- **Library:** `tidalapi` for API communication
- **Flow:** On first run, user authorizes via web link; credentials cached for future runs

#### 📥 Smart Download System (`downloader.py`)
- **Sequential mode** (`TIDAL_SEQUENTIAL=true`, recommended): one download at a time with a random 0.5–1.5s gap — reliably avoids Tidal rate limiting
- **Parallel mode** (`TIDAL_SEQUENTIAL=false`): 2 concurrent workers for faster downloads when rate limiting isn't a concern
- **Rate limit handling:** `TooManyRequests` is caught specifically with 10s/20s/40s backoff; other transient errors retry with 5s/10s/20s backoff; HTTP-level errors use `requests.adapters.Retry` with exponential backoff
- **Track Deduplication:** Checks local cache before downloading
- **Cache Rotation:** When cache reaches `TIDAL_DOWNLOAD_MAX` per playlist, removes oldest 25% of tracks
- **History Filtering:** Skips any tracks played in past 7 days
- **Quality:** Downloads at 96 kbps (low bandwidth, good quality)

#### 📊 Play History Management (`history.py`)
- **Window:** 7-day rolling history
- **Auto-Cleanup:** Removes entries older than 7 days
- **Storage:** JSON file for human readability and debugging
- **Purpose:** Prevents song repetition in consecutive mixes

#### 🎵 Audio Mixing (`mixer.py`)
- **Selection:** Randomly picks tracks to fill target duration
- **Smart Fit:** Chooses best combination to reach duration without overshoot
- **Parallel Processing:** 4 concurrent workers for audio encoding
- **Per-Track Processing:**
  - Normalization (EBU R128, -16 LUFS)
  - Fade in/out (dynamic, 3-10 seconds)
  - MP3 encoding (96 kbps, 44.1 kHz)
- **Concatenation:** FFmpeg concat demuxer for seamless merging

#### ⬆️ Upload System (`uploader.py`)
- **Protocol:** SFTP via Paramiko
- **Retry Logic:** 3 attempts by default, 5-second delay between retries
- **Destination:** Configurable path on HA (e.g., `/ha/media/LoFi.mp3`)
- **Validation:** Checks file exists after upload

#### 🎼 Orchestration (`main.py`)
- Initializes all directories
- Coordinates pipeline: auth → download → mix → upload
- Cleanup of temporary files
- Error handling and logging

---

## 📁 Project Structure

```
LofiGen/
│
├── src/                          # Main source code
│   ├── __init__.py              # Package init
│   ├── main.py                  # Entry point, orchestrates workflow
│   ├── config.py                # Loads .env configuration
│   ├── tidal_client.py          # Tidal API authentication
│   ├── downloader.py            # Downloads from Tidal playlists
│   ├── history.py               # Manages 7-day play history
│   ├── mixer.py                 # Audio processing & mixing with FFmpeg
│   └── uploader.py              # SFTP uploader to Home Assistant
│
├── data/                        # Runtime data (git-ignored)
│   ├── downloads/               # Downloaded M4A files from Tidal
│   ├── output/                  # Final MP3 mixes
│   ├── tidal_session.json       # Cached auth session
│   └── history.json             # Play history tracking
│
├── assets/
│   └── cover.jpg                # Cover art embedded in the output MP3
│                                # Source: https://cdn-images.dzcdn.net/images/cover/f5bdcb7e132d256f675a15013b8df9ef/0x1900-000000-80-0-0.jpg
├── .env                         # Configuration (sensitive, git-ignored)
├── .env.example                 # Configuration template
├── pyproject.toml               # Dependencies and project metadata
├── uv.lock                      # Locked dependency versions
├── README.md                    # This file
├── LICENSE                      # GPL v3 license
└── .gitignore                   # Git ignore rules
```

### Module Purposes

| Module | Purpose | Key Classes/Functions |
|--------|---------|----------------------|
| `main.py` | Orchestrates full workflow | `main()` |
| `config.py` | Loads environment variables | `load_config()` |
| `tidal_client.py` | Tidal OAuth & API access | `TidalClient` |
| `downloader.py` | Playlist downloads | `Downloader` |
| `history.py` | Play history tracking | `PlayHistory` |
| `mixer.py` | Audio processing & mixing | `Mixer` |
| `uploader.py` | SFTP upload to HA | `Uploader` |

---

## 🛠️ Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Language** | Python | 3.14+ | Core runtime |
| **Package Manager** | uv | Latest | Dependency management |
| **Tidal Integration** | tidalapi | 0.8.11+ | Tidal API client |
| **Audio Processing** | FFmpeg | Latest | Audio encoding & mixing |
| **Audio Library** | pydub | 0.25.1+ | Audio analysis |
| **SSH/SFTP** | Paramiko | 4.0.0+ | Secure file transfer |
| **Configuration** | python-dotenv | 1.2.2+ | .env file parsing |

---

## 👨‍💻 Development

### Set Up Dev Environment

```bash
# Clone repo
git clone <repository-url>
cd LofiGen

# Install dev dependencies
uv sync

# Enter virtual environment (if needed)
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

### Project Structure for Developers

Each module is independent and testable:

- **Separation of concerns:** Each component handles one responsibility
- **Configuration abstraction:** `config.py` centralizes all env vars
- **Parallel processing:** Downloads and audio processing use `ThreadPoolExecutor`
- **Error handling:** Graceful degradation; tracks can be skipped if processing fails

### Key Design Patterns

1. **History-based Deduplication**
   - 7-day rolling window prevents repetition
   - Auto-cleanup keeps storage minimal

2. **Smart Cache Rotation**
   - Keeps mixes fresh without constant re-downloading
   - Balances API calls with variety

3. **Parallel Processing**
   - 8 concurrent downloads
   - 4 concurrent audio encoders
   - Significant speed improvement for large mixes

4. **Modular Architecture**
   - Each component (`tidal`, `download`, `mix`, `upload`) is independently testable
   - Easy to extend or replace individual modules

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make changes and test locally
4. Commit with clear messages
5. Push to your fork
6. Open a Pull Request

---

## ⚡ Performance Tips

### Optimizing Downloads

**Tune Parallel Workers:**
```python
# In downloader.py, modify MAX_WORKERS
MAX_WORKERS = 12  # Default is 8, increase for faster downloads
```

**Increase Cache Size:**
```env
TIDAL_DOWNLOAD_MAX=5  # Keep more tracks, fewer downloads needed
```

**Tip:** Higher cache = less frequent Tidal API calls, but more local storage.

---

### Optimizing Audio Processing

**Reduce Mix Quality (saves time):**
```python
# In mixer.py, modify bitrate
BITRATE = "64k"  # Default is 96k; 64k still sounds good, faster to encode
```

**Increase Processing Workers:**
```python
# In mixer.py, modify MAX_WORKERS
MAX_WORKERS = 8  # Default is 4; use your CPU core count
```

**Tip:** More workers speed up processing but use more CPU/RAM.

---

### Network Optimization

**SFTP Connection Issues:**
- Use IP address instead of hostname if possible (faster)
- Ensure stable network connection before running
- Consider running on the same network as Home Assistant

**Large File Uploads:**
```bash
# SSH into HA and run locally (avoids network transfer)
# Copy generated file to HA media folder directly
scp ./data/output/LoFi.mp3 root@192.168.1.100:/ha/media/
```

---

### Hardware Considerations

| Hardware | Impact | Recommendation |
|----------|--------|-----------------|
| **CPU Cores** | Audio encoding speed | More cores = faster processing |
| **RAM** | Parallel downloads/encoding | 2GB minimum, 4GB+ recommended |
| **Disk Speed** | Cache rotation & mixing | SSD > HDD; NAS slower |
| **Network** | Upload time | Gigabit > 100Mbps |

**For Raspberry Pi:**
- Use lower bitrate (64k)
- Reduce parallel workers (2-4)
- Limit mix duration (2-3 hours)

---

## 🔧 Troubleshooting

### Tidal Authentication Fails

**Problem:** "OAuth failed" or "Session expired"

**Solutions:**
1. Delete the cached session file:
   ```bash
   rm data/tidal_session.json
   ```
2. Re-run the app and complete OAuth authorization
3. Ensure you have internet connection during auth
4. Check Tidal account status (active subscription required)

---

### FFmpeg Not Found

**Problem:** "FFmpeg: command not found"

**Solutions:**
1. Verify FFmpeg installation:
   ```bash
   ffmpeg -version
   ```
2. Add to PATH (if manually installed)
   - Windows: Add installation folder to System PATH
   - macOS/Linux: `which ffmpeg` should show path
3. Reinstall FFmpeg (see [Installation](#installation))

---

### SFTP Connection Fails

**Problem:** "Connection refused" or "Authentication failed"

**Solutions:**
1. Verify Home Assistant is running and accessible:
   ```bash
   ping <HA_HOSTNAME>
   ```
2. Check SSH credentials:
   - Hostname: IP or hostname of HA
   - User: Usually `root` (verify in HA SSH addon)
   - Password: Your configured password
3. Ensure SSH addon is enabled in Home Assistant
4. Check firewall rules (port 22 by default)
5. Test SSH directly:
   ```bash
   ssh root@<HA_IP>
   ```

---

### Audio Processing Errors

**Problem:** "Invalid audio format" or processing hangs

**Solutions:**
1. Ensure FFmpeg is properly installed
2. Check disk space (needs room for temp files):
   ```bash
   df -h  # Check available space
   ```
3. Try reducing parallel workers (increase processing time but less resource contention)
4. Check file permissions in `LOCAL_MUSIC_DIR`

---

### Disk Space Issues

**Problem:** "No space left on device"

**Solutions:**
1. Check available space:
   ```bash
   df -h
   ```
2. Clear old mixes:
   ```bash
   rm data/output/*.mp3
   ```
3. Reduce cache size:
   ```env
   TIDAL_DOWNLOAD_MAX=1  # Keep only latest track per playlist
   ```
4. Clean up downloaded files:
   ```bash
   rm data/downloads/*.m4a
   # App will re-download as needed
   ```

---

## ❓ FAQ

### How often should I run this?

**Daily is ideal.** The 7-day history prevents repetition, so daily runs give you fresh mixes with good variety. You can run every 12 hours for maximum freshness.

---

### Can I use it without Home Assistant?

**Yes!** Skip the upload step by not configuring `HA_HOSTNAME` etc. The mix is created in `OUTPUT_MIX_PATH` and you can access it manually.

---

### How much disk space do I need?

**Typical usage:** 500 MB to 2 GB
- Downloaded tracks: 50-100 MB (cached)
- Output mixes: 100-200 MB (keeps 1-2 recent)
- History: <1 MB

**Recommendation:** 5 GB free space for comfortable operation.

---

### Can I customize the fade length?

**Yes!** Edit `mixer.py`:
```python
# In mixer.py, find fade_duration calculation
fade_duration = max(3, min(10, duration / 20))  # Adjust these values
```

---

### Why are my mixes repetitive?

**Possible causes:**
1. **Too few playlists** → Add more Tidal playlists to config
2. **Cache too small** → Increase `TIDAL_DOWNLOAD_MAX` 
3. **Running too frequently** → The 7-day history can't help if you run multiple times daily
4. **Playlists are small** → Use larger playlists with more tracks

---

### How do I prevent certain songs?

**Current:** Edit `history.json` to add songs you want to skip:
```json
{
  "song_title": "2024-01-01T00:00:00"  // Add entry with recent date
}
```

**Future:** Could add a blocklist feature (contributions welcome!)

---

### Can I use with other music services (Spotify, Apple Music)?

**Currently:** Tidal only (tidalapi library)

**To add others:** Would need to:
1. Replace Tidal API with Spotify API (`spotipy` library)
2. Update `tidal_client.py` to use new service
3. Adjust authentication flow

**Contributions welcome!**

---

### What if the upload fails?

**Automatic:** Built-in retry logic (3 attempts, 5-second delay)

**Manual fallback:**
```bash
# Copy mix directly to HA
scp ./data/output/LoFi.mp3 root@<HA_IP>:/ha/media/
```

---

## 📄 License & Support

### License: GNU General Public License v3

This project is licensed under the **GPL v3**, which means:

✅ **You can:**
- Use it for personal purposes
- Modify the code for your own use
- Share it with others under the same license
- Learn from and study the code

❌ **You cannot:**
- Use it commercially (sell, include in products, etc.)
- Distribute modified versions without open-sourcing them
- Relicense under different terms

**For details, see the [LICENSE](./LICENSE) file.**

---

### Getting Help

**Found a bug?**
- Check [Troubleshooting](#troubleshooting) section
- Review console logs and error messages
- Open an issue with:
  - Error message (full stack trace)
  - Your configuration (without passwords!)
  - Steps to reproduce

**Have a feature idea?**
- Open a discussion or issue
- Describe your use case
- Contributions welcome!

**Questions?**
- Check the [FAQ](#faq) section
- Review [Examples](#examples--use-cases)
- Read the relevant module code (well-commented)

---

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a PR with description

---

**Made with ❤️ for ambient music lovers**
