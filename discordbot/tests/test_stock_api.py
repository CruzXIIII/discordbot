import json
from pathlib import Path
import pytest
import stock_api
from models import StockSnapshot


def test_extract_snapshot_from_mock_html():
    fixture_path = Path(__file__).parent / "fixtures" / "snapshot.json"
    assert fixture_path.exists(), "Fixtures snapshot.json must exist"

    with open(fixture_path, "r", encoding="utf-8") as f:
        snapshot_data = json.load(f)

    # Wrap in Next.js RSC push script format
    inner_payload = f'2f:["$","$L4b",null,{{"initialSnapshot":{json.dumps(snapshot_data)}}}]'
    mock_push = json.dumps([1, inner_payload])
    mock_html = f'<html><head></head><body><script>self.__next_f.push({mock_push})</script></body></html>'

    extracted = stock_api._extract_snapshot_from_html(mock_html)
    assert extracted is not None
    assert "normal" in extracted
    assert "mirage" in extracted
    assert len(extracted["normal"]["fruits"]) == len(snapshot_data["normal"]["fruits"])


def test_extract_snapshot_balanced_brace_fallback():
    fixture_path = Path(__file__).parent / "fixtures" / "snapshot.json"
    with open(fixture_path, "r", encoding="utf-8") as f:
        snapshot_data = json.load(f)

    # Simulate HTML where push array parsing fails, leaving escaped text with nested braces
    raw_escaped = json.dumps(snapshot_data).replace('"', r'\"')
    mock_html = f'<html><body>Some text \\"initialSnapshot\\":{raw_escaped} other trailing text</body></html>'

    extracted = stock_api._extract_snapshot_from_html(mock_html)
    assert extracted is not None
    assert "normal" in extracted
    assert "mirage" in extracted
    assert len(extracted["normal"]["fruits"]) == len(snapshot_data["normal"]["fruits"])


def test_extract_snapshot_invalid_html():
    extracted = stock_api._extract_snapshot_from_html("<html><body>Empty</body></html>")
    assert extracted is None


def test_caching_behavior(monkeypatch):
    # Reset cache
    stock_api._cached_snapshot = None
    stock_api._cache_timestamp = 0

    fixture_path = Path(__file__).parent / "fixtures" / "snapshot.json"
    with open(fixture_path, "r", encoding="utf-8") as f:
        snapshot_data = json.load(f)

    call_count = 0

    def mock_fallback_page(url, timeout=12.0):
        nonlocal call_count
        call_count += 1
        return snapshot_data

    monkeypatch.setattr(stock_api, "fetch_from_api_endpoint", lambda url, timeout=8.0: None)
    monkeypatch.setattr(stock_api, "fetch_from_fallback_page", mock_fallback_page)

    # First call: should fetch
    snap1 = stock_api.fetch_stock_sync(force_refresh=False)
    assert call_count == 1
    assert len(snap1.normal_fruits) > 0

    # Second call: should hit cache
    snap2 = stock_api.fetch_stock_sync(force_refresh=False)
    assert call_count == 1  # Not incremented!
    assert snap2 is snap1

    # Forced refresh: should bypass cache
    snap3 = stock_api.fetch_stock_sync(force_refresh=True)
    assert call_count == 2
