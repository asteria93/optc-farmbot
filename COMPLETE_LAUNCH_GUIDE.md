# COMPLETE LAUNCH GUIDE

This guide explains how to get the current `asteria93/optc-farmbot` repository running from scratch.

> Repository root used in this guide's environment: `/home/runner/work/optc-farmbot/optc-farmbot`
>
> Shorthand used below: `<repo-root>`
>
> If you cloned the project somewhere else, replace `<repo-root>` with your own clone path.

---

## Read this first: current repository status

This repository is **partially implemented**.

What works today:
- Installing the Python dependencies from `requirements.txt`
- Initializing storage with `<repo-root>/scripts/init_db.py`
- Starting the Flask app with `<repo-root>/app.py`
- Opening the landing page at `http://localhost:5000/`
- Using the JSON API under `http://localhost:5000/api/...`
- Using the CLI in `<repo-root>/bot/cli.py`

What is **not fully wired in the current snapshot**:
- No `celery_app.py` file exists, so `celery -A celery_app worker --loglevel=info` will fail unless you add Celery configuration yourself.
- Only one HTML template exists: `<repo-root>/web/templates/index.html`.
  Routes such as `/dashboard`, `/accounts`, `/farming`, `/settings`, and `/logs` currently point to missing templates and will error until those files are created.
- Account creation and farming are currently demo/in-memory flows in `<repo-root>/api/routes.py`; they are not persistent background game automation yet.
- No migration framework is configured. The app uses `db.create_all()` and the helper script instead of Alembic/Flask-Migrate.
- No `src/bisque/`, DLL loader, or `sakura.db` integration exists in this repository snapshot.

Because of that, this guide is split into:
1. **What you can launch right now**
2. **Optional components that are listed in the repo but not yet fully connected**

---

# PART 1: INSTALLATION & SETUP

## Step 1: Install Python

### Required version
- Recommended: **Python 3.11**
- Minimum for this guide: **Python 3.9+**

### Download
Download Python from:
- https://www.python.org/downloads/

### Windows
1. Download the latest Python 3.11 installer.
2. Run the installer.
3. **Check `Add Python to PATH`** before clicking Install.
4. Finish the installation.

### macOS
Options:
- Use the official installer from python.org, or
- Use Homebrew:

```bash
brew install python@3.11
```

### Linux
Most distributions already include Python, but install a modern version if needed.

Ubuntu/Debian:
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
```

Fedora:
```bash
sudo dnf install -y python3 python3-virtualenv python3-pip
```

Arch:
```bash
sudo pacman -S python python-pip
```

### Verify installation
Windows:
```bash
py --version
```

macOS/Linux:
```bash
python3 --version
```

Expected result:
```text
Python 3.11.x
```

---

## Step 2: Clone the repository and install dependencies

### Clone
```bash
git clone https://github.com/asteria93/optc-farmbot.git
cd optc-farmbot
```

### Create a virtual environment

Windows:
```bash
py -3.11 -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Upgrade pip
Windows:
```bash
python -m pip install --upgrade pip
```

macOS/Linux:
```bash
python3 -m pip install --upgrade pip
```

### Install required packages
The repository pins these versions in `<repo-root>/requirements.txt`:

- Flask==2.3.3
- Flask-CORS==4.0.0
- Flask-SQLAlchemy==3.0.5
- SQLAlchemy==2.0.21
- pymongo==4.5.0
- motor==3.3.1
- redis==5.0.0
- celery==5.3.1
- requests==2.31.0
- python-dotenv==1.0.0
- aiohttp==3.8.6
- selenium==4.13.0
- playwright==1.39.0
- pillow==10.1.0
- opencv-python==4.8.1.78
- numpy==1.24.3
- pandas==2.1.1
- apscheduler==3.10.4
- pydantic==2.4.2
- psutil==5.9.6
- beautifulsoup4==4.12.2
- lxml==4.9.3

### Install with pip
```bash
pip install -r requirements.txt
```

### Platform notes

#### Windows
If `opencv-python` or `playwright` gives trouble:
- Open a fresh terminal as a normal user
- Re-activate `.venv`
- Re-run `pip install -r requirements.txt`

