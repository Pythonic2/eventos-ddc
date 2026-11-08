#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

export GCS_ENABLED=true
export GCS_APP_PREFIX=eventos-ddc
uv run --no-sync python manage.py sync_media_to_gcs "$@"
