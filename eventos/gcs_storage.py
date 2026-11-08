import hashlib
import json

from django.conf import settings
from django.core.cache import cache
from storages.backends.gcloud import GoogleCloudStorage


class CachedGoogleCloudStorage(GoogleCloudStorage):
    """Reutiliza URLs assinadas por processo sem tornar o bucket público."""

    def _cache_key(self, name, parameters_json):
        digest = hashlib.sha256(f"{name}:{parameters_json}".encode()).hexdigest()
        return f"eventos-gcs-url:{digest}"

    def url(self, name, parameters=None):
        normalized = self._normalize_name(name)
        serialized = json.dumps(parameters or {}, sort_keys=True, default=str)
        key = self._cache_key(normalized, serialized)
        cached_url = cache.get(key)
        if cached_url:
            return cached_url
        signed_url = super().url(name, parameters=json.loads(serialized))
        cache.set(key, signed_url, timeout=settings.GCS_SIGNED_URL_CACHE_TTL)
        return signed_url

    def save(self, name, content, max_length=None):
        stored_name = super().save(name, content, max_length=max_length)
        cache.delete_pattern("eventos-gcs-url:*") if hasattr(cache, "delete_pattern") else cache.clear()
        return stored_name

    def delete(self, name):
        cache.delete_pattern("eventos-gcs-url:*") if hasattr(cache, "delete_pattern") else cache.clear()
        return super().delete(name)
