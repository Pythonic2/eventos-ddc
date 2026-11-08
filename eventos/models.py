from pathlib import Path

from django.core.exceptions import ValidationError
from django.db import models

from .validators import (
    media_upload_path,
    validate_destination,
    validate_image_extension,
    validate_image_size,
    validate_video_extension,
    validate_video_size,
)


class EventPage(models.Model):
    titulo = models.CharField("título principal", max_length=180, default="O seu evento merece chopp gelado e muita comemoração.")
    subtitulo = models.CharField("chamada superior", max_length=100, default="Chopp para eventos")
    descricao = models.TextField("descrição principal", blank=True)
    hero_image = models.ImageField(
        "imagem do hero",
        upload_to="eventos/hero/",
        blank=True,
        validators=[validate_image_extension, validate_image_size],
        help_text="Tamanho ideal: 1920 × 1080 px (proporção 16:9). Outros tamanhos são aceitos e exibidos inteiros, sem distorção.",
    )
    hero_video = models.FileField(
        "vídeo do hero",
        upload_to="eventos/hero/",
        blank=True,
        validators=[validate_video_extension, validate_video_size],
        help_text="Use preferencialmente MP4 com vídeo H.264 e áudio AAC. Também são aceitos M4V, WebM, OGG e MOV; o vídeo será exibido sem cortes.",
    )
    hero_cta_text = models.CharField("texto do botão principal", max_length=80, default="Quero chopp no meu evento")
    hero_cta_url = models.CharField("destino do botão principal", max_length=500, default="#whatsapp", validators=[validate_destination])
    secondary_cta_text = models.CharField("texto do botão secundário", max_length=80, default="Ver como fica", blank=True)
    secondary_cta_url = models.CharField("destino do botão secundário", max_length=500, default="#eventos", blank=True, validators=[validate_destination])
    seo_title = models.CharField("título para buscadores", max_length=180, default="Chopp para seu evento | Dona do Chopp")
    seo_description = models.CharField("descrição para buscadores", max_length=320, blank=True)
    ativo = models.BooleanField("página publicada", default=True)
    atualizado_em = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "página de eventos"
        verbose_name_plural = "página de eventos"

    def clean(self):
        if not self.pk and EventPage.objects.exists():
            raise ValidationError("Já existe uma página de eventos. Edite o registro existente.")
        if self.hero_image and self.hero_video:
            raise ValidationError("Escolha uma imagem ou um vídeo para o hero, não os dois.")

    def __str__(self):
        return "Página de eventos"

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class EventSection(models.Model):
    class SectionType(models.TextChoices):
        ABOUT = "empresa", "Sobre a empresa"
        BRANDS = "marcas", "Marcas de chopp"
        EVENTS = "eventos", "Eventos — fotos e vídeos"
        KEYWORDS = "palavras_chave", "Palavras-chave"
        PRESENTATION = "apresentacao", "Vantagens"
        GALLERY = "galeria", "Galeria de fotos"
        OCCASIONS = "ocasioes", "Tipos de evento"
        LOCATION = "localizacao", "Fortaleza e Região Metropolitana"
        VIDEOS = "videos", "Vídeos"
        FINAL_CTA = "cta_final", "Chamada final"
        BUDGET = "orcamento", "Orçamento"
        FAQ = "faq", "Dúvidas frequentes"
        WHATSAPP = "whatsapp", "Contato pelo WhatsApp"

    PUBLIC_TYPES = (
        SectionType.ABOUT,
        SectionType.BRANDS,
        SectionType.EVENTS,
        SectionType.WHATSAPP,
    )

    pagina = models.ForeignKey(EventPage, on_delete=models.CASCADE, related_name="secoes", verbose_name="página")
    tipo = models.CharField("tipo de seção", max_length=20, choices=SectionType.choices)
    chamada = models.CharField("chamada superior", max_length=120, blank=True, help_text="Texto pequeno exibido acima do título da seção.")
    titulo = models.CharField("título", max_length=180)
    subtitulo = models.CharField("subtítulo", max_length=240, blank=True)
    descricao = models.TextField("texto principal", blank=True)
    conteudo_extra = models.TextField("texto complementar", blank=True)
    ordem = models.PositiveSmallIntegerField("ordem", default=0)
    ativo = models.BooleanField("ativo", default=True)
    cta_text = models.CharField("texto do botão", max_length=80, blank=True)
    cta_url = models.CharField("destino do botão", max_length=500, blank=True, validators=[validate_destination])

    class Meta:
        verbose_name = "seção da página"
        verbose_name_plural = "seções da página"
        ordering = ("ordem", "id")
        constraints = [models.UniqueConstraint(fields=("pagina", "tipo"), name="unique_event_section_type")]

    def __str__(self):
        return f"{self.get_tipo_display()}: {self.titulo}"


