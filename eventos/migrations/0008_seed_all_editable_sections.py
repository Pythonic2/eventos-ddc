from django.db import migrations


SECTION_DEFAULTS = {
    "apresentacao": {
        "chamada": "MAIS SABOR PARA SUA FESTA",
        "titulo": "Seu evento acontece uma vez. Faça valer cada brinde.",
        "descricao": "Do primeiro convidado ao último brinde, a experiência faz a diferença.",
        "ordem": 1,
    },
    "galeria": {
        "chamada": "CLIMA DE FESTA",
        "titulo": "Se a festa é boa, o brinde acompanha.",
        "descricao": "Inspirações para imaginar o chopp no seu próximo evento.",
        "ordem": 2,
    },
    "ocasioes": {
        "chamada": "SEJA QUAL FOR A COMEMORAÇÃO",
        "titulo": "Tem chopp para o seu momento.",
        "ordem": 3,
    },
    "localizacao": {
        "chamada": "EVENTOS EM FORTALEZA–CE",
        "titulo": "Fortaleza e Região Metropolitana, com chopp tirado na hora.",
        "descricao": "A Dona do Chopp atende eventos em Fortaleza–CE e Região Metropolitana, levando chopp gelado e estrutura para diferentes tipos de celebração.",
        "conteudo_extra": "Atendemos aniversários, casamentos, batizados, bodas, noivados, formaturas, chá de bebê, chá revelação, festas de família, confraternizações de empresas, eventos corporativos, inaugurações e comemorações especiais. Consulte disponibilidade, quantidade de convidados e opções para sua data.",
        "ordem": 4,
    },
    "cta_final": {
        "chamada": "JÁ IMAGINOU NO SEU EVENTO?",
        "titulo": "Seu próximo brinde começa aqui.",
        "descricao": "Conte sua ideia para um evento em Fortaleza–CE e Região Metropolitana e consulte as opções disponíveis.",
        "cta_text": "Quero meu orçamento",
        "cta_url": "#orcamento",
        "ordem": 5,
    },
    "videos": {
        "chamada": "VEJA A EXPERIÊNCIA",
        "titulo": "Dá até para sentir o clima da festa!",
        "descricao": "Veja montagens, convidados e chopp sendo servido.",
        "ordem": 6,
    },
    "orcamento": {
        "chamada": "FORTALEZA–CE E REGIÃO METROPOLITANA",
        "titulo": "Vamos colocar chopp nessa festa?",
        "descricao": "Atendemos eventos em Fortaleza–CE e Região Metropolitana. Preencha os dados e envie tudo pelo WhatsApp em um clique.",
        "ordem": 7,
    },
    "faq": {
        "chamada": "DÚVIDAS FREQUENTES",
        "titulo": "Ainda pensando no seu evento?",
        "descricao": "A gente te ajuda a dar o próximo passo. Consulte as condições específicas com a equipe.",
        "cta_text": "Consultar disponibilidade",
        "cta_url": "#orcamento",
        "ordem": 8,
    },
}


