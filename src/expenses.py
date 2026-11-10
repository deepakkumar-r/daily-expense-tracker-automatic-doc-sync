"""Daily Expense Tracker CLI with persistent SQLite storage and exact cent totals.

Run python src\\expenses.py --help for add, view, update, delete and total commands.
Amounts use a single user-chosen currency with two decimal places. Categories are
trimmed and casefolded; dates are ISO YYYY-MM-DD. No network services are used.
"""

from __future__ import annotations

import argparse
from contextlib import closing, contextmanager
from dataclasses import dataclass
from datetime import date as calendar_date
from decimal import Decimal
from pathlib import Path
import re
import sqlite3
import sys
from typing import Iterator

DEFAULT_DATABASE = Path(__file__).resolve().parent.parent / "expenses.sqlite3"


class ExpenseError(ValueError):
    """Signal invalid expense input or an expense ID that does not exist."""


def _text(value: str, field: str, limit: int) -> str:
    if not isinstance(value, str) or not value.strip() or len(value.strip()) > limit:
        raise ExpenseError(f"{field} must contain 1 to {limit} characters")
    result = value.strip()
    if any(not character.isprintable() for character in result):
        raise ExpenseError(f"{field} must contain printable characters only")
    return result


def _category(value: str) -> str:
    return _text(_text(value, "category", 80).casefold(), "category", 80)


def _amount_cents(value: str) -> int:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]+(?:\.[0-9]{1,2})?", value):
        raise ExpenseError("amount must be a positive decimal with at most two decimal places")
    amount = Decimal(value)
    if not 0 < amount <= Decimal("999999999.99"):
        raise ExpenseError("amount must be between 0.01 and 999999999.99")
    return int(amount * 100)


def _date(value: str) -> str:
    try:
        parsed = calendar_date.fromisoformat(value)
    except (TypeError, ValueError) as error:
        raise ExpenseError("date must be a valid YYYY-MM-DD calendar date") from error
    if parsed.isoformat() != value:
        raise ExpenseError("date must be a valid YYYY-MM-DD calendar date")
    return value


def _identifier(value: int) -> int:
    if type(value) is not int or not 1 <= value <= 9223372036854775807:
        raise ExpenseError("expense ID must be a positive SQLite integer")
    return value


def format_amount(cents: int) -> str:
    """Format nonnegative integer cents as a two-decimal currency-neutral amount."""
    if type(cents) is not int or cents < 0:
        raise ExpenseError("cents must be a nonnegative integer")
    return f"{cents // 100}.{cents % 100:02d}"


@dataclass(frozen=True)
class Expense:
    """Immutable persisted expense: ID, amount in cents, category, description, date."""

    id: int
    amount_cents: int
    category: str
    description: str
    date: str


