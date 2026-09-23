import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Load environment variables from .env file
load_dotenv(BASE_DIR / ".env")

# Discord Configuration
DISCORD_TOKEN = os.getenv(
    "DISCORD_TOKEN",
    "MTU1MjMwMzUxNjQ2NTM2OTA5OA.GPOstV.Y6CALKkr83FLzmNUp82kPr4_y1VL836jQTaNDE"
).strip()

BOT_PREFIX = os.getenv("BOT_PREFIX", "!").strip()

# Stock API and Scraping Configuration
# User requested API endpoint; fallback to main site stock tracker if API hostname is not reachable
STOCK_API_URL = os.getenv("STOCK_API_URL", "https://api.bloxfruitsvalues.com/stock").strip()
STOCK_FALLBACK_URL = os.getenv("STOCK_FALLBACK_URL", "https://bloxfruitsvalues.com/stock").strip()

# Interval in seconds to check for stock changes in background
STOCK_CHECK_INTERVAL_SECONDS = int(os.getenv("STOCK_CHECK_INTERVAL_SECONDS", "60"))

# Local REST API Server configuration (optional standalone / embedded API)
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("PORT", os.getenv("API_PORT", "8080")))

# Persistent storage file path
CONFIG_FILE_PATH = DATA_DIR / "bot_config.json"

# Rarity Color Palettes (Discord embed hex colors)
RARITY_COLORS = {
    "Common": 0x9E9E9E,       # Gray
    "Uncommon": 0x4CAF50,     # Green
    "Rare": 0x2196F3,         # Blue
    "Legendary": 0x9C27B0,    # Purple
    "Mythical": 0xE91E63,     # Crimson Pink/Red
    "Default": 0x5865F2,      # Discord Blurple
}

# Rarity Emojis
RARITY_EMOJIS = {
    "Common": "⚪",
    "Uncommon": "🟢",
    "Rare": "🔵",
    "Legendary": "🟣",
    "Mythical": "🔴",
}
