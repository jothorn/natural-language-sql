"""Campus piano catalog: natural language to safe, read-only SQL."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

from database import query_readonly, row_count

app = Flask(__name__, static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024

SCHEMA = """
Tables:
- buildings(id, name, abbreviation, address)
- rooms(id, building_id, room_number, room_type, floor, capacity, has_climate_control)
  Each room belongs to one building.
- pianos(id, serial_number, manufacturer, model, year_built, piano_type, condition_status,
  last_tuned_on, next_tuning_due, room_id, status)
  Each piano is assigned to one room. condition_status is Excellent, Good, Fair, or Needs repair.
- technicians(id, name, email, phone_number, specialty)
- maintenance_records(id, piano_id, technician_id, work_type, completed_on, cost, notes)
  Each record is work performed on one piano by one technician.
- events(id, room_id, piano_id, title, event_type, starts_at, ends_at, attendance, status)
  Events link a room and piano; status is scheduled, completed, or cancelled.

Use SQLite syntax. Dates are ISO YYYY-MM-DD; event timestamps are ISO YYYY-MM-DD HH:MM.
""".strip()


def _make_sql_prompt(question: str) -> str:
    return f"""You translate questions into one safe SQLite SELECT query.
Return only a JSON object with keys `sql` and `note`. `sql` must be one SELECT (WITH is okay),
never modify data, use only the listed tables and columns, and limit detail rows to 50.
Use explicit joins. For a question about current/future events use date('now') as the reference.
If a question cannot be answered from this schema, return {{"sql":"","note":"Explain why."}}.

{SCHEMA}

