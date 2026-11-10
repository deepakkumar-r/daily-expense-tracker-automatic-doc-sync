"""Real loopback HTTP integration tests using isolated SQLite databases."""

from __future__ import annotations

from http.client import HTTPConnection
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import web
from expenses import ExpenseTracker


class WebTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.database = Path(self.temporary.name) / "expenses.sqlite3"
        self.server = web.ExpenseServer(self.database, 0)
        self.worker = threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.01})
        self.worker.start()
        self.addCleanup(self.stop_server)
        log_patch = patch.object(web.ExpenseHandler, "log_message")
        self.log = log_patch.start()
        self.addCleanup(log_patch.stop)

    def stop_server(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        self.worker.join(timeout=3)
        self.assertFalse(self.worker.is_alive())

    def request(self, method: str, path: str = "/api/expenses", data: object = None,
                headers: dict[str, str] | None = None, raw: bytes | None = None) -> tuple[int, object, dict[str, str]]:
        connection = HTTPConnection("127.0.0.1", self.server.server_port, timeout=3)
        try:
            body = json.dumps(data).encode("utf-8") if data is not None else raw
            request_headers = {"Content-Type": "application/json", "X-Expense-Request": "1"}
            request_headers.update(headers or {})
            connection.request(method, path, body=body, headers=request_headers)
            response = connection.getresponse()
            content = response.read()
            result = json.loads(content) if content and response.getheader("Content-Type", "").startswith("application/json") else content
            return response.status, result, dict(response.getheaders())
        finally:
            connection.close()

    def add(self, **fields: str) -> dict[str, str]:
        data = {"amount": "12.50", "category": "Food", "description": "Lunch", "date": "2026-11-10"}
        data.update(fields)
        status, result, _ = self.request("POST", data=data)
        self.assertEqual(status, 201, result)
        return result["expense"]

    def test_http_crud_persistence_and_existing_cli_share_service(self) -> None:
        record = self.add()
        identifier = record["id"]
        self.assertEqual(record["amount_cents"], "1250")
        self.assertEqual(ExpenseTracker(self.database).view()[0].id, int(identifier))
        status, data, _ = self.request("PUT", f"/api/expenses/{identifier}", {"amount": "0.30", "description": "Revised"})
        self.assertEqual(status, 200)
        self.assertEqual(data["expense"]["id"], identifier)
        self.assertEqual(data["expense"]["category"], "food")
        cli = subprocess.run(
            [sys.executable, str(Path(web.__file__).with_name("expenses.py")), "--database", str(self.database), "total"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual((cli.returncode, cli.stdout.strip()), (0, "Total: 0.30"), cli.stderr)
        self.assertEqual(self.request("DELETE", f"/api/expenses/{identifier}")[0], 200)
        self.assertEqual(self.request("GET")[1]["summary"]["total"], "0.00")
        self.assertGreater(int(self.add()["id"]), int(identifier))

    def test_month_category_filters_summary_and_charts_are_consistent(self) -> None:
        self.add(amount="0.10", category="Stra\u00dfe", date="2026-11-01")
        self.add(amount="0.20", category="STRASSE", date="2026-11-01")
        self.add(amount="2.00", category="Travel", date="2026-11-02")
        self.add(amount="9.00", date="2026-12-01")
        status, data, _ = self.request("GET", "/api/expenses?month=2026-11&category=%20STRASSE%20")
        self.assertEqual(status, 200)
        self.assertEqual([item["amount"] for item in data["expenses"]], ["0.10", "0.20"])
        self.assertEqual(data["categories"], ["food", "strasse", "travel"])
        self.assertEqual(data["summary"], {
            "total_cents": "30", "total": "0.30", "count": 2, "category_count": 1,
            "by_category": [{"category": "strasse", "amount_cents": "30", "amount": "0.30"}],
            "by_day": [{"date": "2026-11-01", "amount_cents": "30", "amount": "0.30"}],
        })
        self.assertEqual(self.request("GET", "/api/expenses?month=2026-11")[1]["summary"]["total"], "2.30")
        empty = self.request("GET", "/api/expenses?month=2025-01")[1]
        self.assertEqual((empty["expenses"], empty["summary"]["by_day"], empty["summary"]["total"]), ([], [], "0.00"))

    def test_precision_strings_and_never_execute_or_render_user_html(self) -> None:
        record = self.add(amount="999999999.99", description="<script>alert(1)</script>")
        self.assertEqual(record["amount_cents"], "99999999999")
        self.assertEqual(record["description"], "<script>alert(1)</script>")
        self.assertIsInstance(record["id"], str)
        self.assertIn("application/json", self.request("GET")[2]["Content-Type"])

    def test_invalid_inputs_are_explicit_and_never_mutate_existing_data(self) -> None:
        record = self.add()
        for data in ({}, {"amount": "0"}, {"amount": "-1"}, {"amount": "1e2"}, {"amount": "0.001"},
                     {"amount": 1.2}, {"amount": None}, {"date": "2026-02-30"},
                     {"category": " "}, {"description": ""}, {"unknown": "value"},
                     ["not", "an", "object"]):
            with self.subTest(data=data):
                self.assertEqual(self.request("PUT", f"/api/expenses/{record['id']}", data)[0], 400)
                self.assertEqual(self.request("GET")[1]["expenses"], [record])
        self.assertEqual(self.request("POST", data={"amount": "1"})[0], 400)
        for query in ("month=2026-13", "month=0000-01", "month=26-01", "month=", "category=",
                      "month=2026-11&month=2026-12", "unknown=1", "a=1&b=2&c=3&d=4&e=5"):
            self.assertEqual(self.request("GET", f"/api/expenses?{query}")[0], 400, query)
        self.assertEqual(self.request("PUT", "/api/expenses/9223372036854775808", {"amount": "1"})[0], 400)

    def test_missing_ids_and_wrong_routes(self) -> None:
        self.assertEqual(self.request("PUT", "/api/expenses/42", {"amount": "1"})[0], 404)
        self.assertEqual(self.request("DELETE", "/api/expenses/42")[0], 404)
        self.assertEqual(self.request("PUT", "/api/expenses", {"amount": "1"})[0], 405)
        self.assertEqual(self.request("GET", "/api/expenses/1")[0], 405)
        self.assertEqual(self.request("GET", "/missing")[0], 404)
        for path in ("/../demo.sqlite3", "/src/expenses.py", "/%2e%2e/demo.sqlite3", "/expenses.sqlite3"):
            self.assertEqual(self.request("GET", path)[0], 404)

    def test_static_assets_head_and_response_policy(self) -> None:
        for path, content_type in (("/", "text/html"), ("/styles.css", "text/css"), ("/app.js", "text/javascript")):
            status, body, headers = self.request("GET", path)
            self.assertEqual(status, 200)
            self.assertTrue(body)
            self.assertIn(content_type, headers["Content-Type"])
            self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
            self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])
        status, body, headers = self.request("HEAD", "/")
        self.assertEqual((status, body), (200, b""))
        self.assertGreater(int(headers["Content-Length"]), 0)
        self.assertEqual(self.request("GET", "/?ignored=1")[0], 200)

    def test_cross_origin_and_dns_rebinding_requests_are_rejected(self) -> None:
        for headers in ({"Host": "attacker.invalid"}, {"Origin": "https://attacker.invalid"},
                        {"Origin": "null"}, {"X-Expense-Request": ""}):
            self.assertEqual(self.request("POST", data={}, headers=headers)[0], 403)
        port = self.server.server_port
        self.assertEqual(self.request("GET", headers={"Host": f"localhost:{port}"})[0], 200)
        self.assertEqual(self.request("GET", headers={"Host": "attacker.invalid"})[0], 403)
        self.assertNotIn("Access-Control-Allow-Origin", self.request("GET")[2])

    def test_malformed_wrong_type_and_oversized_requests(self) -> None:
        for raw in (b"{bad", b"\xff", b"[]", b"null", '{"amount":"1"}'.encode("utf-16")):
            self.assertEqual(self.request("POST", raw=raw)[0], 400)
        self.assertEqual(self.request("POST", raw=b"{}", headers={"Content-Type": "text/plain"})[0], 400)
        self.assertEqual(self.request("POST", raw=b"x" * (web.MAX_BODY + 1))[0], 400)

    def test_database_failure_is_not_an_empty_success(self) -> None:
        with patch.object(self.server.tracker, "view", side_effect=sqlite3.OperationalError("locked")):
            status, data, _ = self.request("GET")
        self.assertEqual(status, 503)
        self.assertIn("unavailable", data["error"])
        self.log.assert_called()

    def test_static_symlinks_are_rejected(self) -> None:
        with patch.object(Path, "is_symlink", return_value=True):
            self.assertEqual(self.request("GET", "/app.js")[0], 503)


if __name__ == "__main__":
    unittest.main()
