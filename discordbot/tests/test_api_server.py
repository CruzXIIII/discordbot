import time
import json
import urllib.request
import urllib.error
import pytest
from api_server import StockApiServer


@pytest.fixture(scope="module")
def running_api_server():
    server = StockApiServer(host="127.0.0.1", port=8199)
    server.start()
    time.sleep(0.5)  # Allow thread to bind
    yield "http://127.0.0.1:8199"
    server.stop()


def test_api_health(running_api_server):
    url = f"{running_api_server}/health"
    with urllib.request.urlopen(url, timeout=5) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert data.get("status") == "ok"


def test_api_stock(running_api_server):
    url = f"{running_api_server}/stock"
    with urllib.request.urlopen(url, timeout=10) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert data.get("status") == "success"
        assert "normal" in data["data"]
        assert "mirage" in data["data"]
        assert len(data["data"]["normal"]["fruits"]) > 0


def test_api_regular_and_mirage(running_api_server):
    # Regular
    url_reg = f"{running_api_server}/stock/regular"
    with urllib.request.urlopen(url_reg, timeout=10) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert data.get("status") == "success"
        assert "window" in data
        assert "fruits" in data

    # Mirage
    url_mir = f"{running_api_server}/stock/mirage"
    with urllib.request.urlopen(url_mir, timeout=10) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert data.get("status") == "success"
        assert "window" in data
        assert "fruits" in data


def test_api_countdown(running_api_server):
    url = f"{running_api_server}/countdown"
    with urllib.request.urlopen(url, timeout=10) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert data.get("status") == "success"
        assert "normal" in data
        assert "mirage" in data


def test_api_fruits_catalog(running_api_server):
    url = f"{running_api_server}/fruits"
    with urllib.request.urlopen(url, timeout=5) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert data.get("status") == "success"
        assert data.get("count") > 20
        assert len(data.get("fruits")) > 20


def test_api_single_fruit(running_api_server):
    url = f"{running_api_server}/fruit/Kitsune"
    with urllib.request.urlopen(url, timeout=10) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert data.get("status") == "success"
        assert data["fruit"]["name"] == "Kitsune"
        assert data["fruit"]["rarity"] == "Mythical"
        assert data["fruit"]["beli_price"] == 8000000


def test_api_404(running_api_server):
    url = f"{running_api_server}/nonexistent_endpoint"
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        urllib.request.urlopen(url, timeout=5)
    assert exc_info.value.code == 404
