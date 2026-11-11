from django.db import migrations


OLD_NUMBER = "5585991803678"
NEW_NUMBER = "5585981423909"


def replace_whatsapp_number(apps, old_number, new_number):
    EventSection = apps.get_model("eventos", "EventSection")
    sections = EventSection.objects.filter(tipo="whatsapp", cta_url__contains=old_number)
    for section in sections.iterator():
        section.cta_url = section.cta_url.replace(old_number, new_number)
        section.save(update_fields=("cta_url",))


def update_whatsapp_number(apps, schema_editor):
    replace_whatsapp_number(apps, OLD_NUMBER, NEW_NUMBER)


def restore_whatsapp_number(apps, schema_editor):
    replace_whatsapp_number(apps, NEW_NUMBER, OLD_NUMBER)


class Migration(migrations.Migration):
    dependencies = [("eventos", "0013_remove_eventsection_unique_event_section_type_and_more")]

    operations = [migrations.RunPython(update_whatsapp_number, restore_whatsapp_number)]
