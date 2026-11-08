from django.conf import settings
from django.http import FileResponse, JsonResponse


def home(request):
    return FileResponse((settings.BASE_DIR / "prepage.html").open("rb"), content_type="text/html; charset=utf-8")


def health(request):
    return JsonResponse({"status": "ok"})
