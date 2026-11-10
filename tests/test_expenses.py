"""Isolated API and real CLI regression tests for the Daily Expense Tracker."""

from __future__ import annotations

from contextlib import closing
from datetime import date
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from expenses import ExpenseError, ExpenseTracker, format_amount


class ExpenseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.database = Path(self.directory.name) / "expenses.sqlite3"
        self.tracker = ExpenseTracker(self.database)

    def test_add_and_persist_across_instances(self) -> None:
        expense = self.tracker.add("12.34", " Food ", " Lunch ", "2026-11-10")
        self.assertEqual(expense.id, 1)
        self.assertEqual(expense.amount_cents, 1234)
        self.assertEqual(expense.category, "food")
        self.assertEqual(expense.description, "Lunch")
        self.assertEqual(ExpenseTracker(self.database).view(), [expense])

    def test_default_date_and_date_id_order(self) -> None:
        today = self.tracker.add("1", "food", "Today")
        self.assertEqual(today.date, date.today().isoformat())
        older = self.tracker.add("1", "food", "Older", "2000-01-01")
        same_day = self.tracker.add("2", "food", "Same day", "2000-01-01")
        self.assertEqual(self.tracker.view(), [older, same_day, today])

    def test_exact_totals_and_category_filter(self) -> None:
        first = self.tracker.add("0.10", " Food ", "One")
        second = self.tracker.add("0.20", "FOOD", "Two")
        self.tracker.add("3.45", "Travel", "Bus")
        self.assertEqual(self.tracker.view(" fOoD "), [first, second])
        self.assertEqual(self.tracker.total("FOOD"), 30)
        self.assertEqual(self.tracker.total(), 375)
        self.assertEqual(format_amount(self.tracker.total("FOOD")), "0.30")
        self.assertEqual(self.tracker.view("missing"), [])
        self.assertEqual(self.tracker.total("missing"), 0)

    def test_unicode_category_and_sql_parameters(self) -> None:
        expense = self.tracker.add("1", "Straße", "User's lunch")
        self.assertEqual(self.tracker.view("STRASSE"), [expense])
        unusual = self.tracker.add("2", "food' OR 1=1 --", "SQL text")
        self.assertEqual(self.tracker.view("food' OR 1=1 --"), [unusual])
        self.assertEqual(self.tracker.view("other' OR 1=1 --"), [])

    def test_update_each_field_and_preserve_unspecified(self) -> None:
        expense = self.tracker.add("10", "Food", "Lunch", "2026-01-01")
        updated = self.tracker.update(expense.id, amount="20.01")
        self.assertEqual(updated.amount_cents, 2001)
        self.assertEqual(updated.description, expense.description)
        updated = self.tracker.update(
            expense.id, category=" Travel ", description=" Train ", date="2026-02-28",
        )
        self.assertEqual(updated.id, expense.id)
        self.assertEqual(updated.amount_cents, 2001)
        self.assertEqual((updated.category, updated.description, updated.date),
                         ("travel", "Train", "2026-02-28"))
        self.assertEqual(self.tracker.total("food"), 0)
        self.assertEqual(self.tracker.total("travel"), 2001)
        self.assertEqual(ExpenseTracker(self.database).view(), [updated])

    def test_delete_persists_and_ids_are_not_reused(self) -> None:
        expense = self.tracker.add("1", "food", "First")
        self.tracker.delete(expense.id)
        self.assertEqual(ExpenseTracker(self.database).view(), [])
        self.assertEqual(self.tracker.total(), 0)
        another = self.tracker.add("2", "food", "Second")
        self.assertGreater(another.id, expense.id)

    def test_empty_tracker(self) -> None:
        self.assertEqual(self.tracker.view(), [])
        self.assertEqual(self.tracker.total(), 0)
        self.assertEqual(format_amount(0), "0.00")

    def test_amount_validation_and_boundary(self) -> None:
        for value in ("0", "0.00", "-1", "1.001", "NaN", "Infinity", "1e2",
                      "1,00", "", " 1", "1 ", ".50", "1.", "+1", "１２",
                      "1000000000", "9" * 100, None, 1.2):
            with self.subTest(value=value), self.assertRaises(ExpenseError):
                self.tracker.add(value, "food", "Invalid")
        self.assertEqual(self.tracker.view(), [])
        self.tracker.add("999999999.99", "food", "Maximum")
        self.tracker.add("0.01", "food", "Minimum")
        self.assertEqual(self.tracker.total(), 100000000000)
        self.assertEqual(format_amount(self.tracker.total()), "1000000000.00")

    def test_date_validation_and_leap_day(self) -> None:
        for value in ("2026-02-29", "2026-13-01", "2026-01-32", "20261110",
                      "2026-W46-2", "2026-1-01", "", "today", "2026-11-10T12:00:00", 1):
            with self.subTest(value=value), self.assertRaises(ExpenseError):
                self.tracker.add("1", "food", "Invalid", value)
        expense = self.tracker.add("1", "food", "Leap", "2024-02-29")
        self.assertEqual(expense.date, "2024-02-29")

    def test_text_validation(self) -> None:
        for field, values in (
            ("category", ("", " ", "a" * 81, "food\ntravel", "\x1b", None)),
            ("description", ("", " ", "a" * 501, "hello\tworld", None)),
        ):
            for value in values:
                inputs = {"amount": "1", "category": "food", "description": "Lunch"}
                inputs[field] = value
                with self.subTest(field=field, value=value), self.assertRaises(ExpenseError):
                    self.tracker.add(**inputs)
        with self.assertRaises(ExpenseError):
            self.tracker.view(" ")
        with self.assertRaises(ExpenseError):
            self.tracker.total("")
        self.assertEqual(self.tracker.view(), [])

    def test_invalid_update_is_atomic(self) -> None:
        expense = self.tracker.add("1", "food", "Lunch")
        for fields in ({}, {"amount": "0"}, {"category": ""}, {"description": ""},
                       {"amount": "2", "date": "invalid"}):
            with self.subTest(fields=fields), self.assertRaises(ExpenseError):
                self.tracker.update(expense.id, **fields)
            self.assertEqual(self.tracker.view(), [expense])

    def test_missing_and_invalid_ids(self) -> None:
        expense = self.tracker.add("1", "food", "Lunch")
        for identifier in (0, -1, True, 1.5, "1", 2**63, 999):
            with self.subTest(identifier=identifier):
                with self.assertRaises(ExpenseError):
                    self.tracker.update(identifier, amount="2")
                with self.assertRaises(ExpenseError):
                    self.tracker.delete(identifier)
        self.assertEqual(self.tracker.view(), [expense])

    def test_format_rejects_non_integer_or_negative(self) -> None:
        for value in (-1, 0.1, "100", True):
            with self.subTest(value=value), self.assertRaises(ExpenseError):
                format_amount(value)

    def test_database_errors_surface(self) -> None:
        with self.assertRaises(sqlite3.Error):
            ExpenseTracker(Path(self.directory.name) / "missing" / "data.sqlite3")
        damaged = Path(self.directory.name) / "damaged.sqlite3"
        damaged.write_text("not a database", encoding="utf-8")
        with self.assertRaises(sqlite3.Error):
            ExpenseTracker(damaged)
        with closing(sqlite3.connect(self.database)) as connection:
            with connection:
                connection.execute("DROP TABLE expenses")
        for operation in (self.tracker.view, self.tracker.total,
                          lambda: self.tracker.add("1", "food", "Lunch"),
                          lambda: self.tracker.update(1, amount="2"),
                          lambda: self.tracker.delete(1)):
            with self.assertRaises(sqlite3.Error):
                operation()

    def cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(ROOT / "src" / "expenses.py"),
             "--database", str(self.database), *args],
            capture_output=True, text=True, timeout=10,
        )

    def test_real_cli_crud_filter_totals_and_persistence(self) -> None:
        result = self.cli("add", "--amount", "0.10", "--category", "Food",
                          "--description", "Lunch", "--date", "2026-11-10")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Added\t1\t2026-11-10\tfood\t0.10\tLunch", result.stdout)
        self.assertEqual(self.cli("add", "--amount", "0.20", "--category", "food",
                                  "--description", "Snack").returncode, 0)
        result = self.cli("view", "--category", "FOOD")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Lunch", result.stdout)
        self.assertIn("Snack", result.stdout)
        self.assertEqual(self.cli("total", "--category", "food").stdout, "Total: 0.30\n")
        result = self.cli("update", "1", "--amount", "1.20", "--category", "Travel",
                          "--description", "Bus", "--date", "2026-11-09")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Updated\t1\t2026-11-09\ttravel\t1.20\tBus", result.stdout)
        self.assertEqual(self.cli("total").stdout, "Total: 1.40\n")
        self.assertEqual(self.cli("delete", "1").stdout, "Deleted expense 1\n")
        self.assertEqual(self.cli("total").stdout, "Total: 0.20\n")
        self.assertIn("No expenses found.", self.cli("view", "--category", "travel").stdout)
        self.assertEqual(self.cli("total", "--category", "travel").stdout, "Total: 0.00\n")

    def test_real_cli_failures_are_explicit(self) -> None:
        for args in (
            ("add", "--amount", "0", "--category", "food", "--description", "Bad"),
            ("add", "--amount", "1"),
            ("update", "1"),
            ("update", "999", "--amount", "1"),
            ("delete", "999"),
            ("delete", "not-an-id"),
            ("view", "--category", ""),
            ("total", "--category", ""),
            ("unknown",),
        ):
            with self.subTest(args=args):
                result = self.cli(*args)
                self.assertEqual(result.returncode, 2)
                self.assertTrue(result.stderr)
                self.assertEqual(result.stdout, "")
        self.assertEqual(self.tracker.view(), [])

    def test_real_cli_database_failure_and_help(self) -> None:
        self.database = Path(self.directory.name) / "missing" / "data.sqlite3"
        result = self.cli("view")
        self.assertEqual(result.returncode, 2)
        self.assertIn("ERROR:", result.stderr)
        self.assertEqual(result.stdout, "")
        result = self.cli("--help")
        self.assertEqual(result.returncode, 0)
        for command in ("add", "view", "update", "delete", "total", "--database"):
            self.assertIn(command, result.stdout)


if __name__ == "__main__":
    unittest.main()
