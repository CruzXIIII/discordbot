import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from tracker import StockTracker
from models import StockSnapshot, StockWindow, Fruit
from bot_config import BotConfigStore


@pytest.fixture
def mock_bot():
    bot = MagicMock()
    bot.wait_until_ready = AsyncMock()
    bot.get_channel = MagicMock()
    return bot


def test_tracker_prevent_duplicate_start(mock_bot):
    tracker = StockTracker(mock_bot)
    tracker.track_loop = MagicMock()
    tracker.track_loop.is_running.return_value = True

    # Calling start while running should NOT call track_loop.start()
    tracker.start()
    tracker.track_loop.start.assert_not_called()

    # When not running, it SHOULD call track_loop.start()
    tracker.track_loop.is_running.return_value = False
    tracker.start()
    tracker.track_loop.start.assert_called_once()


def test_tracker_handles_pending_stock(mock_bot):
    async def _runner():
        tracker = StockTracker(mock_bot)
        tracker.is_first_run = False

        fake_config = MagicMock()
        fake_config.last_normal_reset = 1000
        fake_config.last_mirage_reset = 2000
        fake_config.data = {"channels": {}}

        # Snapshot with changed resets_at but normal_pending is True
        pending_snapshot = StockSnapshot(
            normal_window=StockWindow("normal", 0, 5000, 14400000),
            normal_fruits=[Fruit(name="Rocket")],
            normal_pending=True,  # Scanning in progress
            mirage_window=StockWindow("mirage", 0, 2000, 7200000),
            mirage_fruits=[],
            mirage_pending=False,
        )

        with patch("tracker.stock_api.fetch_stock_async", AsyncMock(return_value=pending_snapshot)), \
             patch("tracker.config_store", fake_config):
            await tracker.track_loop()

            # Because normal_pending is True, update_last_resets should NOT have been called with 5000
            fake_config.update_last_resets.assert_not_called()

    asyncio.run(_runner())
