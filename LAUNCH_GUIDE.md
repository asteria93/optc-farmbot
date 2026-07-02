# OPTC Farming Bot — Launch Guide

A complete guide to setting up and running the OPTC Farming Bot web interface.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Database Setup](#2-database-setup)
3. [Configuration](#3-configuration)
4. [Launch Instructions](#4-launch-instructions)
5. [Usage Guide](#5-usage-guide)
6. [Troubleshooting](#6-troubleshooting)
7. [File Structure](#7-file-structure)

---

## 1. Prerequisites

### Python 3.8+

**Linux / Mac:**
```bash
# Check your version
python3 --version

# Ubuntu/Debian install
sudo apt update && sudo apt install -y python3 python3-pip python3-venv

# macOS (Homebrew)
brew install python
```

**Windows:**
1. Download Python 3.8+ from https://www.python.org/downloads/
2. During installation check **"Add Python to PATH"**
3. Verify: open Command Prompt → `python --version`

### Redis

Redis is required for the Celery task queue.

**Linux:**
```bash
sudo apt install -y redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**Mac (Homebrew):**
```bash
brew install redis
brew services start redis
```

**Windows:**
- **Recommended:** Install via WSL2 (Windows Subsystem for Linux) and follow the Linux steps above.
- **Alternative:** Download Redis Stack for Windows from https://redis.io/downloads/
- **Docker:** `docker run -d -p 6379:6379 redis:alpine`

### DLL Files (Windows only)

Some encryption features used by the bot require the Microsoft Visual C++ Redistributable:
1. Download from https://aka.ms/vs/17/release/vc_redist.x64.exe
2. Install and reboot if prompted.

---

## 2. Database Setup

The bot uses **SQLite** by default (no extra installation needed). The database file is created automatically on first launch.

### Automatic (recommended)

The database is created when you run `python app.py` or execute the setup scripts. No manual steps required.

### Manual initialization

```bash
# From the project root
python scripts/init_db.py
```

This creates `optc_farmbot.db` (SQLite) and sets up all required tables.

---

## 3. Configuration

### Copy the example environment file

```bash
# Linux / Mac
cp .env.example .env

# Windows
copy .env.example .env
```

### Edit `.env` with your settings

Open `.env` in any text editor. Key values to change:

| Variable | Description | Example |
|---|---|---|
| `SECRET_KEY` | Flask secret key — **change this!** | `my-super-secret-key-abc123` |
| `SQLALCHEMY_DATABASE_URI` | Database path | `sqlite:///optc_farmbot.db` |
| `REDIS_URL` | Redis connection | `redis://localhost:6379/0` |
| `HOST` | Web server host | `0.0.0.0` |
| `PORT` | Web server port | `5000` |
| `LOG_LEVEL` | Logging verbosity | `INFO` |

### Bot farming priorities

```dotenv
# Set to True/False to enable or disable each farming mode
PRIORITY_EVENTS=True
PRIORITY_STORY=True
PRIORITY_MISSIONS=True
PRIORITY_GRINDING=False
```

### Bot/game region

The region (JP/GB) and platform (iOS/Android) are configured per-account through the web dashboard after launch.

---

## 4. Launch Instructions

### Quick Start (recommended)

**Linux / Mac:**
```bash
chmod +x setup.sh start.sh
./setup.sh      # First time only — installs dependencies
./start.sh      # Start everything
```

**Windows:**
```bat
setup.bat       :: First time only — installs dependencies
start.bat       :: Start everything
```

---

### Manual Launch (step by step)

#### Step 1 — Create and activate a virtual environment

```bash
# Linux / Mac
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

#### Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

#### Step 3 — Set up the environment

```bash
cp .env.example .env   # then edit .env as described above
```

#### Step 4 — Initialize the database

```bash
python scripts/init_db.py
```

#### Step 5 — Start Redis

```bash
# Linux (if not already running as a service)
redis-server

# Mac
brew services start redis

# Windows — run redis-server.exe from the Redis install directory
```

#### Step 6 — Start the Celery worker (new terminal / tab)

```bash
# Linux / Mac
source venv/bin/activate
celery -A app.celery worker --loglevel=info

# Windows
venv\Scripts\activate
celery -A app.celery worker --loglevel=info --pool=solo
```

> **Windows note:** Celery on Windows requires `--pool=solo` or `--pool=gevent`.

#### Step 7 — Start the Flask web server (new terminal / tab)

```bash
# Linux / Mac
source venv/bin/activate
python app.py

# Windows
venv\Scripts\activate
python app.py
```

#### Step 8 — Open the dashboard

Visit **http://localhost:5000** in your browser.

---

## 5. Usage Guide

### Creating your first account

1. Open http://localhost:5000
2. Click **"Add Account"** (or navigate to `/accounts/new`)
3. Fill in:
   - **Username** — any label you want
   - **Email** — the OPTC account email
   - **Password** — the OPTC account password
   - **Device ID** *(optional)* — leave blank to auto-generate
4. Click **Save**. The account appears in the dashboard.

### Starting farming

1. From the dashboard, locate the account you want to farm.
2. Click **"Start Farming"**.
3. Choose the farming mode:
   - **All** — story + events + missions in priority order
   - **Story** — story chapters only
   - **Events** — active events only
   - **Missions** — daily/weekly missions only
   - **Grinding** — repeatable grind stages
4. Choose a strategy:
   - **Aggressive** — faster runs, 30-min breaks
   - **Moderate** — balanced, 1-hour breaks *(recommended)*
   - **Conservative** — slower, 90-min breaks
5. Click **Start**. The farming job is queued in Celery.

### Monitoring progress

- The **Dashboard** (`/`) shows all accounts and their live status.
- The **Logs** tab (`/logs`) shows per-account farming history.
- Each account card displays: current mode, total runs, berries/gold/exp earned.

### Stopping / restarting

- Click **"Stop Farming"** on the account card to cancel the active Celery task.
- To restart, click **"Start Farming"** again.
- To stop all services, press `Ctrl+C` in each terminal (or run `./stop.sh` if you used the start scripts).

---

## 6. Troubleshooting

### Redis connection refused

```
redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379
```

Redis is not running. Start it:
```bash
# Linux
sudo systemctl start redis
# Mac
brew services start redis
# Windows — start redis-server.exe
```

### Celery task not starting

Make sure:
1. Redis is running (see above).
2. The Celery worker process is running in a separate terminal.
3. `REDIS_URL` in `.env` matches the running Redis instance.

On Windows, add `--pool=solo`:
```bat
celery -A app.celery worker --loglevel=info --pool=solo
```

### Database errors / missing tables

Run the initialization script:
```bash
python scripts/init_db.py
```

Or delete `optc_farmbot.db` and restart `app.py` — tables are recreated automatically.

### Flask won't start / port already in use

Change the port in `.env`:
```dotenv
PORT=5001
```

Or kill the process using port 5000:
```bash
# Linux / Mac
lsof -ti:5000 | xargs kill -9

# Windows (Command Prompt)
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Farming stuck / no progress

1. Check the **Logs** tab in the dashboard.
2. Check the Celery worker terminal for error output.
3. Verify account credentials are correct.

### Log locations

| Log | Location |
|---|---|
| Flask web server | Terminal running `python app.py` |
| Celery worker | Terminal running `celery worker` |
| Application log file | `logs/optc_farmbot.log` (configured in `.env`) |
| Database | `optc_farmbot.db` (SQLite file, root of project) |

### Checking bot status via API

```bash
# All accounts
curl http://localhost:5000/api/accounts

# Specific account farming status
curl http://localhost:5000/api/accounts/<id>/status

# All active farming sessions
curl http://localhost:5000/api/farming/sessions
```

---

## 7. File Structure

```
optc-farmbot/
├── app.py                  # Flask application entry point — run this to start the web server
├── models.py               # SQLAlchemy database models (Account, FarmSession, Log)
├── requirements.txt        # Python dependencies — pip install -r requirements.txt
├── .env.example            # Template for environment variables — copy to .env
├── .env                    # Your local configuration (not committed to git)
│
├── api/
│   └── routes.py           # REST API endpoints (/api/accounts, /api/farming, etc.)
│
├── web/
│   ├── routes.py           # Web dashboard page routes
│   ├── templates/          # Jinja2 HTML templates
│   └── static/             # CSS, JS, images
│
├── bot/
│   ├── __init__.py
│   ├── account_manager.py  # Account creation and management logic
│   ├── api_client.py       # HTTP client for OPTC game API calls
│   ├── cli.py              # Command-line interface (standalone use)
│   └── farmer.py           # Core farming logic (Farmer, FarmingScheduler classes)
│
├── config/
│   └── settings.py         # Loads .env and exposes settings as Python constants
│
├── scripts/
│   └── init_db.py          # Database initialization (SQLite + Redis check)
│
├── tests/
│   ├── test_app.py         # Flask app tests
│   └── test_bot.py         # Bot logic tests
│
├── logs/                   # Log files (created automatically)
│
├── setup.sh                # Linux/Mac automated setup script
├── setup.bat               # Windows automated setup script
├── start.sh                # Linux/Mac start-all-services script
└── start.bat               # Windows start-all-services script
```

### Where to configure settings

| What | Where |
|---|---|
| Server port, secret key, Redis URL | `.env` |
| Farming priorities (events/story/missions) | `.env` → `PRIORITY_*` variables |
| Farming strategies (aggressive/moderate/conservative) | `config/settings.py` → `FARMING_STRATEGIES` |
| Database path | `.env` → `SQLALCHEMY_DATABASE_URI` |
| Log file path & verbosity | `.env` → `LOG_FILE`, `LOG_LEVEL` |
| Per-account settings | Dashboard → account edit form |
