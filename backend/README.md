# CyberDemo Backend

FastAPI backend for SOC Tier-1 Agentic AI Analyst demonstration.

## Stack

- FastAPI
- SQLAlchemy 2.0 async
- PostgreSQL (asyncpg)
- OpenSearch

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn src.main:app --reload --port 8000
```
