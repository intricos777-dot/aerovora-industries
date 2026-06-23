#!/usr/bin/env bash
set -eo pipefail

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

# Activate venv
source "$DIR/venv/bin/activate"

# Ensure DB directory exists
mkdir -p "$DIR/data"

export STRIPE_SECRET_KEY="${STRIPE_SECRET_KEY:-}"
export AEROVORA_BASE_URL="http://0.0.0.0:8777"
export AEROVORA_SITE_URL="https://intricos777-dot.github.io/aerovora-storefront"

exec uvicorn backend.main:app --host 0.0.0.0 --port 8777 --reload
