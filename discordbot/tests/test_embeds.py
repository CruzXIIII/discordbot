import time
import pytest
from models import Fruit, StockWindow, StockSnapshot
from embeds import (
    build_stock_embed,
    build_countdown_embed,
    build_fruit_detail_embed,
    build_announcement_embed,
    format_fruit_line
)


@pytest.fixture
def sample_snapshot():
    now_ms = int(time.time() * 1000)
    return StockSnapshot(
        timestamp=now_ms,
        normal_window=StockWindow("normal", now_ms, now_ms + 14400000, 14400000),
        normal_fruits=[
            Fruit(name="Rocket", beli_price=5000, robux_price=50, rarity="Common", regular_demand=1),
            Fruit(name="Flame", beli_price=250000, robux_price=550, rarity="Uncommon", regular_demand=4),
            Fruit(name="Buddha", beli_price=1200000, robux_price=1650, rarity="Legendary", regular_demand=9),
        ],
        mirage_window=StockWindow("mirage", now_ms, now_ms + 7200000, 7200000),
        mirage_fruits=[
            Fruit(name="Tiger", beli_price=5000000, robux_price=3000, rarity="Mythical", regular_demand=8),
        ]
    )


def test_format_fruit_line():
    f = Fruit(name="Venom", beli_price=3000000, robux_price=2450, rarity="Mythical", regular_value=20000000, regular_demand=7)
    line = format_fruit_line(f)
    assert "**Venom**" in line
    assert "3,000,000 Beli" in line
    assert "20M" in line
    assert "7/10" in line


def test_build_stock_embed(sample_snapshot):
    # Test "all"
    embed_all = build_stock_embed(sample_snapshot, view_type="all")
    assert "Blox Fruits — Live Dealer Stock" in embed_all.title
    assert len(embed_all.fields) == 2
    assert "Regular Dealer" in embed_all.fields[0].name
    assert "Mirage Island Dealer" in embed_all.fields[1].name

    # Test "regular"
    embed_reg = build_stock_embed(sample_snapshot, view_type="regular")
    assert "Regular Dealer Stock" in embed_reg.title
    assert len(embed_reg.fields) == 1

    # Test "mirage"
    embed_mir = build_stock_embed(sample_snapshot, view_type="mirage")
    assert "Mirage Island Dealer Stock" in embed_mir.title
    assert len(embed_mir.fields) == 1


def test_build_fruit_detail_embed(sample_snapshot):
    fruit = sample_snapshot.normal_fruits[0]
    embed = build_fruit_detail_embed(fruit, is_in_normal=True, is_in_mirage=False)
    assert "Rocket Fruit" in embed.title
    field_dict = {f.name: f.value for f in embed.fields}
    assert "✅ Regular Dealer" in field_dict["Current Stock"]
    assert "5,000 Beli" in field_dict["Beli Price"]


def test_build_countdown_embed(sample_snapshot):
    embed = build_countdown_embed(sample_snapshot)
    assert "Restock Countdowns" in embed.title
    assert len(embed.fields) == 2
    assert "Regular Blox Fruit Dealer" in embed.fields[0].name
    assert "Mirage Island Dealer" in embed.fields[1].name


def test_build_announcement_embed(sample_snapshot):
    # Without watched hits
    embed_no_hits = build_announcement_embed(sample_snapshot, watched_hits=[], dealer_type="normal")
    assert "Stock Rotated" in embed_no_hits.title
    assert "WATCHLIST ALERT" not in embed_no_hits.description

    # With watched hits
    embed_with_hits = build_announcement_embed(sample_snapshot, watched_hits=["Tiger", "Buddha"], dealer_type="both")
    assert "WATCHLIST ALERT" in embed_with_hits.description
    assert "**Tiger**" in embed_with_hits.description
