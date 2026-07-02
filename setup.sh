#!/usr/bin/env bash
# OPTC Farming Bot — Linux/Mac setup script
set -e

echo "======================================"
echo "  OPTC Farming Bot — Setup"
echo "======================================"
echo ""

# --- Python check ---
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found. Please install Python 3.8+ first."
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  macOS:         brew install python"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✓ Python $PYTHON_VERSION found"

# --- Virtual environment ---
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate
# shellcheck disable=SC1091
source venv/bin/activate
echo "✓ Virtual environment activated"

# --- Dependencies ---
echo ""
echo "Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✓ Dependencies installed"

# --- Environment file ---
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ""
    echo "✓ .env file created from .env.example"
    echo ""
    echo "  *** ACTION REQUIRED ***"
    echo "  Edit .env and set a secure SECRET_KEY before running in production."
    echo "  Open .env in your editor now, or do it later before starting the bot."
else
    echo "✓ .env already exists (not overwritten)"
fi

# --- Logs directory ---
mkdir -p logs
echo "✓ logs/ directory ready"

# --- Database ---
echo ""
echo "Initializing database..."
python scripts/init_db.py
echo "✓ Database initialized"

# --- Redis check ---
echo ""
if command -v redis-cli &>/dev/null && redis-cli ping &>/dev/null 2>&1; then
    echo "✓ Redis is running"
else
    echo "⚠ Redis not detected — make sure to start it before running the bot."
    echo "  Ubuntu/Debian: sudo apt install redis-server && sudo systemctl start redis"
    echo "  macOS:         brew install redis && brew services start redis"
fi

echo ""
echo "======================================"
echo "  Setup complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your settings (especially SECRET_KEY)"
echo "  2. Start Redis if not already running"
echo "  3. Run: ./start.sh"
echo ""
