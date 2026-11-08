from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView
from django.views.static import serve

from .views import health, home


urlpatterns = [
    path("admin/", admin.site.urls),
    path("eventos/", include("eventos.urls")),
    path("", home, name="home"),
    path("healthz/", health, name="health"),
    path("assets/<path:path>", serve, {"document_root": settings.BASE_DIR / "assets"}),
    path("eventos/index.html", RedirectView.as_view(pattern_name="eventos:index", permanent=False)),
]

if settings.SERVE_MEDIA:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
