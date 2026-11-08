from django.contrib import admin
from django import forms
from django.utils.html import format_html

from .models import EventMedia, EventPage, EventSection


class EventMediaInlineForm(forms.ModelForm):
    class Meta:
        model = EventMedia
        exclude = ("media_type",)

    def clean(self):
        cleaned_data = super().clean()
        section = getattr(self.instance, "secao", None)
        if section:
            self.instance.media_type = (
                EventMedia.MediaType.VIDEO
                if section.tipo == EventSection.SectionType.VIDEOS
                else EventMedia.MediaType.IMAGE
            )
        return cleaned_data


class TextMediaInlineForm(forms.ModelForm):
    class Meta:
        model = EventMedia
        exclude = ("media_type",)

    def clean(self):
        cleaned_data = super().clean()
        self.instance.media_type = EventMedia.MediaType.CONTENT
        return cleaned_data


MEDIA_INLINE_FIELDS = (
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
    "ordem",
    "ativo",
)


class EventMediaInline(admin.StackedInline):
    model = EventMedia
    extra = 1
    fields = MEDIA_INLINE_FIELDS
    classes = ("collapse",)


class ImageMediaInline(EventMediaInline):
    form = EventMediaInlineForm
    fields = tuple(field for field in MEDIA_INLINE_FIELDS if field != "media_type")


class VideoMediaInline(ImageMediaInline):
    pass


class TextMediaInline(EventMediaInline):
    form = TextMediaInlineForm
    fields = ("titulo", "descricao", "ordem", "ativo")
    classes = ()


class BrandMediaInline(TextMediaInline):
    verbose_name = "marca"
    verbose_name_plural = "marcas"


class KeywordMediaInline(TextMediaInline):
    verbose_name = "palavra-chave"
    verbose_name_plural = "palavras-chave"


@admin.register(EventPage)
class EventPageAdmin(admin.ModelAdmin):
    list_display = ("__str__", "atualizado_em", "hero_preview")
    search_fields = ("titulo", "subtitulo", "descricao")
    readonly_fields = ("atualizado_em", "hero_preview")
    fieldsets = (
        ("Atualização", {"fields": ("atualizado_em",)}),
        ("Hero", {"fields": ("subtitulo", "titulo", "descricao", "hero_image", "hero_video", "hero_preview")}),
    )

    @admin.display(description="Prévia")
    def hero_preview(self, obj):
        if obj and obj.hero_image:
            return format_html('<img src="{}" alt="" style="height:100px;width:180px;object-fit:contain;background:#21130c;border-radius:8px">', obj.hero_image.url)
        return "Sem imagem"

    def has_add_permission(self, request):
        return not EventPage.objects.exists() and super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(EventSection)
class EventSectionAdmin(admin.ModelAdmin):
    list_display = ("titulo", "tipo", "ativo")
    list_filter = ("ativo",)
    search_fields = ("titulo", "descricao")
    ordering = ("ordem", "id")
    inlines = (EventMediaInline,)

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return (("Nova seção", {"fields": ("tipo", "titulo")}),)
        content_fields = ("chamada", "titulo", "descricao")
        if obj.tipo == EventSection.SectionType.ABOUT:
            content_fields += ("conteudo_extra",)
        if obj.tipo == EventSection.SectionType.WHATSAPP:
            return (
                ("Texto", {"fields": content_fields}),
                ("Botão do WhatsApp", {"fields": ("cta_text", "cta_url")}),
                ("Exibição", {"fields": ("ativo",)}),
            )
        return (
            ("Texto", {"fields": content_fields}),
            ("Exibição", {"fields": ("ativo",)}),
        )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(tipo__in=EventSection.PUBLIC_TYPES)

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if db_field.name == "tipo":
            existing_types = set(EventSection.objects.filter(tipo__in=EventSection.PUBLIC_TYPES).values_list("tipo", flat=True))
            kwargs["choices"] = [
                choice for choice in EventSection.SectionType.choices
                if choice[0] in EventSection.PUBLIC_TYPES and choice[0] not in existing_types
            ]
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def get_inlines(self, request, obj):
        if obj and obj.tipo == EventSection.SectionType.BRANDS:
            return (BrandMediaInline,)
        if obj and obj.tipo == EventSection.SectionType.KEYWORDS:
            return (KeywordMediaInline,)
        if obj and obj.tipo == EventSection.SectionType.GALLERY:
            return (ImageMediaInline,)
        if obj and obj.tipo == EventSection.SectionType.VIDEOS:
            return (VideoMediaInline,)
        return ()

    def has_add_permission(self, request):
        existing_types = set(EventSection.objects.filter(tipo__in=EventSection.PUBLIC_TYPES).values_list("tipo", flat=True))
        return bool(EventPage.objects.exists() and set(EventSection.PUBLIC_TYPES) - existing_types) and super().has_add_permission(request)

    def save_model(self, request, obj, form, change):
        if not obj.pagina_id:
            obj.pagina = EventPage.objects.first()
        super().save_model(request, obj, form, change)

admin.site.site_header = "Dona do Chopp — Administração"
admin.site.site_title = "Dona do Chopp"
admin.site.index_title = "Conteúdo do site"
