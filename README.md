# Campus Piano Catalog

A small natural-language interface to a seeded SQLite piano catalog. Ask a question, review the answer and matching rows. With an OpenAI API key, GPT generates the SQL and summarizes the query results.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Add `OPENAI_API_KEY` to `.env`. Set `OPENAI_MODEL=gpt-6-luna` there to use GPT-6 Luna.

```bash
python app.py
```
