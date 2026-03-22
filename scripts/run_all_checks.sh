#!/usr/bin/env bash
# Run non-Docker checks from repo root. See docs/TESTING.md.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> compileall (syntax)"
export PYTHONPYCACHEPREFIX="$ROOT/.pycache_local"
python3 -m compileall -q .
rm -rf "$ROOT/.pycache_local"

if [[ -f "$ROOT/.venv/bin/activate" ]]; then
  # shellcheck source=/dev/null
  source "$ROOT/.venv/bin/activate"
  echo "==> dashboard pytest"
  PYTHONPATH=dashboard pytest dashboard/tests -v --tb=short
else
  echo "==> skip dashboard pytest (no .venv — create one per docs/TESTING.md)"
fi

if [[ -f "$ROOT/.venv-backend/bin/activate" ]]; then
  # shellcheck source=/dev/null
  source "$ROOT/.venv-backend/bin/activate"
  export DATABASE_URL="${DATABASE_URL:-sqlite:///$ROOT/backend/.smoke_checks.db}"
  echo "==> backend smoke_test.py"
  (cd backend && pytest smoke_test.py -v --tb=short)
else
  echo "==> skip backend pytest (no .venv-backend — create one per docs/TESTING.md)"
fi

if command -v docker >/dev/null 2>&1; then
  echo "==> docker compose config"
  docker compose config >/dev/null && echo "docker compose config: OK"
else
  echo "==> skip docker (not installed)"
fi

echo "==> done"
