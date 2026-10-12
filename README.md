# Campus Piano Catalog

A small natural-language interface to a seeded SQLite piano catalog. Ask a question, review the answer and matching rows. With an OpenAI API key, GPT generates the SQL and summarizes the query results.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add `OPENAI_API_KEY` to `.env`. Set `OPENAI_MODEL=gpt-6-luna` there to use GPT-6 Luna. Without a key, the example questions work in demo mode.

```bash
python app.py
```

## Database diagram

Create or update the standalone [schema diagram](schema_diagram.png) with the free [SQLite to ER Diagram](https://sqltoerdiagram.com/sqlite/) website: paste in `data/schema.sql`, arrange the tables, then export PNG or SVG. The site says it parses the schema in your browser and does not upload it.
