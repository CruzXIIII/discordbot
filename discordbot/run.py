import argparse
import logging
import signal
import sys
import threading
from config import DISCORD_TOKEN, API_HOST, API_PORT
from api_server import StockApiServer
from bot import bot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("bloxfruits.main")


def main():
    parser = argparse.ArgumentParser(description="Blox Fruits Stock Discord Bot & API Service")
    parser.add_argument("--bot-only", action="store_true", help="Run only the Discord Bot")
    parser.add_argument("--api-only", action="store_true", help="Run only the REST API Server")
    parser.add_argument("--port", type=int, default=API_PORT, help=f"Port for REST API (default: {API_PORT})")
    parser.add_argument("--host", type=str, default=API_HOST, help=f"Host for REST API (default: {API_HOST})")
    args = parser.parse_args()

    api_server = None

    if not args.bot_only:
        # Start API server in background thread
        logger.info("Initializing Local REST API server on %s:%d...", args.host, args.port)
        api_server = StockApiServer(host=args.host, port=args.port)
        api_server.start()

    if args.api_only:
        logger.info("Running in API-only mode. Press Ctrl+C to terminate.")
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down API server...")
            if api_server:
                api_server.stop()
            sys.exit(0)

    # Run Discord Bot
    logger.info("Starting Discord Bot...")
    if not DISCORD_TOKEN:
        logger.error("FATAL: DISCORD_TOKEN is missing in environment or config.py!")
        if api_server:
            api_server.stop()
        sys.exit(1)

    try:
        bot.run(DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("Bot interrupted by user.")
    except Exception as e:
        logger.error("Bot encountered fatal error: %s", e)
    finally:
        if api_server:
            api_server.stop()


if __name__ == "__main__":
    main()
