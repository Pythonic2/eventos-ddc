from django.db import migrations, models

import eventos.validators


def create_events_section(apps, schema_editor):
    EventPage = apps.get_model("eventos", "EventPage")
    EventSection = apps.get_model("eventos", "EventSection")
    EventMedia = apps.get_model("eventos", "EventMedia")

    media_fields = (
        "media_type",
        "titulo",
        "descricao",
        "imagem",
        "image_url",
        "video_file",
        "video_url",
        "thumbnail",
        "thumbnail_url",
        "legenda",
        "texto_alternativo",
        "ativo",
    )

    for page in EventPage.objects.all():
        page_updates = []
        if page.hero_cta_url == "#orcamento":
            page.hero_cta_url = "#whatsapp"
            page_updates.append("hero_cta_url")
        if page.secondary_cta_url == "#galeria":
            page.secondary_cta_url = "#eventos"
            page_updates.append("secondary_cta_url")
        if page_updates:
            page.save(update_fields=page_updates)

        events, created = EventSection.objects.get_or_create(
            pagina=page,
            tipo="eventos",
            defaults={
                "chamada": "FOTOS E VÍDEOS",
                "titulo": "Chopp, festas e bons momentos.",
                "descricao": "Alguns registros de aniversários, casamentos, confraternizações e eventos em Fortaleza e Região Metropolitana.",
                "ordem": 3,
                "ativo": True,
            },
        )
        if not created:
            continue

        order = 1
        sources = (
            ("galeria", "imagem", 3),
            ("videos", "video", 1),
        )
        for section_type, media_type, limit in sources:
            source = EventSection.objects.filter(pagina=page, tipo=section_type).first()
            if source is None:
                continue
            for media in EventMedia.objects.filter(secao=source, ativo=True, media_type=media_type).order_by("ordem", "id")[:limit]:
                values = {field: getattr(media, field) for field in media_fields}
                values["ordem"] = order
                EventMedia.objects.create(secao=events, **values)
                order += 1


class Migration(migrations.Migration):
    dependencies = [("eventos", "0009_simplify_event_sections")]

    operations = [
        migrations.AlterField(
            model_name="eventpage",
            name="hero_cta_url",
            field=models.CharField(
                default="#whatsapp",
                max_length=500,
                validators=[eventos.validators.validate_destination],
                verbose_name="destino do botão principal",
            ),
        ),
        migrations.AlterField(
            model_name="eventpage",
            name="secondary_cta_url",
            field=models.CharField(
                blank=True,
                default="#eventos",
                max_length=500,
                validators=[eventos.validators.validate_destination],
                verbose_name="destino do botão secundário",
            ),
        ),
        migrations.AlterField(
            model_name="eventsection",
            name="tipo",
            field=models.CharField(
                choices=[
                    ("empresa", "Sobre a empresa"),
                    ("marcas", "Marcas de chopp"),
                    ("eventos", "Eventos — fotos e vídeos"),
                    ("palavras_chave", "Palavras-chave"),
                    ("apresentacao", "Vantagens"),
                    ("galeria", "Galeria de fotos"),
                    ("ocasioes", "Tipos de evento"),
                    ("localizacao", "Fortaleza e Região Metropolitana"),
                    ("videos", "Vídeos"),
                    ("cta_final", "Chamada final"),
                    ("orcamento", "Orçamento"),
                    ("faq", "Dúvidas frequentes"),
                    ("whatsapp", "Contato pelo WhatsApp"),
                ],
                max_length=20,
                verbose_name="tipo de seção",
            ),
        ),
        migrations.RunPython(create_events_section, migrations.RunPython.noop),
    ]
