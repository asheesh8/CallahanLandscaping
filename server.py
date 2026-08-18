#!/usr/bin/env python3
"""
Callahan Landscaping — dev/static server + quote endpoint.

Standard library only, no dependencies, no framework. The site itself is a plain
static bundle: index.html + assets/ + media/. This server exists only to (a) serve
it with byte-range support so Safari will play the videos, and (b) accept the quote
form. Drop the static files on any host and the page still works — the form falls
back to a normal POST, and you can point its action at whatever handler you like.

    python3 server.py [--port 8000] [--host 127.0.0.1]

Submissions are appended as JSON Lines to data/quotes.jsonl.
"""

import argparse
import json
import os
import re
import sys
import time
from collections import defaultdict, deque
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, "data")
STORE = os.path.join(DATA_DIR, "quotes.jsonl")

MAX_BODY = 64 * 1024          # plenty for a contact form, small enough to be safe
RATE_MAX = 5                  # submissions ...
RATE_WINDOW = 600             # ... per IP per 10 minutes
_hits = defaultdict(deque)

FIELDS = {"name": 120, "contact": 160, "address": 200, "message": 2000}


def _clean(value, limit):
    """Collapse whitespace, strip control characters, enforce a length cap."""
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", str(value or ""))
    return re.sub(r"[ \t]+", " ", text).strip()[:limit]


def _rate_limited(ip):
    now = time.time()
    q = _hits[ip]
    while q and now - q[0] > RATE_WINDOW:
        q.popleft()
    if len(q) >= RATE_MAX:
        return True
    q.append(now)
    return False


def _persist(record):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(STORE, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


THANKS = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Thanks — Callahan Landscaping</title><link rel="stylesheet" href="/assets/css/site.css">
</head><body><main class="band"><div class="wrap wrap-narrow">
<p class="label">Quote request</p><h1 class="h2">Got it.</h1>
<p class="lede">Thanks — we have your details and will be in touch.</p>
<p><a class="btn btn-accent" href="/">Back to the site</a></p>
</div></main></body></html>"""


class Handler(SimpleHTTPRequestHandler):
    server_version = "callahan/1.0"
    extensions_map = {
        **SimpleHTTPRequestHandler.extensions_map,
        ".webp": "image/webp",
        ".mp4": "video/mp4",
        ".js": "text/javascript",
        ".css": "text/css",
    }

    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def log_message(self, fmt, *args):
        sys.stderr.write("  %s\n" % (fmt % args))

    # ---- static ---------------------------------------------------------
    def end_headers(self):
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        super().end_headers()

    def do_GET(self):
        if urlparse(self.path).path == "/api/health":
            return self._json(200, {"ok": True})
        if "Range" in self.headers:
            return self._ranged()
        return super().do_GET()

    def _ranged(self):
        """Minimal single-range support — Safari refuses to play video without it."""
        path = self.translate_path(self.path)
        if not os.path.isfile(path):
            return super().do_GET()
        size = os.path.getsize(path)
        m = re.match(r"bytes=(\d*)-(\d*)", self.headers.get("Range", ""))
        if not m:
            return super().do_GET()
        start_s, end_s = m.groups()
        if start_s == "":                              # suffix range: last N bytes
            length = min(int(end_s or 0), size)
            start, end = size - length, size - 1
        else:
            start = int(start_s)
            end = int(end_s) if end_s else size - 1
        if start >= size or start > end:
            self.send_response(416)
            self.send_header("Content-Range", "bytes */%d" % size)
            self.end_headers()
            return
        end = min(end, size - 1)
        self.send_response(206)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Range", "bytes %d-%d/%d" % (start, end, size))
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        remaining = end - start + 1
        with open(path, "rb") as fh:
            fh.seek(start)
            while remaining > 0:
                chunk = fh.read(min(64 * 1024, remaining))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    return
                remaining -= len(chunk)

    # ---- quote endpoint -------------------------------------------------
    def do_POST(self):
        if urlparse(self.path).path != "/api/quote":
            return self._reply(404, {"error": "Not found."})

        wants_json = "application/json" in (self.headers.get("Accept", "") or "") or \
                     "application/json" in (self.headers.get("Content-Type", "") or "")

        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length <= 0 or length > MAX_BODY:
            return self._reply(413, {"error": "That message is too large."}, wants_json)

        raw = self.rfile.read(length).decode("utf-8", "replace")
        ctype = self.headers.get("Content-Type", "")
        if "application/json" in ctype:
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                return self._reply(400, {"error": "Could not read that."}, wants_json)
        else:
            payload = {k: v[0] for k, v in parse_qs(raw).items()}

        if _clean(payload.get("website"), 80):          # honeypot
            return self._reply(200, {"ok": True}, wants_json)   # look successful, drop it

        ip = self.headers.get("X-Forwarded-For", self.client_address[0]).split(",")[0].strip()
        if _rate_limited(ip):
            return self._reply(429, {"error": "Too many requests — try again shortly."}, wants_json)

        record = {k: _clean(payload.get(k), limit) for k, limit in FIELDS.items()}
        if not record["name"] or not record["contact"]:
            return self._reply(400, {"error": "Name and a way to reach you are both required."}, wants_json)

        record["received_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        record["ip"] = ip
        try:
            _persist(record)
        except OSError as exc:
            self.log_message("persist failed: %s", exc)
            return self._reply(500, {"error": "Could not save that. Please call instead."}, wants_json)

        self.log_message("quote from %s <%s>", record["name"], record["contact"])
        return self._reply(200, {"ok": True}, wants_json)

    # ---- helpers --------------------------------------------------------
    def _reply(self, code, body, wants_json=True):
        if wants_json:
            return self._json(code, body)
        if code == 200:
            data = THANKS.encode("utf-8")
            self.send_response(200)
        else:
            data = ("<!doctype html><meta charset=utf-8><p>%s</p><p><a href='/#quote'>Go back</a></p>"
                    % body.get("error", "Error")).encode("utf-8")
            self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json(self, code, body):
        data = json.dumps(body).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--host", default="127.0.0.1")
    args = ap.parse_args()

    os.makedirs(DATA_DIR, exist_ok=True)
    srv = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Callahan Landscaping  ->  http://{args.host}:{args.port}")
    print(f"quotes append to      ->  {STORE}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
        srv.server_close()


if __name__ == "__main__":
    main()
