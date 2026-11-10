"""Local expense website and JSON API backed by the existing SQLite service.

Run python src\\web.py and open http://127.0.0.1:8000. This loopback-only server
is for personal local use, not public deployment or multi-user authentication.
GET /api/expenses accepts optional month (YYYY-MM) and category filters.
POST /api/expenses creates; PUT and DELETE /api/expenses/{id} mutate a record.
Mutation requests require JSON and X-Expense-Request: 1. Amounts, cents and IDs
are decimal strings in JSON to preserve precision in browser JavaScript.
"""

from __future__ import annotations

import argparse
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import sqlite3
import sys
from urllib.parse import parse_qs, urlsplit

from expenses import DEFAULT_DATABASE, Expense, ExpenseError, ExpenseTracker, _category, format_amount

STATIC_ROOT = Path(__file__).resolve().parent / "static"
MAX_BODY = 65_536


def expense_json(expense: Expense) -> dict[str, str]:
    """Serialize a persisted record without lossy JavaScript integers."""
    return {
        "id": str(expense.id), "amount_cents": str(expense.amount_cents),
        "amount": format_amount(expense.amount_cents), "category": expense.category,
        "description": expense.description, "date": expense.date,
    }


def dashboard(tracker: ExpenseTracker, month: str | None, category: str | None) -> dict[str, object]:
    """Build exact filtered totals and chart series from one persisted snapshot."""
    if month is not None:
        if not re.fullmatch(r"[0-9]{4}-[0-9]{2}", month):
            raise ExpenseError("month must be YYYY-MM")
        try:
            date.fromisoformat(month + "-01")
        except ValueError as error:
            raise ExpenseError("month must be a valid YYYY-MM") from error
    records = tracker.view()
    categories = sorted({item.category for item in records})
    if category is not None:
        # Reuse the service's complete Unicode and printable-text validation.
        key = _category(category)
        records = [item for item in records if item.category == key]
    if month is not None:
        records = [item for item in records if item.date.startswith(month + "-")]
    by_category: dict[str, int] = {}
    by_day: dict[str, int] = {}
    for item in records:
        by_category[item.category] = by_category.get(item.category, 0) + item.amount_cents
        by_day[item.date] = by_day.get(item.date, 0) + item.amount_cents
    total = sum(item.amount_cents for item in records)
    return {
        "expenses": [expense_json(item) for item in records],
        "categories": categories,
        "summary": {
            "total_cents": str(total), "total": format_amount(total),
            "count": len(records), "category_count": len(by_category),
            "by_category": [
                {"category": key, "amount_cents": str(value), "amount": format_amount(value)}
                for key, value in sorted(by_category.items())
            ],
            "by_day": [
                {"date": key, "amount_cents": str(value), "amount": format_amount(value)}
                for key, value in sorted(by_day.items())
            ],
        },
    }


class ExpenseServer(ThreadingHTTPServer):
    """Serve loopback requests using the unchanged expense service."""

    daemon_threads = True

    def __init__(self, database: Path = DEFAULT_DATABASE, port: int = 8000) -> None:
        """Validate/open SQLite before binding the loopback HTTP listener."""
        self.tracker = ExpenseTracker(database)
        super().__init__(("127.0.0.1", port), ExpenseHandler)


