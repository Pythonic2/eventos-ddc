#!/usr/bin/env bash
set -euo pipefail

SERVICE="${SERVICE:-eventos-ddc}"
REGION="${REGION:-southamerica-east1}"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_ENV="${PROJECT_ROOT}/.env"

command -v gcloud >/dev/null || { echo "Erro: gcloud não encontrado." >&2; exit 1; }
command -v python3 >/dev/null || { echo "Erro: python3 não encontrado." >&2; exit 1; }
test -f "$APP_ENV" || { echo "Erro: .env não encontrado." >&2; exit 1; }

TEMP_ENV="$(mktemp "${TMPDIR:-/tmp}/eventos-ddc-cloud-run.XXXXXX.json")"
trap 'rm -f "$TEMP_ENV"' EXIT
chmod 600 "$TEMP_ENV"

python3 - "$APP_ENV" "$TEMP_ENV" <<'PY'
import json
import sys
from pathlib import Path


def read_env(path):
    values = {}
    for raw_line in Path(path).read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        values[key.strip()] = value
    return values


source = read_env(sys.argv[1])


def append_csv(value, required):
    items = [item.strip() for item in value.split(",") if item.strip()]
    if required not in items:
        items.append(required)
    return ",".join(items)


allowed = {
    "SECRET_KEY", "DB_ENGINE", "DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT",
    "DB_SCHEMA", "DB_SSLMODE", "DB_CHANNEL_BINDING", "DB_CONNECT_TIMEOUT", "DB_CONN_MAX_AGE",
    "ALLOWED_HOSTS", "CSRF_TRUSTED_ORIGINS", "GCS_BUCKET_NAME", "GCS_PROJECT_ID",
    "GCS_SIGNED_URL_TTL", "GCS_IAM_SIGN_BLOB", "GCS_SA_EMAIL", "MEDIA_MAX_UPLOAD_SIZE",
    "GUNICORN_WORKERS", "GUNICORN_THREADS", "GUNICORN_TIMEOUT",
}
env = {key: value for key, value in source.items() if key in allowed and value}
env.update({
    "DJANGO_ENV": "production", "DEBUG": "false", "GCS_ENABLED": "true",
    "GCS_APP_PREFIX": "eventos-ddc", "SERVE_MEDIA": "false", "RUN_MIGRATIONS": "false",
    "DJANGO_SECURE_SSL_REDIRECT": "true",
})
env["ALLOWED_HOSTS"] = append_csv(env.get("ALLOWED_HOSTS", ""), ".run.app")
env["CSRF_TRUSTED_ORIGINS"] = append_csv(env.get("CSRF_TRUSTED_ORIGINS", ""), "https://*.run.app")
required = ("SECRET_KEY", "DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST", "DB_SCHEMA", "GCS_BUCKET_NAME", "GCS_PROJECT_ID", "GCS_SA_EMAIL")
missing = [key for key in required if not env.get(key)]
if missing:
    raise SystemExit("Variáveis obrigatórias ausentes: " + ", ".join(missing))
Path(sys.argv[2]).write_text(json.dumps(env), encoding="utf-8")
PY

PROJECT_ID="$(python3 - "$TEMP_ENV" <<'PY'
import json, sys
print(json.load(open(sys.argv[1], encoding="utf-8"))["GCS_PROJECT_ID"])
PY
)"
SERVICE_ACCOUNT="$(python3 - "$TEMP_ENV" <<'PY'
import json, sys
print(json.load(open(sys.argv[1], encoding="utf-8"))["GCS_SA_EMAIL"])
PY
)"

gcloud run deploy "$SERVICE" \
    --project "$PROJECT_ID" \
    --source "$PROJECT_ROOT" \
    --region "$REGION" \
    --service-account "$SERVICE_ACCOUNT" \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --min-instances 0 \
    --max-instances 1 \
    --concurrency 1 \
    --timeout 120 \
    --env-vars-file "$TEMP_ENV" \
    --quiet