class ExpenseTracker:
    """Manage a local SQLite expense file; methods raise on invalid or missing data."""

    def __init__(self, database: Path = DEFAULT_DATABASE) -> None:
        """Create the expense table if needed; surface database/open failures."""
        self.database = Path(database)
        with self._connection() as connection:
            connection.execute(
                """CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount_cents INTEGER NOT NULL
                        CHECK(amount_cents BETWEEN 1 AND 99999999999),
                    category TEXT NOT NULL CHECK(length(category) BETWEEN 1 AND 80),
                    description TEXT NOT NULL CHECK(length(description) BETWEEN 1 AND 500),
                    date TEXT NOT NULL
                )"""
            )

    @contextmanager
    def _connection(self) -> Iterator[sqlite3.Connection]:
        with closing(sqlite3.connect(self.database)) as connection:
            with connection:
                yield connection

    def add(
        self, amount: str, category: str, description: str, date: str | None = None,
    ) -> Expense:
        """Persist a positive decimal expense; omit date to use the local day."""
        cents = _amount_cents(amount)
        category = _category(category)
        description = _text(description, "description", 500)
        day = _date(date if date is not None else calendar_date.today().isoformat())
        with self._connection() as connection:
            cursor = connection.execute(
                "INSERT INTO expenses (amount_cents, category, description, date) VALUES (?, ?, ?, ?)",
                (cents, category, description, day),
            )
            identifier = cursor.lastrowid
            if identifier is None:
                raise ExpenseError("database did not assign an expense ID")
        return Expense(identifier, cents, category, description, day)

    def view(self, category: str | None = None) -> list[Expense]:
        """List expenses by date then ID, optionally matching a normalized category."""
        query = "SELECT id, amount_cents, category, description, date FROM expenses"
        parameters: tuple[str, ...] = ()
        if category is not None:
            query += " WHERE category = ?"
            parameters = (_category(category),)
        with self._connection() as connection:
            rows = connection.execute(query + " ORDER BY date, id", parameters).fetchall()
        return [Expense(*row) for row in rows]

    def update(
        self, expense_id: int, *, amount: str | None = None,
        category: str | None = None, description: str | None = None,
        date: str | None = None,
    ) -> Expense:
        """Update supplied fields atomically; reject missing IDs or an empty update."""
        identifier = _identifier(expense_id)
        fields: dict[str, int | str] = {}
        if amount is not None:
            fields["amount_cents"] = _amount_cents(amount)
        if category is not None:
            fields["category"] = _category(category)
        if description is not None:
            fields["description"] = _text(description, "description", 500)
        if date is not None:
            fields["date"] = _date(date)
        if not fields:
            raise ExpenseError("update requires at least one field")
        assignments = ", ".join(f"{column} = ?" for column in fields)
        with self._connection() as connection:
            cursor = connection.execute(
                f"UPDATE expenses SET {assignments} WHERE id = ?",
                (*fields.values(), identifier),
            )
            if cursor.rowcount != 1:
                raise ExpenseError(f"expense {identifier} not found")
            row = connection.execute(
                "SELECT id, amount_cents, category, description, date FROM expenses WHERE id = ?",
                (identifier,),
            ).fetchone()
            if row is None:
                raise ExpenseError(f"expense {identifier} not found")
            expense = Expense(*row)
        return expense

    def delete(self, expense_id: int) -> None:
        """Delete one expense by ID; raise ExpenseError if it does not exist."""
        identifier = _identifier(expense_id)
        with self._connection() as connection:
            cursor = connection.execute("DELETE FROM expenses WHERE id = ?", (identifier,))
            if cursor.rowcount != 1:
                raise ExpenseError(f"expense {identifier} not found")

    def total(self, category: str | None = None) -> int:
        """Return exact integer cents for all expenses or one normalized category."""
        return sum(expense.amount_cents for expense in self.view(category))


def _display(expense: Expense) -> str:
    return (
        f"{expense.id}\t{expense.date}\t{expense.category}\t"
        f"{format_amount(expense.amount_cents)}\t{expense.description}"
    )


def main(argv: list[str] | None = None) -> int:
    """Run the expense CLI; return 0 on success or 2 for input/database errors."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE, help="SQLite file path")
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add", help="add an expense")
    add.add_argument("--amount", required=True)
    add.add_argument("--category", required=True)
    add.add_argument("--description", required=True)
    add.add_argument("--date")
    view = commands.add_parser("view", help="list expenses by date then ID")
    view.add_argument("--category")
    update = commands.add_parser("update", help="update supplied fields")
    update.add_argument("id", type=int)
    for field in ("amount", "category", "description", "date"):
        update.add_argument(f"--{field}")
    delete = commands.add_parser("delete", help="delete an expense by ID")
    delete.add_argument("id", type=int)
    total = commands.add_parser("total", help="calculate an exact total")
    total.add_argument("--category")
    args = parser.parse_args(argv)
    try:
        tracker = ExpenseTracker(args.database)
        if args.command == "add":
            expense = tracker.add(args.amount, args.category, args.description, args.date)
            print("Added\t" + _display(expense))
        elif args.command == "view":
            expenses = tracker.view(args.category)
            print("ID\tDate\tCategory\tAmount\tDescription")
            for expense in expenses:
                print(_display(expense))
            if not expenses:
                print("No expenses found.")
        elif args.command == "update":
            expense = tracker.update(
                args.id, amount=args.amount, category=args.category,
                description=args.description, date=args.date,
            )
            print("Updated\t" + _display(expense))
        elif args.command == "delete":
            tracker.delete(args.id)
            print(f"Deleted expense {args.id}")
        else:
            print("Total: " + format_amount(tracker.total(args.category)))
    except (ExpenseError, sqlite3.Error, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