ITEMS = {
    "apresentacao": [
        ("conteudo", "Chopp para celebrar", "Uma opção especial para reunir quem você gosta e deixar a festa ainda mais gostosa.", ""),
        ("conteudo", "Para cada ocasião", "Aniversários, casamentos, confraternizações e eventos corporativos: a ocasião é sua.", ""),
        ("conteudo", "Planejado com você", "Conte a data, o local e o tamanho do evento. Vamos conversar sobre a melhor solução.", ""),
    ],
    "galeria": [
        ("imagem", "Chopp servido na hora", "", "/static/site/fotoboa2.jpg"),
        ("imagem", "Festas especiais", "", "https://images.unsplash.com/photo-1530103862676-de8c9debad1d?auto=format&fit=crop&w=780&q=82"),
        ("imagem", "Ambiente de comemoração", "", "https://images.unsplash.com/photo-1514933651103-005eec06c04b?auto=format&fit=crop&w=780&q=82"),
        ("imagem", "O clima perfeito para brindar", "", "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=1200&q=82"),
    ],
    "ocasioes": [
        ("imagem", "Festas e aniversários", "Gente querida, música boa, conversa solta e um brinde para marcar a data.", "https://images.unsplash.com/photo-1464366400600-7168b8af9bc3?auto=format&fit=crop&w=850&q=82"),
        ("imagem", "Casamentos e celebrações", "Um toque a mais de descontração para brindar os momentos que ficam na memória.", "https://images.unsplash.com/photo-1519741497674-611481863552?auto=format&fit=crop&w=850&q=82"),
        ("imagem", "Eventos corporativos", "Do encontro da equipe à grande confraternização, faça desse momento uma experiência.", "https://images.unsplash.com/photo-1511578314322-379afb476865?auto=format&fit=crop&w=850&q=82"),
    ],
    "videos": [
        ("video", "Veja como é celebrar com chopp", "Vídeo de eventos da Dona do Chopp.", "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?auto=format&fit=crop&w=950&q=82"),
        ("video", "Chopeira e experiência no evento", "Montagem e serviço de chopp no evento.", "https://images.unsplash.com/photo-1514933651103-005eec06c04b?auto=format&fit=crop&w=950&q=82"),
    ],
    "orcamento": [
        ("conteudo", "Conte sobre o evento", "Data, local, ocasião e quantidade aproximada de convidados.", ""),
        ("conteudo", "Envie sua solicitação", "Preparamos uma mensagem com as informações que você colocou.", ""),
        ("conteudo", "Converse sobre as opções", "A equipe poderá confirmar disponibilidade e apresentar o orçamento.", ""),
    ],
    "faq": [
        ("conteudo", "Como posso pedir orçamento?", "Preencha o formulário com data, local e quantidade de convidados. Ao enviar, você será direcionado ao WhatsApp.", ""),
        ("conteudo", "Vocês atendem que tipos de evento?", "Aniversários, casamentos, confraternizações, eventos corporativos e outras celebrações em Fortaleza e Região Metropolitana.", ""),
        ("conteudo", "Qual o valor para meu evento?", "O valor depende das condições e necessidades do evento. Envie os dados para receber uma proposta personalizada.", ""),
        ("conteudo", "Vocês levam chopeira e equipamentos?", "Informe o que você precisa. A equipe confirmará os itens, a logística e o serviço disponíveis para sua data e região.", ""),
    ],
}


def seed_sections(apps, schema_editor):
    EventPage = apps.get_model("eventos", "EventPage")
    EventSection = apps.get_model("eventos", "EventSection")
    EventMedia = apps.get_model("eventos", "EventMedia")
    page = EventPage.objects.order_by("pk").first()
    if page is None:
        return

    sections = {}
    for section_type, defaults in SECTION_DEFAULTS.items():
        section, _ = EventSection.objects.get_or_create(pagina=page, tipo=section_type, defaults=defaults)
        changed = []
        for field, value in defaults.items():
            if not getattr(section, field) and value:
                setattr(section, field, value)
                changed.append(field)
        if changed:
            section.save(update_fields=changed)
        sections[section_type] = section

    for section_type, items in ITEMS.items():
        section = sections[section_type]
        for order, (media_type, title, description, source) in enumerate(items, start=1):
            defaults = {"media_type": media_type, "descricao": description, "ordem": order, "ativo": True}
            if media_type == "imagem":
                defaults["image_url"] = source
                defaults["legenda"] = title
                defaults["texto_alternativo"] = title
            elif media_type == "video":
                defaults["video_url"] = f"/static/eventos/videos/evento-{order}.mp4"
                defaults["thumbnail_url"] = source
            EventMedia.objects.get_or_create(secao=section, titulo=title, defaults=defaults)


class Migration(migrations.Migration):
    dependencies = [("eventos", "0007_eventmedia_thumbnail_url_alter_eventmedia_image_url_and_more")]
    operations = [migrations.RunPython(seed_sections, migrations.RunPython.noop)]