#### macOS
If command-line tools are missing:
```bash
xcode-select --install
```

#### Linux
If Pillow or lxml need system libraries:

Ubuntu/Debian:
```bash
sudo apt install -y build-essential libjpeg-dev zlib1g-dev libxml2-dev libxslt1-dev
```

### Optional: install Playwright browser binaries
The current repo does not launch Playwright automatically, but if you later use browser automation:
```bash
python -m playwright install
```

### Verify imports
```bash
python - <<'PY'
import flask
import dotenv
import sqlalchemy
print('Core imports OK')
PY
```

Expected output:
```text
Core imports OK
```

---

## Step 3: Redis setup (optional in the current repository)

Redis is listed as a dependency and referenced in `<repo-root>/.env.example`, but **the current repo snapshot does not contain a working Celery app module**.

That means:
- You **can** install Redis now for future background-task support.
- You **cannot** successfully start `celery -A celery_app worker --loglevel=info` today without adding `celery_app.py` first.

### Windows
Redis is no longer officially maintained for native Windows by Redis Ltd. Use one of these:

#### Option A: Docker Desktop
```bash
docker run --name optc-redis -p 6379:6379 redis:7
```

#### Option B: WSL2
Inside Ubuntu on WSL:
```bash
sudo apt update
sudo apt install -y redis-server
sudo service redis-server start
```

### macOS
Using Homebrew:
```bash
brew install redis
brew services start redis
```

### Linux
Ubuntu/Debian:
```bash
sudo apt update
sudo apt install -y redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

Fedora:
```bash
sudo dnf install -y redis
sudo systemctl enable redis
sudo systemctl start redis
```

### Verify Redis is running
```bash
redis-cli ping
```

Expected output:
```text
PONG
```

### Alternative if Redis is unavailable
The current repository can still be launched **without Redis** because Flask and the demo API do not require it.

> [!NOTE]
> **Do not use SQLite as a Celery broker.** Celery does not support SQLite as a message broker.
> In the current project state, the practical fallback is to **skip Celery entirely** and run the Flask app plus CLI/demo API only.

---

## Step 4: Database setup

### What the current repo uses
The repository includes two storage paths:
- MongoDB settings exist in `<repo-root>/.env.example`
- SQLite is the simplest option for local launch

### Initialize the database
From the repo root:
```bash
python scripts/init_db.py
```

What this script does:
1. Tries MongoDB first
2. Falls back to SQLite if MongoDB is unavailable
3. Tries to ping Redis

### Expected behavior
If MongoDB is not installed, a normal local result looks like:
```text
Initializing OPTC Farming Bot database...
--------------------------------------------------
MongoDB not available, using SQLite
✓ SQLite database initialized
⚠ Redis not available (optional)
--------------------------------------------------
Database initialization complete!
```

### Verify database creation
For SQLite, the default database file is created from `SQLALCHEMY_DATABASE_URI`.
With the default value:
```env
SQLALCHEMY_DATABASE_URI=sqlite:///optc_farmbot.db
```
You should see `optc_farmbot.db` in the repo root after initialization.

### Migrations
There is **no migration tool configured** in the current repository.

Current behavior instead:
- `<repo-root>/app.py` runs `db.create_all()` on startup
- `<repo-root>/scripts/init_db.py` can create basic tables manually

So there is no `flask db upgrade` or Alembic step yet.

---

## Step 5: Bot data files

The problem statement mentions DLL files, `src/bisque/`, `sakura.db`, and game resources. Those items are **not present in the current repository**.

### What exists today
- Python source in `<repo-root>/bot`
- Flask app in `<repo-root>/app.py`
- Web assets in `<repo-root>/web`
- Database script in `<repo-root>/scripts/init_db.py`

### What does not exist today
- `<repo-root>/src/bisque/`
- Any `.dll` files in the repo
- Any `sakura.db` file in the repo
- Any documented resource-import directory for mobile game assets

### Guidance
Do **not** create or place random DLLs or databases into the repo unless a future code change explicitly introduces loaders for them.

---

# PART 2: CONFIGURATION

## Step 6: Environment variables

### Create `.env`
Windows PowerShell:
```powershell
Copy-Item .env.example .env
```

Windows CMD:
```cmd
copy .env.example .env
```

macOS/Linux:
```bash
cp .env.example .env
```

### Variables explained
The template lives at `<repo-root>/.env.example`.

#### Flask
- `FLASK_ENV=development`
  - Tells Flask you are running a development environment.
- `FLASK_DEBUG=True`
  - Enables debug mode and auto-reload.
- `SECRET_KEY=...`
  - Used by Flask for session security.
  - Change this for any non-test deployment.

#### Database
- `MONGODB_URI=mongodb://localhost:27017/optc_farmbot`
  - Used by the helper script if MongoDB is available.
