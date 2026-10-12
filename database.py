"""SQLite setup and read-only query boundary."""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("DATABASE_PATH", ROOT / "data" / "campus_pianos.sqlite3"))
SCHEMA_FILE = ROOT / "data" / "schema.sql"
SEED_FILE = ROOT / "data" / "seed.sql"

SAFE_FUNCTIONS = {
    "abs", "avg", "coalesce", "count", "date", "datetime", "ifnull", "julianday",
    "group_concat", "instr", "length", "like", "lower", "max", "min", "printf", "replace",
    "round", "strftime", "substr", "sum", "time", "total", "trim", "upper", "typeof", "unicode",
}
ALLOWED_TABLES = {"buildings", "rooms", "pianos", "technicians", "maintenance_records", "events"}


def initialize_database() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript(SCHEMA_FILE.read_text())
        technician_columns = {
            row[1] for row in conn.execute("PRAGMA table_info(technicians)")
        }
        if "phone_number" not in technician_columns:
            conn.execute("ALTER TABLE technicians ADD COLUMN phone_number TEXT")
            conn.executemany(
                "UPDATE technicians SET phone_number = ? WHERE id = ?",
                [
                    ("720-555-0101", 1),
                    ("720-555-0102", 2),
                    ("720-555-0103", 3),
                    ("720-555-0104", 4),
                ],
            )
        count = conn.execute("SELECT COUNT(*) FROM pianos").fetchone()[0]
        if count == 0:
            conn.executescript(SEED_FILE.read_text())


def _authorizer(action, arg1, arg2, database, trigger):
    if action in (sqlite3.SQLITE_SELECT, sqlite3.SQLITE_RECURSIVE):
        return sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_READ and arg1 in ALLOWED_TABLES:
        return sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_FUNCTION and (arg2 or arg1 or "").lower() in SAFE_FUNCTIONS:
        return sqlite3.SQLITE_OK
    return sqlite3.SQLITE_DENY


def query_readonly(sql: str) -> list[dict]:
    normalized = sql.strip()
    if not normalized:
        raise ValueError("No SQL query was generated.")
    if "\x00" in normalized or normalized.lstrip().lower().startswith(("insert", "update", "delete", "drop", "alter", "create", "attach", "pragma", "vacuum", "replace")):
        raise ValueError("Only read-only SELECT queries are allowed.")
    try:
        with sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA query_only = ON")
            conn.set_authorizer(_authorizer)
            cur = conn.execute(normalized)
            rows = cur.fetchmany(51)
            if len(rows) > 50:
                rows = rows[:50]
            return [dict(row) for row in rows]
    except sqlite3.DatabaseError as exc:
        raise ValueError(f"That query could not be run against the catalog: {exc}") from exc


def row_count(table: str) -> int:
    if table != "pianos":
        raise ValueError("Unknown table")
    with sqlite3.connect(DB_PATH) as conn:
        return int(conn.execute("SELECT COUNT(*) FROM pianos").fetchone()[0])


initialize_database()
