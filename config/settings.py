import os
import re
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
    return os.environ.get(name, str(default)).lower() in {"1", "true", "yes"}


def env_list(name, default=()):
    raw_value = os.environ.get(name)
    values = raw_value.split(",") if raw_value else default
    return list(dict.fromkeys(value.strip() for value in values if value.strip()))


ENVIRONMENT = os.environ.get("DJANGO_ENV", "development").lower()
IS_PRODUCTION = ENVIRONMENT == "production"
SECRET_KEY = os.environ.get("SECRET_KEY") or os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    if IS_PRODUCTION:
        raise RuntimeError("SECRET_KEY é obrigatória em produção.")
    SECRET_KEY = "django-insecure-local-development-only"

DEBUG = env_bool("DEBUG", not IS_PRODUCTION) and not IS_PRODUCTION
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", (".run.app",) if IS_PRODUCTION else ("localhost", "127.0.0.1", "testserver"))
ALLOWED_HOSTS = list(dict.fromkeys([*ALLOWED_HOSTS, *env_list("DJANGO_ALLOWED_HOSTS")]))
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS", ("https://*.run.app",) if IS_PRODUCTION else ())
CSRF_TRUSTED_ORIGINS = list(dict.fromkeys([*CSRF_TRUSTED_ORIGINS, *env_list("DJANGO_CSRF_TRUSTED_ORIGINS")]))

INSTALLED_APPS = [
    "django.contrib.admin", "django.contrib.auth", "django.contrib.contenttypes",
    "django.contrib.sessions", "django.contrib.messages", "django.contrib.staticfiles",
    "eventos.apps.EventosConfig",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware", "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware", "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware", "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware", "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"], "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request", "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASE_ENGINE = os.environ.get("DB_ENGINE", "").lower()
USE_POSTGRESQL = IS_PRODUCTION or DATABASE_ENGINE in {"postgres", "postgresql"}
if USE_POSTGRESQL:
    required_db_vars = ("DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST")
    missing_db_vars = [name for name in required_db_vars if not os.environ.get(name)]
    if missing_db_vars:
        raise RuntimeError("Variáveis PostgreSQL ausentes: " + ", ".join(missing_db_vars))
    db_schema = os.environ.get("DB_SCHEMA", "eventos_ddc")
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", db_schema):
        raise RuntimeError("DB_SCHEMA deve ser um identificador PostgreSQL simples.")
    db_options = {
        "connect_timeout": int(os.environ.get("DB_CONNECT_TIMEOUT", "10")),
        "sslmode": os.environ.get("DB_SSLMODE", "require"),
        "options": f"-c search_path={db_schema}",
    }
    if os.environ.get("DB_CHANNEL_BINDING"):
        db_options["channel_binding"] = os.environ["DB_CHANNEL_BINDING"]
    DATABASES = {"default": {
        "ENGINE": "django.db.backends.postgresql", "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"], "PASSWORD": os.environ["DB_PASSWORD"],
        "HOST": os.environ["DB_HOST"], "PORT": os.environ.get("DB_PORT", "5432"),
        "OPTIONS": db_options, "CONN_MAX_AGE": int(os.environ.get("DB_CONN_MAX_AGE", "60")),
        "CONN_HEALTH_CHECKS": True, "DISABLE_SERVER_SIDE_CURSORS": "-pooler." in os.environ["DB_HOST"],
    }}
else:
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": os.environ.get("SQLITE_NAME", BASE_DIR / "db.sqlite3")}}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Fortaleza"
USE_I18N = True
USE_TZ = True

STATIC_URL = os.environ.get("STATIC_URL", "/static/")
STATIC_ROOT = Path(os.environ.get("STATIC_ROOT", BASE_DIR / "staticfiles"))
STATICFILES_DIRS = [("site", BASE_DIR / "assets"), ("eventos", BASE_DIR / "eventos" / "assets")]
MEDIA_URL = os.environ.get("MEDIA_URL", "/media/")
MEDIA_ROOT = Path(os.environ.get("MEDIA_ROOT", BASE_DIR / "media"))
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage" if IS_PRODUCTION or env_bool("BUILD_STATICFILES") else "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

GCS_ENABLED = env_bool("GCS_ENABLED")
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "")
GCS_PROJECT_ID = os.environ.get("GCS_PROJECT_ID", "")
GCS_APP_PREFIX = os.environ.get("GCS_APP_PREFIX", "eventos-ddc").strip("/")
GCS_MEDIA_PREFIX = f"{GCS_APP_PREFIX}/midias"
GCS_SIGNED_URL_TTL = min(int(os.environ.get("GCS_SIGNED_URL_TTL", "900")), 604800)
GCS_SIGNED_URL_CACHE_TTL = max(min(GCS_SIGNED_URL_TTL - 60, 840), 1)
GCS_IAM_SIGN_BLOB = env_bool("GCS_IAM_SIGN_BLOB", True)
GCS_SA_EMAIL = os.environ.get("GCS_SA_EMAIL", "")
MEDIA_MAX_UPLOAD_SIZE = int(os.environ.get("MEDIA_MAX_UPLOAD_SIZE", str(100 * 1024 * 1024)))
WHATSAPP_NUMBER = "5585991803678"
if GCS_ENABLED:
    required_gcs = {"GCS_BUCKET_NAME": GCS_BUCKET_NAME, "GCS_PROJECT_ID": GCS_PROJECT_ID}
    missing_gcs = [name for name, value in required_gcs.items() if not value]
    if missing_gcs:
        raise RuntimeError("Variáveis GCS ausentes: " + ", ".join(missing_gcs))
    STORAGES["default"] = {"BACKEND": "eventos.gcs_storage.CachedGoogleCloudStorage", "OPTIONS": {
        "bucket_name": GCS_BUCKET_NAME, "project_id": GCS_PROJECT_ID, "location": GCS_MEDIA_PREFIX,
        "default_acl": None, "querystring_auth": True, "expiration": GCS_SIGNED_URL_TTL,
        "file_overwrite": False, "iam_sign_blob": GCS_IAM_SIGN_BLOB, "sa_email": GCS_SA_EMAIL or None,
        "object_parameters": {"cache_control": "private, max-age=900"},
    }}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = IS_PRODUCTION
CSRF_COOKIE_SECURE = IS_PRODUCTION
SECURE_SSL_REDIRECT = IS_PRODUCTION and env_bool("DJANGO_SECURE_SSL_REDIRECT", True)
SECURE_HSTS_SECONDS = int(os.environ.get("DJANGO_SECURE_HSTS_SECONDS", "3600")) if IS_PRODUCTION else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS")
SECURE_HSTS_PRELOAD = env_bool("DJANGO_SECURE_HSTS_PRELOAD")
SERVE_MEDIA = env_bool("SERVE_MEDIA", not GCS_ENABLED and DEBUG)
LOGGING = {
    "version": 1, "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "django.request": {"handlers": ["console"], "level": "ERROR", "propagate": False},
        "django.security": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}