- `SQLALCHEMY_DATABASE_URI=sqlite:///optc_farmbot.db`
  - Default local SQLite database path.
  - Relative to the repo root when you start the app there.

#### Redis
- `REDIS_URL=redis://localhost:6379/0`
  - Redis connection string.
  - Present for future/background task support.
  - Not required for the current Flask landing page and demo API.

#### Bot settings
- `BOT_MAX_ACCOUNTS=10`
  - Intended max number of accounts.
- `BOT_FARMING_INTERVAL=300`
  - Intended farming loop interval in seconds.
- `BOT_CHECK_INTERVAL=60`
  - Intended polling/check interval in seconds.

#### API settings
- `OPTC_API_BASE_URL=https://api.optc.example.com`
  - Placeholder base URL in the current repository.
  - This is not a verified live production endpoint.
- `OPTC_API_KEY=your-api-key-here`
  - Placeholder API key.

#### Web server
- `HOST=0.0.0.0`
  - Listen on all interfaces.
- `PORT=5000`
  - Flask port.

#### Logging
- `LOG_LEVEL=INFO`
  - Intended log level.
- `LOG_FILE=logs/optc_farmbot.log`
  - Declared in config, but the current app logs primarily to stdout/stderr unless you extend logging.

#### Security
- `ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5000`
  - Used by Flask-CORS for `/api/*` routes.

#### Account creation
- `AUTO_CREATE_ACCOUNTS=False`
  - Intended scheduler setting.
- `ACCOUNT_CREATION_INTERVAL=3600`
  - Intended interval in seconds.

#### Farming priorities
- `PRIORITY_EVENTS=True`
- `PRIORITY_STORY=True`
- `PRIORITY_MISSIONS=True`
- `PRIORITY_GRINDING=False`

### Minimum safe local `.env`
```env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=change-me-for-real-use
SQLALCHEMY_DATABASE_URI=sqlite:///optc_farmbot.db
REDIS_URL=redis://localhost:6379/0
HOST=127.0.0.1
PORT=5000
```

---

## Step 7: Game server configuration

The problem statement asks for JP/Global and iOS/Android selection, but the current repository does **not** expose those settings in the running UI or config files.

### What exists
- Placeholder remote API configuration in `<repo-root>/config/settings.py`
- No implemented UI fields for server region/platform selection
- No account schema field for region/platform in the current Flask models or API routes

### Current recommendation
If you need region/platform support, treat it as a future implementation task.
For the repo as it exists today, there is nothing to configure for:
- JP vs Global
- iOS vs Android

---

# PART 3: FIRST RUN

## Step 8: Start Redis (optional)

Only do this if you want Redis available for future Celery work.

### Start commands
macOS with Homebrew:
```bash
brew services start redis
```

Ubuntu/Debian:
```bash
sudo systemctl start redis-server
```

Docker:
```bash
docker start optc-redis
```

### Verify
```bash
redis-cli ping
```

Expected output:
```text
PONG
```

If Redis is not running, the current Flask app can still be launched.

---

## Step 9: Start the Flask web server

From the repo root:
```bash
python app.py
```

Typical startup output:
```text
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

### What works
Open:
- `http://localhost:5000/`
- `http://localhost:5000/api/health`

Expected health response:
```json
{
  "status": "healthy",
  "timestamp": "2026-07-02T..."
}
```

