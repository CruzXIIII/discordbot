import tempfile
from pathlib import Path
from bot_config import BotConfigStore


def test_bot_config_store():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir) / "test_config.json"
        store = BotConfigStore(file_path=tmp_path)

        # Initial state
        assert store.get_channel(12345) is None
        assert store.last_normal_reset == 0

        # Set channel
        store.set_channel(12345, 67890)
        assert store.get_channel(12345) == 67890

        # Persistence check: create new store pointing to same file
        store2 = BotConfigStore(file_path=tmp_path)
        assert store2.get_channel(12345) == 67890

        # Remove channel
        assert store.remove_channel(12345) is True
        assert store.get_channel(12345) is None
        assert store.remove_channel(99999) is False

        # Ping role
        store.set_ping_role(12345, 11111)
        assert store.get_ping_role(12345) == 11111
        store.set_ping_role(12345, None)
        assert store.get_ping_role(12345) is None

        # Watchlist
        default_wl = store.get_watchlist(12345)
        assert "Kitsune" in default_wl

        assert store.add_to_watchlist(12345, "Rocket") is True
        assert "Rocket" in store.get_watchlist(12345)
        assert store.add_to_watchlist(12345, "Rocket") is False

        assert store.remove_from_watchlist(12345, "Rocket") is True
        assert "Rocket" not in store.get_watchlist(12345)

        # Reset times
        store.update_last_resets(1000, 2000)
        assert store.last_normal_reset == 1000
        assert store.last_mirage_reset == 2000
