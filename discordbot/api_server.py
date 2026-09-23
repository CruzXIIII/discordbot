import json
import logging
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import threading
import urllib.parse
from typing import Optional
from config import API_HOST, API_PORT
import stock_api
from fruit_catalog import get_fruit_by_name, get_all_catalog_fruits

logger = logging.getLogger("bloxfruits.api_server")


class StockApiHandler(BaseHTTPRequestHandler):
    def _send_json_response(self, status_code: int, data: dict):
        response_bytes = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response_bytes)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.end_headers()
        self.wfile.write(response_bytes)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        clean_path = self.path.split("?")[0].rstrip("/")
        if clean_path in ("", "/stock", "/api/stock"):
            try:
                snapshot = stock_api.fetch_stock_sync(force_refresh=False)
                payload = {
                    "status": "success",
                    "source": "bloxfruitsvalues",
                    "data": snapshot.to_dict(),
                }
                self._send_json_response(200, payload)
            except Exception as e:
                logger.error("Error generating stock API response: %s", e)
                self._send_json_response(500, {"status": "error", "message": str(e)})

        elif clean_path in ("/stock/regular", "/stock/normal"):
            try:
                snapshot = stock_api.fetch_stock_sync(force_refresh=False)
                self._send_json_response(200, {
                    "status": "success",
                    "window": snapshot.normal_window.to_dict(),
                    "fruits": [f.to_dict() for f in snapshot.normal_fruits],
                })
            except Exception as e:
                self._send_json_response(500, {"status": "error", "message": str(e)})

        elif clean_path in ("/stock/mirage",):
            try:
                snapshot = stock_api.fetch_stock_sync(force_refresh=False)
                self._send_json_response(200, {
                    "status": "success",
                    "window": snapshot.mirage_window.to_dict(),
                    "fruits": [f.to_dict() for f in snapshot.mirage_fruits],
                })
            except Exception as e:
                self._send_json_response(500, {"status": "error", "message": str(e)})

        elif clean_path in ("/countdown", "/timers"):
            try:
                snapshot = stock_api.fetch_stock_sync(force_refresh=False)
                self._send_json_response(200, {
                    "status": "success",
                    "normal": snapshot.normal_window.to_dict(),
                    "mirage": snapshot.mirage_window.to_dict(),
                })
            except Exception as e:
                self._send_json_response(500, {"status": "error", "message": str(e)})

        elif clean_path in ("/fruits", "/catalog"):
            fruits = [f.to_dict() for f in get_all_catalog_fruits()]
            self._send_json_response(200, {
                "status": "success",
                "count": len(fruits),
                "fruits": fruits,
            })

        elif clean_path.startswith("/fruit/"):
            raw_name = clean_path[len("/fruit/"):]
            fruit_name = urllib.parse.unquote(raw_name)
            try:
                snapshot = stock_api.fetch_stock_sync(force_refresh=False)
                target = snapshot.find_fruit(fruit_name)
                in_normal = False
                in_mirage = False
                if target:
                    in_normal = any(f.name.lower() == target.name.lower() for f in snapshot.normal_fruits)
                    in_mirage = any(f.name.lower() == target.name.lower() for f in snapshot.mirage_fruits)
                else:
                    target = get_fruit_by_name(fruit_name)

                if target:
                    data = target.to_dict()
                    data["in_normal_stock"] = in_normal
                    data["in_mirage_stock"] = in_mirage
                    self._send_json_response(200, {"status": "success", "fruit": data})
                else:
                    self._send_json_response(404, {"status": "error", "message": f"Fruit '{fruit_name}' not found."})
            except Exception as e:
                self._send_json_response(500, {"status": "error", "message": str(e)})

        elif clean_path in ("/health", "/ping"):
            self._send_json_response(200, {"status": "ok", "service": "BloxFruitsStockAPI"})

        else:
            self._send_json_response(404, {"status": "error", "message": "Endpoint not found"})

    def log_message(self, format, *args):
        # Silence default stderr spam and route through logger
        logger.debug("%s - - [%s] %s", self.address_string(), self.log_date_time_string(), format % args)


class StockApiServer:
    def __init__(self, host: str = API_HOST, port: int = API_PORT):
        self.host = host
        self.port = port
        self.server: Optional[ThreadingHTTPServer] = None
        self.thread: Optional[threading.Thread] = None

    def start(self):
        try:
            self.server = ThreadingHTTPServer((self.host, self.port), StockApiHandler)
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            logger.info("Stock REST API server listening at http://%s:%d/stock", self.host, self.port)
        except Exception as e:
            logger.error("Failed to start REST API server on %s:%d: %s", self.host, self.port, e)

    def stop(self):
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            logger.info("Stock REST API server stopped.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    srv = StockApiServer()
    srv.start()
    print(f"API server running on http://{API_HOST}:{API_PORT}/stock. Press Ctrl+C to stop.")
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        srv.stop()