### Important limitation
The following routes are registered but currently reference missing templates:
- `http://localhost:5000/dashboard`
- `http://localhost:5000/accounts`
- `http://localhost:5000/farming`
- `http://localhost:5000/settings`
- `http://localhost:5000/logs`

Until those templates are added, use the landing page plus the JSON API/CLI.

---

## Step 10: Start a Celery worker (not available yet in this repo)

The requested command is:
```bash
celery -A celery_app worker --loglevel=info
```

### Current result
In the current repository, this will fail because there is no `celery_app.py` module in `<repo-root>`.

### What you need before this command will work
You would need all of the following first:
1. A `celery_app.py` file
2. A configured Celery instance
3. At least one registered task
4. A running broker such as Redis

### Practical guidance for now
Skip this step for the current snapshot.
The present repo can be launched using:
- Flask
- the demo API
- the CLI

---

## Step 11: Access the web dashboard

### What to open now
Open:
```text
http://localhost:5000/
```

### What you should see
The current homepage shows:
- Navigation links
- Summary stat cards
- Quick action buttons
- Recent activity area

### Login and registration
There is **no implemented login/registration flow** in the current repository.

### Navigate to accounts page
The homepage links to `/accounts`, but that page is not implemented yet because `<repo-root>/web/templates/accounts.html` does not exist.

### Use these alternatives instead
- CLI account creation
- API account creation

---

# PART 4: USING THE BOT

## Step 12: Create your first account

Because the account page is not implemented yet, use one of these methods.

### Option A: CLI
```bash
python -m bot.cli create-account --username test_user --password password123 --email test@example.com
```

Expected output:
```text
✓ Account created successfully!
Account ID: <generated-id>
Username: test_user
```

### Option B: API
In a second terminal, with Flask running:

```bash
curl -X POST http://localhost:5000/api/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "password": "password123",
    "email": "test@example.com"
  }'
```

Expected response:
```json
{
  "message": "Account created successfully",
  "account": {
    "id": "...",
    "username": "test_user",
    "email": "test@example.com",
    "status": "active",
    "level": 1,
    "berry": 0,
    "gold": 0,
    "experience": 0,
    "created_at": "..."
  }
}
```

### Current behavior note
Accounts created through the current API are stored in memory inside `<repo-root>/api/routes.py` and do not survive a server restart.

---

## Step 13: Configure farming settings

The full settings UI described in the problem statement is not implemented yet.

### What exists today
You can choose only these values in the current API/CLI flow:
- `mode`: `story`, `events`, `missions`, `grinding`, or `all`
- `strategy`: `aggressive`, `moderate`, or `conservative`
- `duration`: CLI-only placeholder argument

### What does not exist yet
The current repository does not expose fields for:
- Auto-sell cards
- Refill stamina with meat or gems
- Content priority editor in the UI
- Per-account duration form in the web dashboard

### Current way to configure behavior
Use API or CLI parameters when starting farming.

---

## Step 14: Start farming

### CLI example
```bash
python -m bot.cli start-farming --account-id YOUR_ACCOUNT_ID --mode all --strategy moderate --duration 3600
```

### API example
```bash
curl -X POST http://localhost:5000/api/farming/start \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": "YOUR_ACCOUNT_ID",
    "mode": "all",
    "strategy": "moderate"
  }'
```

Expected API response:
```json
{
  "message": "Farming started",
  "session": {
    "session_id": "...",
    "account_id": "YOUR_ACCOUNT_ID",
    "mode": "all",
    "strategy": "moderate",
    "status": "active",
    "start_time": "...",
    "runs": 0
  }
}
```

### Current behavior note
The current repository does **not** yet perform real game automation from this endpoint.
It creates a demo session object in memory.

---

## Step 15: Monitor progress

### API endpoint
```bash
curl http://localhost:5000/api/farming/status/YOUR_SESSION_ID
```

Expected response shape:
```json
{
  "session": {
    "session_id": "...",
    "account_id": "...",
    "mode": "all",
    "strategy": "moderate",
    "status": "active",
    "start_time": "...",
    "runs": 0
  },
  "account_stats": {
    "level": 1,
    "berry": 0,
    "gold": 0,
    "experience": 0
  }
}
```

