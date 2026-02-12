from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from scraper import SearchService

ROOT = Path(__file__).parent
search_service = SearchService()


class Handler(BaseHTTPRequestHandler):
    def _send(self, body: bytes, status: int = 200, content_type: str = "text/html; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/":
            html = (ROOT / "templates" / "index.html").read_bytes()
            self._send(html)
            return

        if self.path == "/healthz":
            self._send(b'{"status":"ok"}', content_type="application/json")
            return

        if self.path.startswith("/static/"):
            file_path = ROOT / self.path.lstrip("/")
            if file_path.exists() and file_path.is_file():
                if file_path.suffix == ".css":
                    ctype = "text/css; charset=utf-8"
                elif file_path.suffix == ".js":
                    ctype = "application/javascript; charset=utf-8"
                else:
                    ctype = "application/octet-stream"
                self._send(file_path.read_bytes(), content_type=ctype)
                return

        self._send(b"Not Found", status=404, content_type="text/plain")

    def do_POST(self):
        if self.path != "/api/search":
            self._send(b"Not Found", status=404, content_type="text/plain")
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
        except json.JSONDecodeError:
            self._send(json.dumps({"error": "Invalid JSON"}).encode("utf-8"), status=400, content_type="application/json")
            return

        prompt = str(payload.get("prompt", "")).strip()
        if not prompt:
            self._send(json.dumps({"error": "Prompt is required."}).encode("utf-8"), status=400, content_type="application/json")
            return

        response = search_service.search(prompt)
        self._send(json.dumps(response).encode("utf-8"), content_type="application/json")


def run(host: str | None = None, port: int | None = None):
    bind_host = host or os.getenv("HOST", "0.0.0.0")
    bind_port = port if port is not None else int(os.getenv("PORT", "8000"))

    server = HTTPServer((bind_host, bind_port), Handler)
    print(f"Serving on http://{bind_host}:{bind_port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