class ExpenseHandler(BaseHTTPRequestHandler):
    """Handle a small allowlisted static website and same-origin JSON API."""

    server: ExpenseServer

    def setup(self) -> None:
        """Bound request socket reads to avoid indefinitely blocked clients."""
        super().setup()
        self.connection.settimeout(10)

    def _send(self, status: int, content: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy",
                         "default-src 'self'; script-src 'self'; style-src 'self'; "
                         "img-src 'self' data:; connect-src 'self'; "
                         "object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(content)

    def _json(self, status: int, payload: object) -> None:
        self._send(status, json.dumps(payload, ensure_ascii=True).encode("utf-8"),
                   "application/json; charset=utf-8")

    def _trusted(self) -> bool:
        port = self.server.server_port
        origins = {f"http://127.0.0.1:{port}", f"http://localhost:{port}"}
        host = self.headers.get("Host", "")
        origin = self.headers.get("Origin")
        if f"http://{host}" not in origins or (origin is not None and origin != f"http://{host}"):
            self._json(403, {"error": "Only same-origin loopback requests are allowed"})
            return False
        if self.command in ("POST", "PUT", "DELETE") and self.headers.get("X-Expense-Request") != "1":
            self._json(403, {"error": "X-Expense-Request: 1 is required"})
            return False
        return True

    def _body(self) -> dict[str, str]:
        length = self.headers.get("Content-Length", "")
        if self.headers.get("Transfer-Encoding") or not re.fullmatch(r"[0-9]{1,6}", length):
            raise ExpenseError("a valid Content-Length is required")
        count = int(length)
        if count > MAX_BODY:
            # Drain the bounded declared body so Windows can deliver the error before closing.
            remaining = count
            while remaining:
                chunk = self.rfile.read(min(remaining, 8192))
                if not chunk:
                    break
                remaining -= len(chunk)
            raise ExpenseError("JSON request must contain 1 to 65536 bytes")
        if count == 0:
            raise ExpenseError("JSON request must contain 1 to 65536 bytes")
        raw = self.rfile.read(count)
        if len(raw) != count:
            raise ExpenseError("incomplete JSON request")
        if self.headers.get_content_type() != "application/json":
            raise ExpenseError("request Content-Type must be application/json")
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeError) as error:
            raise ExpenseError("request must contain valid UTF-8 JSON") from error
        allowed = {"amount", "category", "description", "date"}
        if not isinstance(payload, dict) or set(payload) - allowed:
            raise ExpenseError("JSON must be an object containing only expense fields")
        if any(not isinstance(value, str) for value in payload.values()):
            raise ExpenseError("expense fields must be strings")
        return payload

    def _handle(self) -> None:
        if not self._trusted():
            return
        try:
            url = urlsplit(self.path)
            path = url.path
            if self.command in ("GET", "HEAD") and path == "/api/expenses":
                query = parse_qs(url.query, keep_blank_values=True, max_num_fields=4)
                if set(query) - {"month", "category"} or any(len(values) != 1 for values in query.values()):
                    raise ExpenseError("only one month and category filter may be supplied")
                self._json(200, dashboard(self.server.tracker,
                                         query.get("month", [None])[0],
                                         query.get("category", [None])[0]))
                return
            if self.command == "POST" and path == "/api/expenses" and not url.query:
                body = self._body()
                if not {"amount", "category", "description"} <= body.keys():
                    raise ExpenseError("amount, category and description are required")
                self._json(201, {"expense": expense_json(self.server.tracker.add(**body))})
                return
            match = re.fullmatch(r"/api/expenses/([1-9][0-9]{0,18})", path)
            if match and not url.query and self.command in ("PUT", "DELETE"):
                identifier = int(match.group(1))
                try:
                    if self.command == "PUT":
                        result = self.server.tracker.update(identifier, **self._body())
                        self._json(200, {"expense": expense_json(result)})
                    else:
                        self.server.tracker.delete(identifier)
                        self._json(200, {"deleted": str(identifier)})
                except ExpenseError as error:
                    if str(error) == f"expense {identifier} not found":
                        self._json(404, {"error": str(error)})
                    else:
                        raise
                return
            static = {
                "/": ("index.html", "text/html; charset=utf-8"),
                "/index.html": ("index.html", "text/html; charset=utf-8"),
                "/styles.css": ("styles.css", "text/css; charset=utf-8"),
                "/app.js": ("app.js", "text/javascript; charset=utf-8"),
            }
            if self.command in ("GET", "HEAD") and path in static:
                name, content_type = static[path]
                target = STATIC_ROOT / name
                if STATIC_ROOT.is_symlink() or target.is_symlink() or not target.is_file():
                    raise OSError("Static asset missing or unsafe")
                self._send(200, target.read_bytes(), content_type)
            elif path == "/api/expenses" or match:
                self._json(405, {"error": "Method not allowed for this endpoint"})
            else:
                self._json(404, {"error": "Not found"})
        except (ExpenseError, ValueError) as error:
            self._json(400, {"error": str(error)})
        except (sqlite3.Error, OSError) as error:
            self.log_error("Expense service unavailable: %s", error)
            self._json(503, {"error": "Local storage or website unavailable; check the server log"})

    def do_GET(self) -> None:
        """Return the dashboard assets or filtered expense collection."""
        self._handle()

    def do_HEAD(self) -> None:
        """Return GET response headers without a body."""
        self._handle()

    def do_POST(self) -> None:
        """Create a validated expense from JSON."""
        self._handle()

    def do_PUT(self) -> None:
        """Update supplied expense fields without changing its ID."""
        self._handle()

    def do_DELETE(self) -> None:
        """Delete a persisted expense by ID."""
        self._handle()


def main(argv: list[str] | None = None) -> int:
    """Run the local website until Ctrl+C; report startup failures explicitly."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)
    if not 1 <= args.port <= 65535:
        parser.error("port must be between 1 and 65535")
    try:
        with ExpenseServer(args.database, args.port) as server:
            print(f"Expense Tracker: http://127.0.0.1:{server.server_port}", flush=True)
            server.serve_forever()
    except KeyboardInterrupt:
        return 0
    except (ExpenseError, sqlite3.Error, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
