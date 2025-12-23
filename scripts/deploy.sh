#!/usr/bin/env bash
set -euo pipefail

# Minimal deployment helper (Dev4)
# Usage (on server):
#   1) Copy .env to project root
#   2) ./scripts/deploy.sh

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

docker compose pull || true
docker compose up -d --build

echo "✅ Done. Check status with: docker compose ps"
