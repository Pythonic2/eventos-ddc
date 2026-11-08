from django.db import models
from django.shortcuts import render

from .models import EventMedia, EventPage, EventSection


def event_page(request):
    page = EventPage.objects.filter(ativo=True).first()
    sections = {}
    if page:
        active_media = EventMedia.objects.filter(ativo=True).order_by("ordem", "id")
        queryset = page.secoes.filter(ativo=True).prefetch_related(
            models.Prefetch("midias", queryset=active_media)
        )
        sections = {section.tipo: section for section in queryset}
    return render(
        request,
        "eventos/index.html",
        {
            "event_page": page,
            "presentation_section": sections.get(EventSection.SectionType.PRESENTATION),
            "gallery_section": sections.get(EventSection.SectionType.GALLERY),
            "occasions_section": sections.get(EventSection.SectionType.OCCASIONS),
            "location_section": sections.get(EventSection.SectionType.LOCATION),
            "videos_section": sections.get(EventSection.SectionType.VIDEOS),
            "final_cta_section": sections.get(EventSection.SectionType.FINAL_CTA),
            "budget_section": sections.get(EventSection.SectionType.BUDGET),
            "faq_section": sections.get(EventSection.SectionType.FAQ),
        },
    )
