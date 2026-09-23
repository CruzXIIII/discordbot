# 🍈 Blox Fruits Stock Discord Bot & Live API

A feature-rich, high-performance Discord Bot and REST API service for tracking live **Blox Fruits** dealer stock in real time. It monitors both the standard **Blox Fruit Dealer** (4-hour rotation cycle) and the **Mirage Island Dealer** (2-hour rotation cycle), providing rich interactive Discord embeds, live countdowns, background auto-announcements, and customizable fruit watchlists.

---

## ✨ Features

- **Live Dealer Stock Tracking**:
  - Regular Dealer inventory (4-hour cycle)
  - Mirage Island Dealer inventory (2-hour cycle)
  - Rarity color-coded embeds, Beli prices, Robux prices, physical values, and demand ratings (1-10)
- **Interactive Discord UI**:
  - `discord.ui.View` interactive button bar (`🍈 All Stock`, `🏪 Regular Dealer`, `🌊 Mirage Dealer`, `⏱️ Countdown`, `🔄 Refresh`)
  - Clicking `🔄 Refresh` re-fetches live stock and updates the embed instantly in-place!
- **Dynamic Live Countdowns**:
  - Utilizes Discord's native `<t:TIMESTAMP:R>` relative timestamps that continuously update inside the Discord client without requiring spam edits.
- **Background Auto-Announcements**:
  - Detects global dealer restocks every minute.
  - Automatically posts announcements to designated Discord server channels.
  - Optional ping roles (e.g. `@Stock Alerts`).
- **High-Demand Fruit Watchlists**:
  - Server admins can configure watched fruits (e.g. `Kitsune`, `Dragon`, `Leopard`, `Buddha`, `Portal`, `Dough`).
  - When a watched fruit comes into stock, the bot triggers a highlighted alert: `🚨 WATCHLIST ALERT!`.
- **Hybrid Data Pipeline**:
  - Primary: Direct API endpoint (`STOCK_API_URL`, configured to `https://api.bloxfruitsvalues.com/stock`).
  - Intelligent Fallback: Scrapes and parses the real-time Next.js React Server Component (RSC) snapshot from `https://bloxfruitsvalues.com/stock` if the primary API domain is unreachable or blocked.
  - High-efficiency in-memory caching with TTL to prevent rate-limiting.
- **Embedded / Standalone REST API**:
  - Built-in HTTP REST API exposing `/stock`, `/stock/regular`, `/stock/mirage`, and `/health` in clean JSON format for other apps, scripts, or dashboards.

---

## 📋 Slash Commands & Prefix Commands

### Stock & Lookup
| Slash Command | Prefix Command | Description |
| :--- | :--- | :--- |
| `/stock [dealer]` | `!stock [all\|regular\|mirage]` | Displays current dealer stock with interactive buttons. |
| `/countdown` | `!countdown` | Displays countdown timers to the next dealer restocks. |
| `/fruit <name>` | `!fruit <name>` | Detailed info card for a fruit: price, rarity, demand, value, and current stock status. |
| `/help` | `!help` | Displays command guide and setup instructions. |

### Tracking & Announcements (Requires `Manage Server` permission)
| Slash Command | Description |
| :--- | :--- |
| `/track set [channel]` | Designates a channel for automatic stock rotation alerts. |
| `/track stop` | Disables automatic stock announcements in the server. |
| `/track pingrole [role]` | Sets a role to mention when stock rotates (leave blank to disable). |
| `/track status` | Displays active tracking channel, ping role, and watchlist. |
| `/watchlist add <fruit>` | Adds a fruit to the high-demand alert list. |
| `/watchlist remove <fruit>`| Removes a fruit from the alert list. |
| `/watchlist list` | Lists all fruits currently being watched. |

---

## 🛠️ Project Structure

```
discordbot/
├── .env                       # Environment configuration (Token, API URLs, Port)
├── .env.example               # Example template for environment variables
├── bot.py                     # Main Discord bot client, slash commands, UI buttons
├── bot_config.py              # Persistent JSON configuration store (channels, watchlists)
├── config.py                  # Environment loader and constants
├── embeds.py                  # Discord embed formatters and visual styling
├── models.py                  # Dataclasses: Fruit, StockWindow, StockSnapshot
├── stock_api.py               # Stock fetcher (API fetch + webpage snapshot fallback)
├── tracker.py                 # Background loop monitoring resets & sending announcements
├── api_server.py              # Local HTTP REST API server
├── run.py                     # CLI launcher for bot and API server
├── requirements.txt           # Python package dependencies
├── pytest.ini                 # Pytest configuration
├── data/
│   └── bot_config.json        # Saved server configurations (channels & alerts)
└── tests/                     # 19 comprehensive unit and integration tests
    ├── fixtures/
    │   └── snapshot.json      # Sample live snapshot fixture
    ├── test_models.py
    ├── test_embeds.py
    ├── test_bot_config.py
    ├── test_stock_api.py
    ├── test_api_server.py
    └── test_discord_login.py
```

---

## 🚀 Getting Started

### 1. Requirements
- Python 3.10+ (tested on Python 3.14)
- Discord Bot Token with permissions:
  - `Send Messages`
  - `Embed Links`
  - `Use Application Commands`
  - `Read Message History`

### 2. Installation
Ensure virtual environment is active and install requirements:
```bash
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

### 3. Configuration
Check or edit `.env`:
```ini
DISCORD_TOKEN=your_bot_token_here
BOT_PREFIX=!
STOCK_API_URL=https://api.bloxfruitsvalues.com/stock
STOCK_FALLBACK_URL=https://bloxfruitsvalues.com/stock
STOCK_CHECK_INTERVAL_SECONDS=60
API_HOST=0.0.0.0
API_PORT=8080
```

### 4. Running the Bot & API Service

**Run Both Bot and Local REST API:**
```bash
.\.venv\Scripts\python run.py
```

**Run Only Discord Bot:**
```bash
.\.venv\Scripts\python run.py --bot-only
```

**Run Only REST API Server:**
```bash
.\.venv\Scripts\python run.py --api-only --port 8080
```

---

## 🌐 Local REST API Reference

When the REST API is running (default port `8080`), you can query stock data directly from any HTTP client:

- `GET http://localhost:8080/stock`
  Returns full JSON snapshot with regular and mirage stock:
  ```json
  {
    "status": "success",
    "source": "bloxfruitsvalues",
    "data": {
      "timestamp": 1790165000000,
      "normal": {
        "window": {
          "resets_at": 1790179200000,
          "countdown_seconds": 9600,
          "countdown_formatted": "2h 40m 0s"
        },
        "fruits": [
          {
            "name": "Dark",
            "beli_price": 500000,
            "robux_price": 950,
            "rarity": "Uncommon",
            "regular_demand": 3
          }
        ]
      },
      "mirage": { ... }
    }
  }
  ```
- `GET http://localhost:8080/stock/regular` — Only regular dealer fruits and countdown.
- `GET http://localhost:8080/stock/mirage` — Only mirage dealer fruits and countdown.
- `GET http://localhost:8080/health` — Health check endpoint (`{"status": "ok"}`).

---

## 🧪 Running Tests

The project includes 19 automated tests covering models, embed layout, configuration persistence, API endpoints, caching, fallback parsing, and Discord gateway connectivity:

```bash
.\.venv\Scripts\pytest -v
```

All 19 tests pass successfully.
