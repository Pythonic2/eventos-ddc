from django.db import models
from django.shortcuts import render

from .models import EventMedia, EventPage, EventSection


def event_page(request):
    page = EventPage.objects.filter(ativo=True).first()
    sections = {}
    if page:
        active_media = EventMedia.objects.filter(ativo=True).order_by("ordem", "id")
        queryset = page.secoes.filter(ativo=True, tipo__in=EventSection.PUBLIC_TYPES).prefetch_related(
            models.Prefetch("midias", queryset=active_media)
        )
        sections = {section.tipo: section for section in queryset}
    return render(
        request,
        "eventos/index.html",
        {
            "event_page": page,
            "about_section": sections.get(EventSection.SectionType.ABOUT),
            "brands_section": sections.get(EventSection.SectionType.BRANDS),
            "events_section": sections.get(EventSection.SectionType.EVENTS),
            "whatsapp_section": sections.get(EventSection.SectionType.WHATSAPP),
        },
    )