Question: {question}"""


def _openai_sql(question: str) -> tuple[str, str]:
    from openai import OpenAI

    client = OpenAI()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    params = {
        "model": model,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": "Generate safe, read-only SQLite SQL as requested. Return valid JSON only."},
            {"role": "user", "content": _make_sql_prompt(question)},
        ],
    }
    if not model.startswith("gpt-6"):
        params["temperature"] = 0
    response = client.chat.completions.create(**params)
    payload = json.loads(response.choices[0].message.content or "{}")
    return str(payload.get("sql", "")).strip(), str(payload.get("note", "")).strip()


def _openai_answer(question: str, rows: list[dict]) -> str:
    from openai import OpenAI

    client = OpenAI()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    params = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": "Answer the user's database question in clear, concise plain language. "
                "Use only the supplied query results. If there are no rows, say that no matching records were found. "
                "Do not make up facts or discuss SQL.",
            },
            {"role": "user", "content": json.dumps({"question": question, "results": rows}, default=str)},
        ],
    }
    if not model.startswith("gpt-6"):
        params["temperature"] = 0.3
    response = client.chat.completions.create(**params)
    return (response.choices[0].message.content or "Here are the matching records.").strip()


def _demo_translate(question: str) -> tuple[str, str, str]:
    """Small offline interpreter for the example prompts, so the app works without a key."""
    q = question.lower()
    if any(w in q for w in ("overdue", "past due", "tuning due", "need tuning", "due for tuning")):
        sql = """SELECT p.serial_number, p.manufacturer, p.model, p.next_tuning_due,
                  r.room_number, b.name AS building
           FROM pianos p JOIN rooms r ON r.id=p.room_id JOIN buildings b ON b.id=r.building_id
           WHERE p.status='active' AND date(p.next_tuning_due) < date('now')
           ORDER BY p.next_tuning_due LIMIT 50"""
        return sql, "Overdue tuning is determined by comparing each active piano's next tuning date with today.", "overdue"
    if "grand" in q and any(w in q for w in ("where", "room", "which", "find", "list")):
        sql = """SELECT p.serial_number, p.manufacturer, p.model, r.room_number, r.room_type,
                  b.name AS building
           FROM pianos p JOIN rooms r ON r.id=p.room_id JOIN buildings b ON b.id=r.building_id
           WHERE lower(p.piano_type)='grand' AND p.status='active'
           ORDER BY b.name, r.room_number LIMIT 50"""
        return sql, "These are active grand pianos and their assigned rooms.", "grand"
    if "upcoming" in q or "coming up" in q or "next recital" in q:
        sql = """SELECT e.title, e.event_type, e.starts_at, r.room_number, b.name AS building,
                  p.serial_number, e.attendance
           FROM events e JOIN rooms r ON r.id=e.room_id JOIN buildings b ON b.id=r.building_id
           LEFT JOIN pianos p ON p.id=e.piano_id
           WHERE e.status='scheduled' AND datetime(e.starts_at) >= datetime('now')
           ORDER BY e.starts_at LIMIT 50"""
        return sql, "These are scheduled events from now onward.", "events"
    if "spend" in q or "cost" in q or "maintenance" in q and "technician" in q:
        sql = """SELECT t.name AS technician, COUNT(m.id) AS jobs, ROUND(SUM(m.cost), 2) AS total_cost
           FROM technicians t JOIN maintenance_records m ON m.technician_id=t.id
           WHERE date(m.completed_on) >= date('now','-90 days')
           GROUP BY t.id ORDER BY total_cost DESC"""
        return sql, "Maintenance totals cover the last 90 days.", "costs"
    if "count" in q or "how many" in q or "by building" in q:
        sql = """SELECT b.name AS building, COUNT(p.id) AS piano_count
           FROM buildings b LEFT JOIN rooms r ON r.building_id=b.id
           LEFT JOIN pianos p ON p.room_id=r.id AND p.status='active'
           GROUP BY b.id ORDER BY piano_count DESC"""
        return sql, "Counts include active pianos assigned to rooms in each building.", "counts"
    serial = re.search(r"\b(\d{4,})\b", q)
    if serial and any(w in q for w in ("last tuned", "tuned", "tuning history", "maintenance")):
        sql = """SELECT p.serial_number, p.manufacturer, p.model, p.last_tuned_on,
                  p.next_tuning_due, r.room_number, b.name AS building
           FROM pianos p JOIN rooms r ON r.id=p.room_id JOIN buildings b ON b.id=r.building_id
           WHERE p.serial_number=? LIMIT 1""".replace("?", "'" + serial.group(1) + "'")
        return sql, f"Tuning details for piano {serial.group(1)}.", "detail"
    return "", "Demo mode can answer the sample questions. Add an OpenAI API key in .env for general questions.", "unsupported"


def _demo_answer(kind: str, rows: list[dict], note: str) -> str:
    if kind == "overdue":
        if not rows:
            return "No active pianos are overdue for tuning today."
        names = ", ".join(f"{r['manufacturer']} {r['model']} ({r['serial_number']}) in {r['building']}, room {r['room_number']}" for r in rows)
        return f"{len(rows)} active piano(s) are overdue for tuning: {names}."
    if kind == "grand":
        if not rows:
            return "No active grand pianos were found."
        return "Active grand pianos: " + "; ".join(f"{r['manufacturer']} {r['model']} (serial {r['serial_number']}) in {r['building']}, room {r['room_number']}" for r in rows) + "."
    if kind == "events":
        if not rows:
            return "There are no scheduled upcoming events in the catalog."
        return "Upcoming events: " + "; ".join(f"{r['title']} on {r['starts_at']} in {r['building']}, room {r['room_number']}" for r in rows) + "."
    if kind == "costs":
        if not rows:
            return "No maintenance spending was recorded in the last 90 days."
        return "Maintenance spending in the last 90 days: " + "; ".join(f"{r['technician']}: ${r['total_cost'] or 0:.2f} across {r['jobs']} job(s)" for r in rows) + "."
    if kind == "counts":
        total = sum(r["piano_count"] for r in rows)
        return f"The catalog has {total} active piano(s): " + "; ".join(f"{r['building']}: {r['piano_count']}" for r in rows) + "."
    if kind == "detail":
        if not rows:
            return "No piano with that serial number was found."
        r = rows[0]
        return f"Piano {r['serial_number']} is a {r['manufacturer']} {r['model']} in {r['building']}, room {r['room_number']}. It was last tuned on {r['last_tuned_on']} and is next due on {r['next_tuning_due']}."
    return note


@app.get("/")
def index():
    return send_from_directory(ROOT / "static", "index.html")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "pianos": row_count("pianos"), "mode": "ai" if os.getenv("OPENAI_API_KEY") else "demo"})


@app.post("/api/query")
def query():
    body = request.get_json(silent=True) or {}
    question = str(body.get("question", "")).strip()
    if not question:
        return jsonify({"error": "Type a question first."}), 400
    if len(question) > 500:
        return jsonify({"error": "Keep your question under 500 characters."}), 400

    mode = "ai" if os.getenv("OPENAI_API_KEY") else "demo"
    kind = "ai"
    try:
        if mode == "ai":
            sql, note = _openai_sql(question)
            if not sql:
                return jsonify({"answer": note or "I couldn't map that question to this database.", "sql": "", "rows": [], "columns": [], "mode": mode})
        else:
            sql, note, kind = _demo_translate(question)
            if not sql:
                return jsonify({"answer": note, "sql": "", "rows": [], "columns": [], "mode": mode})
        rows = query_readonly(sql)
        answer = _openai_answer(question, rows) if mode == "ai" else _demo_answer(kind, rows, note)
        columns = list(rows[0].keys()) if rows else []
        return jsonify({"answer": answer, "sql": sql.strip(), "rows": rows, "columns": columns, "mode": mode, "note": note})
    except ValueError as exc:
        return jsonify({"error": str(exc), "mode": mode}), 400
    except Exception as exc:
        app.logger.exception("Query failed")
        message = "The AI request failed. Check your API key and try again." if mode == "ai" else "The demo query could not be completed."
        return jsonify({"error": message, "mode": mode}), 502


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG") == "1")
