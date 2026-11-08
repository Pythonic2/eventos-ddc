from pathlib import Path
from urllib.parse import urlsplit

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator


IMAGE_EXTENSIONS = ("jpg", "jpeg", "png", "webp", "gif")
VIDEO_EXTENSIONS = ("mp4", "webm", "ogg")


def validate_file_size(upload, *, maximum, label):
    if upload and upload.size > maximum:
        raise ValidationError(f"O {label} deve ter no máximo {maximum // (1024 * 1024)} MB.")


def validate_image_size(upload):
    validate_file_size(upload, maximum=10 * 1024 * 1024, label="arquivo de imagem")


def validate_video_size(upload):
    validate_file_size(upload, maximum=100 * 1024 * 1024, label="arquivo de vídeo")


validate_image_extension = FileExtensionValidator(allowed_extensions=IMAGE_EXTENSIONS)
validate_video_extension = FileExtensionValidator(allowed_extensions=VIDEO_EXTENSIONS)


def validate_destination(value):
    if not value:
        return
    if value.startswith(("/", "#", "mailto:", "tel:")):
        return
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValidationError("Use uma URL HTTP(S), um caminho iniciado por /, uma âncora #, mailto: ou tel:.")


def media_upload_path(instance, filename):
    safe_name = Path(filename).name
    return f"eventos/{instance.media_type}/{safe_name}"