### Dashboard monitoring
The landing page can display summary cards, but the full real-time multi-page dashboard described in the problem statement is not fully present yet.

### Logs
Logs currently go mainly to the terminal running Flask.
The `LOG_FILE` environment variable exists in config, but file logging is not fully wired in the current app startup code.

---

## Step 16: Stop farming

### API
```bash
curl -X POST http://localhost:5000/api/farming/stop/YOUR_SESSION_ID
```

Expected response:
```json
{
  "message": "Farming stopped",
  "session": {
    "session_id": "...",
    "account_id": "...",
    "mode": "all",
    "strategy": "moderate",
    "status": "stopped",
    "start_time": "...",
    "end_time": "...",
    "runs": 0
  }
}
```

### Current limitation
There is no completed-session summary page yet.
Use the JSON response and terminal logs instead.

---

# PART 5: ADVANCED

## Step 17: Schedule farming

The codebase includes a scheduler class in `<repo-root>/bot/farmer.py`:
- `FarmingScheduler`

However, it is **not connected to Flask routes or a persistent task runner** in the current repository.

### What this means
- Recurring farming schedules are not available from the running web app yet.
- Multiple accounts in sequence are not wired into a background worker yet.

---

## Step 18: Troubleshooting

### Problem: `ModuleNotFoundError: No module named 'flask'`
Cause:
- Dependencies are not installed in the active Python environment.

Fix:
```bash
pip install -r requirements.txt
```

### Problem: `ModuleNotFoundError: No module named 'dotenv'`
Cause:
- `python-dotenv` is missing.

Fix:
```bash
pip install -r requirements.txt
```

### Problem: `redis-cli: command not found`
Cause:
- Redis client tools are not installed.

Fix:
- Install Redis for your OS, or
- Skip Redis for the current Flask/demo API workflow.

### Problem: `/dashboard` or `/accounts` returns a server error
Cause:
- Those routes point to templates that do not exist yet.

Fix:
- Use `http://localhost:5000/` instead
- Use the API/CLI for account and farming actions until the templates are implemented

### Problem: Celery command fails
Cause:
- No `celery_app.py` exists in the repo.

Fix:
- Skip Celery for now, or
- Implement Celery wiring before trying to run a worker

### Problem: database file not created
Checks:
1. Confirm you are in the repo root when running commands.
2. Confirm `.env` does not override `SQLALCHEMY_DATABASE_URI` incorrectly.
3. Re-run:
```bash
python scripts/init_db.py
```

### Problem: port 5000 already in use
Fix:
Change `.env`:
```env
PORT=5001
```
Then start again:
```bash
python app.py
```

### Problem: need to reset SQLite data
1. Stop Flask
2. Delete the SQLite database file from the repo root
3. Re-run:
```bash
python scripts/init_db.py
```

---

## Step 19: Multi-account management

### Current support
- The demo API can hold multiple account objects in memory.
- The CLI can create and list multiple accounts inside one process instance.

### Current limitation
There is no persistent multi-account dashboard yet.
The current API store is in-memory and resets on server restart.

### Useful endpoint
```bash
curl http://localhost:5000/api/accounts
```

Expected response:
```json
{
  "accounts": [...],
  "count": 2
}
```

---

## Step 20: Stopping everything

### Stop Flask
In the terminal running the server:
```text
Ctrl+C
```

### Stop Redis
macOS:
```bash
brew services stop redis
```

Ubuntu/Debian:
```bash
sudo systemctl stop redis-server
```

Docker:
```bash
docker stop optc-redis
```

### Safe database closure
SQLite closes automatically when the Python process exits normally.

### Backup important data
For SQLite, back up the database file from the repo root:
```bash
cp optc_farmbot.db optc_farmbot.db.backup
```

---

# APPENDIX

## File structure explanation

Current top-level layout:

