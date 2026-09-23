import json
import logging
import re
import time
import urllib.request
import urllib.error
import asyncio
from typing import Optional, Dict, Any

from config import STOCK_API_URL, STOCK_FALLBACK_URL
from models import StockSnapshot

logger = logging.getLogger("bloxfruits.stock_api")

# In-memory cache
_cached_snapshot: Optional[StockSnapshot] = None
_cache_timestamp: float = 0.0
CACHE_TTL_SECONDS = 45.0

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}


def _extract_balanced_json(text: str, start_brace_idx: int) -> Optional[str]:
    """Extracts a balanced JSON object string starting at start_brace_idx."""
    depth = 0
    in_str = False
    escape = False
    for i in range(start_brace_idx, len(text)):
        ch = text[i]
        if escape:
            escape = False
            continue
        if ch == '\\':
            escape = True
            continue
        if ch == '"':
            in_str = not in_str
            continue
        if not in_str:
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return text[start_brace_idx:i + 1]
    return None


def _extract_snapshot_from_html(html: str) -> Optional[Dict[str, Any]]:
    """Extracts the initialSnapshot JSON object from Next.js server rendered HTML."""
    # Method 1: Next.js RSC push chunk parsing
    pushes = re.findall(r'(?:self\.__next_f|\(self\.__next_f\s*=\s*self\.__next_f\s*\|\|\s*\[\]\))\.push\(\[(.*?)\]\)', html, re.DOTALL)
    for p in pushes:
        if "initialSnapshot" in p:
            try:
                parsed_push = json.loads(f"[{p}]")
                if len(parsed_push) > 1 and isinstance(parsed_push[1], str):
                    chunk_str = parsed_push[1]
                    for line in chunk_str.split('\n'):
                        if 'initialSnapshot' in line:
                            colon_idx = line.find(':')
                            data_json = line[colon_idx + 1:]
                            parsed_line = json.loads(data_json)
                            # React element structure: ["$", "$L...", null, props]
                            if isinstance(parsed_line, list) and len(parsed_line) > 3:
                                props = parsed_line[3]
                                if isinstance(props, dict) and "initialSnapshot" in props:
                                    return props["initialSnapshot"]
            except Exception as e:
                logger.debug("Error while decoding Next.js push chunk: %s", e)
                continue

    # Method 2: Balanced brace extraction from escaped Next.js streaming text
    snapshot_idx = html.find('initialSnapshot')
    if snapshot_idx != -1:
        brace_idx = html.find('{', snapshot_idx)
        if brace_idx != -1:
            raw_chunk = _extract_balanced_json(html, brace_idx)
            if raw_chunk:
                unescaped = raw_chunk.replace(r'\"', '"').replace(r'\\', '\\')
                try:
                    loaded = json.loads(unescaped)
                    if isinstance(loaded, dict) and ("normal" in loaded or "mirage" in loaded):
                        return loaded
                except Exception as e:
                    logger.debug("Fallback balanced-brace JSON decode error: %s", e)

    return None


def fetch_from_api_endpoint(url: str, timeout: float = 8.0) -> Optional[Dict[str, Any]]:
    """Attempts to fetch stock JSON directly from an API endpoint."""
    try:
        req = urllib.request.Request(
            url,
            headers={**HEADERS, "Accept": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            content_type = resp.headers.get("Content-Type", "")
            data = resp.read().decode("utf-8", errors="ignore")
            if "application/json" in content_type or data.strip().startswith("{"):
                loaded = json.loads(data)
                # Verify that it has normal and mirage keys
                if "normal" in loaded or "mirage" in loaded or "fruits" in loaded:
                    return loaded
    except Exception as e:
        logger.debug("Direct API request to %s failed: %s", url, e)
    return None


def fetch_from_fallback_page(url: str, timeout: float = 12.0) -> Optional[Dict[str, Any]]:
    """Fetches the live stock page and extracts the embedded React snapshot."""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            return _extract_snapshot_from_html(html)
    except Exception as e:
        logger.error("Failed to fetch fallback page from %s: %s", url, e)
    return None


def fetch_stock_sync(force_refresh: bool = False) -> StockSnapshot:
    """
    Synchronously fetches the latest Blox Fruits stock snapshot.
    Uses caching, direct API attempt, and webpage snapshot extraction fallback.
    """
    global _cached_snapshot, _cache_timestamp

    now = time.time()
    if not force_refresh and _cached_snapshot is not None and (now - _cache_timestamp) < CACHE_TTL_SECONDS:
        return _cached_snapshot

    raw_data: Optional[Dict[str, Any]] = None

    # Step 1: Try user-specified API URL
    if STOCK_API_URL:
        logger.info("Attempting to fetch stock from API endpoint: %s", STOCK_API_URL)
        raw_data = fetch_from_api_endpoint(STOCK_API_URL)

    # Step 2: If API URL failed or is unavailable, fallback to main website scraper
    if raw_data is None and STOCK_FALLBACK_URL:
        logger.info("Fetching stock from web tracker fallback: %s", STOCK_FALLBACK_URL)
        raw_data = fetch_from_fallback_page(STOCK_FALLBACK_URL)

    if raw_data is not None:
        snapshot = StockSnapshot.from_raw_snapshot(raw_data)
        _cached_snapshot = snapshot
        _cache_timestamp = now
        logger.info(
            "Stock snapshot refreshed: %d regular fruits, %d mirage fruits",
            len(snapshot.normal_fruits),
            len(snapshot.mirage_fruits)
        )
        return snapshot

    # If both failed, return existing cached snapshot if present
    if _cached_snapshot is not None:
        logger.warning("Fetch failed, returning expired cached snapshot")
        return _cached_snapshot

    raise RuntimeError("Failed to fetch stock from both API and fallback scraper.")


async def fetch_stock_async(force_refresh: bool = False) -> StockSnapshot:
    """Asynchronous wrapper for fetch_stock_sync running in a background thread."""
    return await asyncio.to_thread(fetch_stock_sync, force_refresh)
