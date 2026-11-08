from django.db import migrations


OLD_PHRASES = (
    ("Atendemos eventos exclusivamente em Fortaleza–CE", "Atendemos eventos em Fortaleza–CE e Região Metropolitana"),
    ("atendimento somente em Fortaleza–CE", "atendimento em Fortaleza–CE e Região Metropolitana"),
    ("evento em Fortaleza–CE", "evento em Fortaleza–CE e Região Metropolitana"),
)


def replace_service_area(apps, schema_editor):
    EventPage = apps.get_model("eventos", "EventPage")
    EventSection = apps.get_model("eventos", "EventSection")

    for page in EventPage.objects.all():
        changed = []
        for field in ("descricao", "seo_description"):
            value = getattr(page, field)
            updated = value
            for old, new in OLD_PHRASES:
                updated = updated.replace(old, new)
            if updated != value:
                setattr(page, field, updated)
                changed.append(field)
        if changed:
            page.save(update_fields=changed)

    for section in EventSection.objects.all():
        updated = section.descricao
        for old, new in OLD_PHRASES:
            updated = updated.replace(old, new)
        if updated != section.descricao:
            section.descricao = updated
            section.save(update_fields=("descricao",))


class Migration(migrations.Migration):
    dependencies = [("eventos", "0002_seed_event_page")]
    operations = [migrations.RunPython(replace_service_area, migrations.RunPython.noop)]
