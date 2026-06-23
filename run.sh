#!/usr/bin/env bash
set -eo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

# Load .env if present
if [ -f "$DIR/.env" ]; then
  set -a; source "$DIR/.env"; set +a
fi

# Activate venv
source "$DIR/venv/bin/activate"

# Ensure DB directory exists
mkdir -p "$DIR/data"

export AEROVORA_BASE_URL="${AEROVORA_BASE_URL:-http://0.0.0.0:8777}"
export AEROVORA_SITE_URL="${AEROVORA_SITE_URL:-https://intricos777-dot.github.io/aerovora-storefront}"

exec uvicorn backend.main:app --host 0.0.0.0 --port 8777 --reload
