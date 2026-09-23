import time
import pytest
from models import Fruit, StockWindow, StockSnapshot, format_short_number


def test_format_short_number():
    assert format_short_number(0) == "0"
    assert format_short_number(500) == "500"
    assert format_short_number(1000) == "1K"
    assert format_short_number(5500) == "5.5K"
    assert format_short_number(1_000_000) == "1M"
    assert format_short_number(120_000_000) == "120M"
    assert format_short_number(1_500_000_000) == "1.5B"
    assert format_short_number(None) == "N/A"
    # String and float inputs
    assert format_short_number("1000000") == "1M"
    assert format_short_number(2500000.0) == "2.5M"
    assert format_short_number("invalid") == "N/A"


def test_fruit_properties_and_serialization():
    fruit_dict = {
        "name": "Kitsune",
        "beliPrice": 8000000,
        "robuxPrice": 4000,
        "fruitType": "Beast",
        "image": "https://example.com/kitsune.png",
        "itemId": "99",
        "rarity": "Mythical",
        "regularValue": 130000000,
        "permanentValue": 250000000,
        "regularDemand": 10,
        "permanentDemand": 10,
        "regularTrend": "Rising",
        "permanentTrend": "Stable",
        "bestUsedFor": "PvP & Grinding",
        "valuePath": "/values/fruits/kitsune"
    }

    fruit = Fruit.from_dict(fruit_dict)
    assert fruit.name == "Kitsune"
    assert fruit.beli_price == 8000000
    assert fruit.formatted_beli == "8,000,000 Beli"
    assert fruit.formatted_robux == "4,000 R$"
    assert fruit.formatted_value == "130M"
    assert fruit.rarity == "Mythical"
    assert fruit.rarity_emoji == "🔴"
    assert fruit.rarity_color == 0xE91E63
    assert fruit.best_used_for == "PvP & Grinding"

    # Test roundtrip serialization
    serialized = fruit.to_dict()
    assert serialized["name"] == "Kitsune"
    assert serialized["beli_price"] == 8000000
    roundtrip = Fruit.from_dict(serialized)
    assert roundtrip.name == fruit.name
    assert roundtrip.beli_price == fruit.beli_price


def test_fruit_defaults_and_edge_cases():
    empty_fruit = Fruit.from_dict({})
    assert empty_fruit.name == "Unknown Fruit"
    assert empty_fruit.beli_price == 0
    assert empty_fruit.formatted_beli == "N/A"
    assert empty_fruit.formatted_robux == "N/A"
    assert empty_fruit.rarity == "Common"
    assert empty_fruit.rarity_emoji == "⚪"


def test_stock_window():
    now_ms = int(time.time() * 1000)
    resets_at = now_ms + 7200 * 1000  # 2 hours from now
    window = StockWindow(
        kind="mirage",
        started_at=now_ms,
        resets_at=resets_at,
        period_ms=7200000
    )

    assert window.kind == "mirage"
    assert window.resets_at_seconds == resets_at // 1000
    assert "h" in window.countdown_formatted or "m" in window.countdown_formatted
    assert f"<t:{resets_at // 1000}:R>" == window.discord_relative_timestamp
    assert f"<t:{resets_at // 1000}:T>" == window.discord_time_timestamp

    # Serialization
    d = window.to_dict()
    assert d["kind"] == "mirage"
    assert d["countdown_seconds"] > 7000


def test_stock_window_zero_or_negative_resets_at():
    # Edge case: resets_at is 0 or uninitialized
    zero_window = StockWindow(
        kind="normal",
        started_at=0,
        resets_at=0,
        period_ms=14400000
    )
    assert zero_window.resets_at_seconds == 0
    assert zero_window.countdown_seconds == 0
    assert zero_window.countdown_formatted == "Pending"
    assert zero_window.discord_relative_timestamp == "*Pending restock*"
    assert zero_window.discord_time_timestamp == "*Pending*"


def test_stock_snapshot():
    now_ms = int(time.time() * 1000)
    raw = {
        "timestamp": now_ms,
        "normal": {
            "window": {"kind": "normal", "startedAt": now_ms, "resetsAt": now_ms + 14400000, "periodMs": 14400000},
            "fruits": [
                {"name": "Rocket", "rarity": "Common", "beliPrice": 5000},
                {"name": "Flame", "rarity": "Uncommon", "beliPrice": 250000},
            ],
            "stale": False,
            "pending": False,
        },
        "mirage": {
            "window": {"kind": "mirage", "startedAt": now_ms, "resetsAt": now_ms + 7200000, "periodMs": 7200000},
            "fruits": [
                {"name": "Tiger", "rarity": "Mythical", "beliPrice": 5000000},
            ],
            "stale": False,
            "pending": False,
        }
    }

    snapshot = StockSnapshot.from_raw_snapshot(raw)
    assert len(snapshot.normal_fruits) == 2
    assert len(snapshot.mirage_fruits) == 1
    assert snapshot.get_highest_rarity("regular") == "Uncommon"
    assert snapshot.get_highest_rarity("mirage") == "Mythical"
    assert snapshot.get_highest_rarity("all") == "Mythical"

    # Search fruits
    found = snapshot.find_fruit("rocket")
    assert found is not None
    assert found.name == "Rocket"

    found_partial = snapshot.find_fruit("tig")
    assert found_partial is not None
    assert found_partial.name == "Tiger"

    not_found = snapshot.find_fruit("Dragon")
    assert not_found is None
