# OPTC Farming Bot

A comprehensive web-based bot for automating One Piece Treasure Cruise (OPTC) gameplay, including account creation, event farming, story mode progression, and mission completion.

## Features

- 🤖 **Automated Account Creation** - Create multiple OPTC accounts automatically
- 🎮 **Story Mode Farming** - Auto-complete story chapters
- 🎪 **Event Farming** - Farm all available events and limited-time content
- 📋 **Mission Completion** - Complete daily, weekly, and monthly missions
- 🔄 **Continuous Farming** - Set schedules for automated farming runs
- 📊 **Dashboard** - Web-based interface to monitor and control the bot
- 🔐 **Account Management** - Manage multiple accounts with ease
- 📈 **Progress Tracking** - Track farming progress and statistics
- ⚙️ **Configuration** - Customize farming strategies and priorities

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- MongoDB (optional, for account storage)
- Redis (optional, for task queuing)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/asteria93/optc-farmbot.git
cd optc-farmbot
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
python scripts/init_db.py
```

## Usage

### Start the Web Server

```bash
python app.py
```

The web interface will be available at `http://localhost:5000`

### Create an Account

```bash
python -m bot.cli create-account --username "test_user" --password "password123"
```

### Start Farming

```bash
python -m bot.cli start-farming --account-id "account_123" --mode "all"
```

### View Status

Visit the dashboard at `http://localhost:5000/dashboard` to monitor progress

## Project Structure

```
optc-farmbot/
├── app.py                 # Flask web server
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── README.md             # This file
├── config/               # Configuration files
├── bot/                  # Core bot logic
├── api/                  # API endpoints
├── web/                  # Web interface
├── scripts/              # Utility scripts
└── tests/                # Unit tests
```

## Configuration

Edit `config/settings.py` to customize:
- Farming targets and priorities
- Farming schedule
- Account creation strategy
- API endpoints
- Bot behavior

## API Documentation

See `API.md` for detailed API endpoint documentation.

## Warning ⚠️

**DISCLAIMER**: This bot is for educational purposes only. Using bots to automate mobile games may violate the game's Terms of Service. The author is not responsible for any account bans, data loss, or other consequences. Use at your own risk.

## Contributing

Contributions are welcome! Please follow the contribution guidelines in `CONTRIBUTING.md`

## License

MIT License - see LICENSE file for details

## Support

For issues and questions, open an issue on GitHub.
