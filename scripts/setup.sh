#!/usr/bin/env bash
# One-shot environment setup: database, models, schema, Python deps.
# Portable across macOS / Linux / Windows (use WSL or Git Bash on Windows).
#
# Ollama runs in one of two modes:
#   native  (default when the `ollama` command is installed) — uses the host GPU
#           (Metal on Apple Silicon, CUDA on Linux). Fastest.
#   docker  (forced with `--ollama-docker`, or automatic when `ollama` is absent) —
#           fully containerized; works anywhere Docker runs (CPU by default).
#
# Usage:
#   bash scripts/setup.sh                  # auto: native if available, else docker
#   bash scripts/setup.sh --ollama-docker  # force the containerized Ollama
set -euo pipefail
cd "$(dirname "$0")/.."

[ -f .env ] || cp .env.example .env
set -a; . ./.env; set +a

# --- choose the Ollama mode ---
OLLAMA_MODE="${RAG_OLLAMA_MODE:-auto}"
[ "${1:-}" = "--ollama-docker" ] && OLLAMA_MODE="docker"
if [ "$OLLAMA_MODE" = "auto" ]; then
  command -v ollama >/dev/null 2>&1 && OLLAMA_MODE="native" || OLLAMA_MODE="docker"
fi
echo "Ollama mode: $OLLAMA_MODE"

if ! docker info >/dev/null 2>&1; then
  echo "ERROR: Docker daemon is not running. Start it (Docker Desktop, or" >&2
  echo "       'sudo systemctl start docker' on Linux) and retry." >&2
  exit 1
fi

echo "==> 1/5 Starting Postgres + pgvector (Docker)"
docker compose up -d db
printf "    waiting for the database to become healthy"
until docker compose exec -T db pg_isready -U "$POSTGRES_USER" -d "$POSTGRES_DB" >/dev/null 2>&1; do
  printf "."; sleep 1
done
echo " ok"

echo "==> 2/5 Initializing schema (pgvector extension + docs table)"
docker compose exec -T db psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" < scripts/db_init.sql

echo "==> 3/5 Pulling Ollama models ($OLLAMA_MODE)"
if [ "$OLLAMA_MODE" = "docker" ]; then
  docker compose --profile containerized up -d ollama
  printf "    waiting for Ollama"
  until docker compose exec -T ollama ollama list >/dev/null 2>&1; do printf "."; sleep 1; done
  echo " ok"
  docker compose exec -T ollama ollama pull "$EMBED_MODEL"
  docker compose exec -T ollama ollama pull "$GEN_MODEL"
else
  ollama pull "$EMBED_MODEL"
  ollama pull "$GEN_MODEL"
fi

echo "==> 4/5 Creating Python virtualenv + installing dependencies"
python3 -m venv .venv
# shellcheck disable=SC1091
. .venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

echo "==> 5/5 Setup complete (Ollama: $OLLAMA_MODE)."
echo "    Next: source .venv/bin/activate"
echo "          python scripts/ingest.py --source corpus/curated --origin curated"
