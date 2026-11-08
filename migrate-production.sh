#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

DJANGO_ENV=production GCS_ENABLED=false uv run --no-sync python - <<'PY'
import os
import re

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from django.conf import settings
from django.db import connection
from psycopg import sql

schema = os.environ.get("DB_SCHEMA", "eventos_ddc")
if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", schema):
    raise SystemExit("DB_SCHEMA inválido.")
with connection.cursor() as cursor:
    cursor.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(sql.Identifier(schema)))
print(f"Schema {schema} pronto.")
PY

DJANGO_ENV=production GCS_ENABLED=false uv run --no-sync python manage.py migrate --noinput
