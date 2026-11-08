from django.db import migrations, models


NEW_SECTIONS = {
    "empresa": {
        "chamada": "CONHEÇA A DONA DO CHOPP",
        "titulo": "Chopp gelado e bons momentos para compartilhar.",
        "descricao": "A Dona do Chopp leva a experiência do chopp tirado na hora para festas e encontros em Fortaleza e Região Metropolitana.",
        "conteudo_extra": "Fale com a nossa equipe para conhecer as opções disponíveis para o seu evento.",
        "ordem": 1,
    },
    "marcas": {
        "chamada": "NOSSAS OPÇÕES",
        "titulo": "Marcas de chopp",
        "descricao": "Consulte as marcas e estilos disponíveis para a sua data.",
        "ordem": 2,
    },
    "palavras_chave": {
        "chamada": "CHOPP PARA CELEBRAR",
        "titulo": "Do seu jeito, para o seu momento.",
        "descricao": "Algumas das ocasiões que atendemos.",
        "ordem": 3,
    },
    "whatsapp": {
        "chamada": "FALE COM A GENTE",
        "titulo": "Quer chopp no seu evento?",
        "descricao": "Chame a Dona do Chopp no WhatsApp para consultar marcas, disponibilidade e orçamento.",
        "cta_text": "Falar pelo WhatsApp",
        "cta_url": "https://wa.me/5585991803678?text=Ol%C3%A1%21%20Vim%20pelo%20site%20de%20eventos%20da%20Dona%20do%20Chopp.",
        "ordem": 6,
    },
}

SECTION_ITEMS = {
    "marcas": [
        ("Marcas selecionadas", "Informe aqui as marcas de chopp disponíveis."),
    ],
    "palavras_chave": [
        ("Aniversários", ""),
        ("Casamentos", ""),
        ("Confraternizações", ""),
        ("Eventos corporativos", ""),
    ],
}


def seed_simplified_sections(apps, schema_editor):
    EventPage = apps.get_model("eventos", "EventPage")
    EventSection = apps.get_model("eventos", "EventSection")
    EventMedia = apps.get_model("eventos", "EventMedia")

    for page in EventPage.objects.all():
        for section_type, defaults in NEW_SECTIONS.items():
            section, created = EventSection.objects.get_or_create(
                pagina=page,
                tipo=section_type,
                defaults=defaults,
            )
            if created:
                for order, (title, description) in enumerate(SECTION_ITEMS.get(section_type, []), start=1):
                    EventMedia.objects.create(
                        secao=section,
                        media_type="conteudo",
                        titulo=title,
                        descricao=description,
                        ordem=order,
                        ativo=True,
                    )


class Migration(migrations.Migration):
    dependencies = [("eventos", "0008_seed_all_editable_sections")]

    operations = [
        migrations.AlterField(
            model_name="eventsection",
            name="tipo",
            field=models.CharField(
                choices=[
                    ("empresa", "Sobre a empresa"),
                    ("marcas", "Marcas de chopp"),
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
        migrations.RunPython(seed_simplified_sections, migrations.RunPython.noop),
    ]
