# Testing & verification

On every push/PR to `main` or `develop`, **[`.github/workflows/ci.yml`](../.github/workflows/ci.yml)** runs on Ubuntu: `compileall` + `pytest` for the dashboard, and backend `smoke_test.py` with SQLite.

## 1. Syntax (whole repo)

Uses a project-local bytecode cache so macOS sandboxed environments can write `.pyc` files:

```bash
export PYTHONPYCACHEPREFIX="$(pwd)/.pycache_local"
python3 -m compileall -q .
rm -rf .pycache_local
```

## 2. Dashboard (pytest)

Use a **dedicated** virtualenv with **only** `dashboard/requirements.txt` first. Mixing `backend/requirements.txt` into the same venv can downgrade/upgrade NumPy and trigger **macOS Accelerate / NumPy segfaults** on import.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r dashboard/requirements.txt pytest httpx
export PYTHONPATH=dashboard
pytest dashboard/tests -v --tb=short
```

### Streamlit smoke (optional)

After dashboard deps are installed:

```bash
export PYTHONPATH=dashboard
python -c "import pages_predictions; import pages_whatif; print('page modules OK')"
```

Full UI: `cd dashboard && streamlit run app.py`

## 3. Backend (smoke tests)

Prefer a **separate** venv (e.g. `.venv-backend`) with **only** `backend/requirements.txt`:

```bash
python3 -m venv .venv-backend
source .venv-backend/bin/activate
pip install -U pip
pip install -r backend/requirements.txt pytest httpx
export DATABASE_URL="sqlite:///$(pwd)/backend/.smoke.db"
cd backend
pytest smoke_test.py -v --tb=short
```

If NumPy crashes on import on Apple Silicon / older macOS Python, try upgrading NumPy in that venv (`pip install -U "numpy>=1.26.4,<2.3"`) or use **Python 3.11+** from python.org or Homebrew.

## 4. Docker Compose (config sanity)

```bash
docker compose config
```

Build images (slow; needs Docker):

```bash
docker compose build
```

Ensure `./ssl` exists if you enable TLS in `nginx.conf` later (compose mounts `./ssl` read-only).
