from django.db import migrations


def seed_event_page(apps, schema_editor):
    EventPage = apps.get_model("eventos", "EventPage")
    EventSection = apps.get_model("eventos", "EventSection")

    page = EventPage.objects.order_by("pk").first()
    if page is None:
        page = EventPage.objects.create(
            titulo="O seu evento merece chopp gelado e muita comemoração.",
            subtitulo="Chopp para eventos",
            descricao="Atendemos eventos exclusivamente em Fortaleza–CE. Imagina os convidados reunidos, a festa acontecendo e aquele chopp tirado na hora, do jeito que uma boa celebração merece.",
            seo_description="Chopp para festas e celebrações com atendimento somente em Fortaleza–CE.",
        )
    sections = (
        ("apresentacao", "Seu evento acontece uma vez. Faça valer cada brinde.", "Do primeiro convidado ao último brinde, a experiência faz a diferença.", 1),
        ("galeria", "Se a festa é boa, o brinde acompanha.", "Inspirações para imaginar o chopp no seu próximo evento em Fortaleza–CE.", 2),
        ("videos", "Dá até para sentir o clima da festa!", "Veja montagens, convidados e chopp sendo servido.", 3),
        ("cta_final", "Seu próximo brinde começa aqui.", "Conte sua ideia para um evento em Fortaleza–CE e consulte as opções disponíveis.", 4),
    )
    for section_type, title, description, order in sections:
        EventSection.objects.get_or_create(
            pagina=page,
            tipo=section_type,
            defaults={"titulo": title, "descricao": description, "ordem": order},
        )


def unseed_event_page(apps, schema_editor):
    # A reversão preserva conteúdo que pode ter sido editado pelo cliente.
    pass


class Migration(migrations.Migration):
    dependencies = [("eventos", "0001_initial")]
    operations = [migrations.RunPython(seed_event_page, unseed_event_page)]