class EventMedia(models.Model):
    class MediaType(models.TextChoices):
        CONTENT = "conteudo", "Somente texto"
        IMAGE = "imagem", "Imagem"
        VIDEO = "video", "Vídeo"

    secao = models.ForeignKey(EventSection, on_delete=models.CASCADE, related_name="midias", verbose_name="seção")
    media_type = models.CharField("tipo de mídia", max_length=10, choices=MediaType.choices)
    titulo = models.CharField("título", max_length=160, blank=True)
    descricao = models.TextField("descrição", blank=True)
    imagem = models.ImageField(
        "imagem",
        upload_to=media_upload_path,
        blank=True,
        validators=[validate_image_extension, validate_image_size],
        help_text="Tamanho ideal para a galeria: 1600 × 1200 px (proporção 4:3). Fotos horizontais, verticais ou quadradas serão exibidas inteiras, sem deformação.",
    )
    image_url = models.CharField(
        "URL da imagem atual",
        max_length=500,
        blank=True,
        validators=[validate_destination],
        help_text="Opcional. Permite manter uma imagem externa até ela ser substituída por um upload.",
    )
    video_file = models.FileField(
        "arquivo de vídeo",
        upload_to=media_upload_path,
        blank=True,
        validators=[validate_video_extension, validate_video_size],
        help_text="Use preferencialmente MP4 com vídeo H.264 e áudio AAC. Também são aceitos M4V, WebM, OGG e MOV; a reprodução não cortará o vídeo.",
    )
    video_url = models.CharField("URL do vídeo", max_length=500, blank=True, validators=[validate_destination])
    thumbnail = models.ImageField(
        "imagem de capa",
        upload_to="eventos/capas/",
        blank=True,
        validators=[validate_image_extension, validate_image_size],
        help_text="Tamanho ideal: 1280 × 720 px (proporção 16:9). A capa será ajustada inteira, sem cortes.",
    )
    thumbnail_url = models.CharField(
        "URL da capa atual",
        max_length=500,
        blank=True,
        validators=[validate_destination],
        help_text="Opcional. Permite manter uma capa externa até ela ser substituída por upload.",
    )
    legenda = models.CharField("legenda", max_length=180, blank=True)
    texto_alternativo = models.CharField("texto alternativo", max_length=220, blank=True)
    ordem = models.PositiveSmallIntegerField("ordem", default=0)
    ativo = models.BooleanField("ativo", default=True)

    class Meta:
        verbose_name = "foto ou vídeo"
        verbose_name_plural = "fotos e vídeos"
        ordering = ("ordem", "id")

    def clean(self):
        errors = {}
        if self.secao_id:
            expected_type = {
                EventSection.SectionType.GALLERY: self.MediaType.IMAGE,
                EventSection.SectionType.VIDEOS: self.MediaType.VIDEO,
            }.get(self.secao.tipo)
            if expected_type and self.media_type != expected_type:
                errors["media_type"] = f"A seção {self.secao.get_tipo_display()} aceita somente {self.MediaType(expected_type).label.lower()}."
        if self.media_type == self.MediaType.IMAGE:
            if bool(self.imagem) == bool(self.image_url):
                errors["imagem"] = "Envie uma imagem ou informe uma URL de imagem, mas não ambos."
            if self.video_file or self.video_url:
                errors.setdefault("media_type", "Uma imagem não pode conter arquivo ou URL de vídeo.")
        if self.media_type == self.MediaType.VIDEO:
            if bool(self.video_file) == bool(self.video_url):
                errors["video_file"] = "Informe um arquivo de vídeo ou uma URL externa, mas não ambos."
            if self.imagem or self.image_url:
                errors["imagem"] = "Use a imagem de capa para representar o vídeo."
        if self.media_type == self.MediaType.CONTENT and any((self.imagem, self.image_url, self.video_file, self.video_url, self.thumbnail, self.thumbnail_url)):
            errors["media_type"] = "Um item somente de texto não pode conter foto ou vídeo."
        if errors:
            raise ValidationError(errors)

    @property
    def video_source(self):
        return self.video_file.url if self.video_file else self.video_url

    @property
    def video_content_type(self):
        source = self.video_file.name if self.video_file else self.video_url
        extension = Path(source.split("?", 1)[0]).suffix.lower()
        return {
            ".mp4": "video/mp4",
            ".m4v": "video/mp4",
            ".webm": "video/webm",
            ".ogg": "video/ogg",
            ".mov": "video/quicktime",
        }.get(extension, "video/mp4")

    @property
    def image_source(self):
        return self.imagem.url if self.imagem else self.image_url

    @property
    def thumbnail_source(self):
        return self.thumbnail.url if self.thumbnail else self.thumbnail_url

    def __str__(self):
        return self.titulo or self.legenda or f"{self.get_media_type_display()} #{self.pk or 'novo'}"
