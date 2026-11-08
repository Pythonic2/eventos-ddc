import django.core.validators
import eventos.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("eventos", "0010_consolidate_event_content")]

    operations = [
        migrations.AlterField(
            model_name="eventmedia",
            name="video_file",
            field=models.FileField(
                blank=True,
                help_text="Use preferencialmente MP4 com vídeo H.264 e áudio AAC. Também são aceitos M4V, WebM, OGG e MOV; a reprodução não cortará o vídeo.",
                upload_to=eventos.validators.media_upload_path,
                validators=[
                    django.core.validators.FileExtensionValidator(allowed_extensions=("mp4", "m4v", "webm", "ogg", "mov")),
                    eventos.validators.validate_video_size,
                ],
                verbose_name="arquivo de vídeo",
            ),
        ),
        migrations.AlterField(
            model_name="eventpage",
            name="hero_video",
            field=models.FileField(
                blank=True,
                help_text="Use preferencialmente MP4 com vídeo H.264 e áudio AAC. Também são aceitos M4V, WebM, OGG e MOV; o vídeo será exibido sem cortes.",
                upload_to="eventos/hero/",
                validators=[
                    django.core.validators.FileExtensionValidator(allowed_extensions=("mp4", "m4v", "webm", "ogg", "mov")),
                    eventos.validators.validate_video_size,
                ],
                verbose_name="vídeo do hero",
            ),
        ),
    ]
