# Contributing

Thanks for helping improve Echolon.

## Before you start

1. Open an **issue** or comment on an existing one so work isn’t duplicated.  
2. Use a **short-lived branch** off `main` (e.g. `fix/…`, `feat/…`).

## Local setup

```bash
# Dashboard (recommended: dedicated venv)
python3 -m venv .venv && source .venv/bin/activate
pip install -r dashboard/requirements.txt pytest httpx
export PYTHONPATH=dashboard
pytest dashboard/tests -v

# Backend (separate venv avoids NumPy/pandas clashes on some Macs)
python3 -m venv .venv-backend && source .venv-backend/bin/activate
pip install -r backend/requirements.txt pytest httpx
export DATABASE_URL=sqlite:///./backend/.local_smoke.db
cd backend && pytest smoke_test.py -v
```

Full notes: **[docs/TESTING.md](docs/TESTING.md)**.

## Optional: pre-commit

```bash
pip install pre-commit
pre-commit install
```

## Pull requests

- Keep changes **focused** (one concern per PR).  
- Ensure **GitHub Actions CI** is green before requesting review.  
- Update **docs** if you change setup, env vars, or deployment steps.

## Code style

- Python: **`black`** (see `.pre-commit-config.yaml`).  
- Prefer **clear names** and **small functions** over large refactors mixed with features.