```text
<repo-root>/
├── app.py
├── .env.example
├── requirements.txt
├── README.md
├── API.md
├── models.py
├── api/
│   └── routes.py
├── bot/
│   ├── account_manager.py
│   ├── api_client.py
│   ├── cli.py
│   └── farmer.py
├── config/
│   └── settings.py
├── scripts/
│   └── init_db.py
├── tests/
│   └── test_bot.py
└── web/
    ├── routes.py
    ├── static/
    │   ├── css/style.css
    │   └── js/
    │       ├── dashboard.js
    │       └── main.js
    └── templates/
        └── index.html
```

### What each main file does
- `<repo-root>/app.py`
  - Creates the Flask app, loads env vars, registers blueprints, creates SQLAlchemy tables.
- `<repo-root>/api/routes.py`
  - Provides JSON endpoints for health, accounts, farming, and stats.
- `<repo-root>/web/routes.py`
  - Declares HTML page routes.
- `<repo-root>/models.py`
  - Defines SQLAlchemy models.
- `<repo-root>/bot/cli.py`
  - Command-line interface.
- `<repo-root>/bot/account_manager.py`
  - In-memory account logic.
- `<repo-root>/bot/farmer.py`
  - Demo farming and scheduling logic.
- `<repo-root>/bot/api_client.py`
  - Placeholder async API wrapper.
- `<repo-root>/scripts/init_db.py`
  - Manual DB/bootstrap script.

### Logs
Current logs are easiest to read from the terminal output of `python app.py`.

### Database location
By default:
- SQLite database: `<repo-root>/optc_farmbot.db`

### Custom scripts
Place your own utility scripts under:
- `<repo-root>/scripts/`

---

## Command reference

### Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/init_db.py
```

### Start app
```bash
python app.py
```

### Health check
```bash
curl http://localhost:5000/api/health
```

### Create account via API
```bash
curl -X POST http://localhost:5000/api/accounts \
  -H "Content-Type: application/json" \
  -d '{"username":"user1","password":"pass123","email":"user1@example.com"}'
```

### List accounts
```bash
curl http://localhost:5000/api/accounts
```

### Start farming
```bash
curl -X POST http://localhost:5000/api/farming/start \
  -H "Content-Type: application/json" \
  -d '{"account_id":"ACCOUNT_ID","mode":"all","strategy":"moderate"}'
```

### Stop farming
```bash
curl -X POST http://localhost:5000/api/farming/stop/SESSION_ID
```

### List sessions
```bash
curl http://localhost:5000/api/farming/sessions
```

### Run tests
```bash
python -m unittest tests.test_bot -q
```

---

## FAQ

### Does this repo currently launch a full production farming dashboard?
No. It currently launches a Flask app, a landing page, demo API endpoints, and CLI helpers.

### Can I use Redis today?
Yes, but only as preparation for future background work. The current repo does not yet include working Celery wiring.

### Can I run a Celery worker today?
No, not with the repository exactly as it stands, because `celery_app.py` is missing.

### Is there a login page?
No.

### Are accounts persistent?
- Flask API accounts: no, they are in-memory in the current routes module
- SQLAlchemy models exist, but the current account API is not wired to them yet

### Where are the game DLLs or `sakura.db`?
They are not present in the current repository snapshot.

### Where should I look if startup fails?
Check:
- the terminal running `python app.py`
- your `.env`
- whether dependencies installed successfully

---

## System requirements

### Minimum
- 2 CPU cores
- 4 GB RAM
- 2 GB free disk space
- Python 3.9+
- Internet connection for dependency installation

### Recommended
- 4 CPU cores
- 8 GB RAM
- 5+ GB free disk space
- Python 3.11
- Redis installed if you plan to add background workers later

### Storage notes
Most storage use will come from:
- Python virtual environment
- pip package cache
- optional browser automation dependencies
- SQLite database growth over time

### Bandwidth notes
Current bandwidth needs are low for local setup itself.
Any real game automation layer added later would increase network usage significantly.

---

## Beginner quick-start summary

If you only want the fastest path to a working local launch of the **current repository**, do this:

```bash
git clone https://github.com/asteria93/optc-farmbot.git
cd optc-farmbot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python scripts/init_db.py
python app.py
```

Then open:
```text
http://localhost:5000/
```

If you want account/farming actions right now, use the JSON API or CLI examples in this guide.
