import shutil
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from eventos.models import EventMedia, EventPage, EventSection
from eventos.validators import validate_video_size


GIF_BYTES = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
MP4_BYTES = b"\x00\x00\x00\x18ftypmp42\x00\x00\x00\x00mp42isom"


class TemporaryMediaMixin:
    @classmethod
    def setUpClass(cls):
        cls._media_dir = tempfile.mkdtemp()
        cls._media_override = override_settings(MEDIA_ROOT=cls._media_dir)
        cls._media_override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._media_override.disable()
        shutil.rmtree(cls._media_dir, ignore_errors=True)


class EventPageViewTests(TemporaryMediaMixin, TestCase):
    def test_health_endpoint_is_available(self):
        response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_home_serves_prepage(self):
        response = self.client.get(reverse("home"))
        content = b"".join(response.streaming_content).decode()
        self.assertEqual(response.status_code, 200)
        self.assertIn("O que você", content)
        self.assertIn("Fortaleza e Região Metropolitana", content)

    def test_home_uses_shared_logo_and_resets_transition_after_browser_back(self):
        response = self.client.get(reverse("home"))
        content = b"".join(response.streaming_content).decode()
        self.assertIn('/static/brand/logo2.png', content)
        self.assertIn("window.addEventListener('pageshow',resetarTransicao)", content)
        self.assertIn("painel.classList.remove('ativa')", content)
        self.assertIn("const URL_EVENTOS='/eventos/'", content)

    def test_prepage_asset_is_available(self):
        response = self.client.get("/assets/fotoboa1.jpg")
        self.assertEqual(response.status_code, 200)

    def test_prepage_uses_events_clean_environment_image(self):
        response = self.client.get(reverse("home"))
        content = b"".join(response.streaming_content).decode()
        self.assertIn("/static/site/eventos-ambiente-limpo.png", content)

    def test_event_page_returns_200_without_configuration(self):
        EventPage.objects.all().delete()
        response = self.client.get(reverse("eventos:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "O seu evento merece chopp gelado")

    def test_event_page_uses_shared_logo_as_link_back_to_choices(self):
        response = self.client.get(reverse("eventos:index"))
        self.assertContains(response, 'href="/" aria-label="Voltar às escolhas"', count=2)
        self.assertContains(response, "/static/brand/logo2.png", count=2)

    def test_database_content_is_rendered_and_escaped(self):
        page = EventPage.objects.get()
        page.titulo = "Título administrado <script>alert(1)</script>"
        page.descricao = "Descrição do banco"
        page.save()
        about = page.secoes.get(tipo=EventSection.SectionType.ABOUT)
        about.titulo = "Apresentação dinâmica"
        about.descricao = "Texto dinâmico"
        about.save()
        response = self.client.get(reverse("eventos:index"))
        self.assertContains(response, "Título administrado")
        self.assertContains(response, "Apresentação dinâmica")
        self.assertContains(response, "&lt;script&gt;alert(1)&lt;/script&gt;")
        self.assertNotContains(response, "<script>alert(1)</script>")

    def test_only_active_media_is_shown_in_configured_order(self):
        page = EventPage.objects.get()
        events = page.secoes.get(tipo=EventSection.SectionType.EVENTS)
        EventMedia.objects.create(
            secao=events,
            media_type=EventMedia.MediaType.IMAGE,
            imagem=SimpleUploadedFile("segunda.gif", GIF_BYTES, content_type="image/gif"),
            legenda="Segunda imagem",
            ordem=2,
        )
        EventMedia.objects.create(
            secao=events,
            media_type=EventMedia.MediaType.IMAGE,
            imagem=SimpleUploadedFile("primeira.gif", GIF_BYTES, content_type="image/gif"),
            legenda="Primeira imagem",
            ordem=1,
        )
        EventMedia.objects.create(
            secao=events,
            media_type=EventMedia.MediaType.IMAGE,
            imagem=SimpleUploadedFile("oculta.gif", GIF_BYTES, content_type="image/gif"),
            legenda="Imagem oculta",
            ordem=0,
            ativo=False,
        )
        content = self.client.get(reverse("eventos:index")).content.decode()
        self.assertLess(content.index("Primeira imagem"), content.index("Segunda imagem"))
        self.assertNotIn("Imagem oculta", content)

    def test_inactive_page_uses_safe_fallback(self):
        page = EventPage.objects.get()
        page.titulo = "Não publicar"
        page.ativo = False
        page.save()
        response = self.client.get(reverse("eventos:index"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Não publicar")

    def test_seo_metadata_and_event_occasions_are_rendered(self):
        response = self.client.get(reverse("eventos:index"))
        self.assertContains(response, "Chopp para Eventos em Fortaleza–CE | Dona do Chopp")
        self.assertContains(response, 'type="application/ld+json"')
        self.assertContains(response, '"@type":"Service"')
        self.assertContains(response, "batizados")
        self.assertContains(response, "confraternizações")
        self.assertContains(response, "Fortaleza–CE e Região Metropolitana")

    def test_whatsapp_uses_official_number_and_site_source(self):
        response = self.client.get(reverse("eventos:index"))
        self.assertContains(response, "5585991803678")
        self.assertContains(response, "Vim pelo site de eventos da Dona do Chopp")

    def test_standard_sections_are_seeded_and_editable(self):
        page = EventPage.objects.get()
        self.assertTrue(set(EventSection.PUBLIC_TYPES).issubset(set(page.secoes.values_list("tipo", flat=True))))

        events = page.secoes.get(tipo=EventSection.SectionType.EVENTS)
        events.titulo = "Eventos alterados no Admin"
        events.descricao = "Fotos e vídeos administráveis"
        events.save()
        first_item = events.midias.first()
        first_item.titulo = "Card administrável"
        first_item.save()

        response = self.client.get(reverse("eventos:index"))
        self.assertContains(response, "Eventos alterados no Admin")
        self.assertContains(response, "Fotos e vídeos administráveis")
        self.assertContains(response, "Card administrável")

    def test_public_page_hides_inactive_promotion_and_legacy_sections(self):
        response = self.client.get(reverse("eventos:index"))
        self.assertContains(response, 'id="empresa"')
        self.assertContains(response, 'id="marcas"')
        self.assertContains(response, 'id="eventos"')
        self.assertContains(response, 'id="whatsapp"')
        self.assertNotContains(response, 'id="palavras-chave"')
        self.assertNotContains(response, 'id="galeria"')
        self.assertNotContains(response, 'id="videos"')

    def test_promotion_is_hidden_by_default_and_rendered_when_active(self):
        page = EventPage.objects.get()
        promotion = page.secoes.get(tipo=EventSection.SectionType.PROMOTION)
        self.assertFalse(promotion.ativo)
        self.assertNotContains(self.client.get(reverse("eventos:index")), 'id="promocao-')

        promotion.ativo = True
        promotion.valor = "R$ 199,90"
        promotion.descricao = "Descrição da promoção ativa"
        promotion.save(update_fields=("ativo", "valor", "descricao"))

        response = self.client.get(reverse("eventos:index"))
        self.assertContains(response, f'id="promocao-{promotion.pk}"')
        self.assertContains(response, promotion.titulo)
        self.assertContains(response, "R$ 199,90")
        self.assertContains(response, "Descrição da promoção ativa")
        self.assertContains(response, f'href="https://wa.me/5585991803678?text=')
        self.assertContains(response, 'target="_blank"')

    def test_multiple_promotions_render_with_text_photo_and_video(self):
        page = EventPage.objects.get()
        first = page.secoes.get(tipo=EventSection.SectionType.PROMOTION)
        first.titulo = "Primeira promoção"
        first.ativo = True
        first.ordem = 4
        first.save()
        second = EventSection.objects.create(
            pagina=page,
            tipo=EventSection.SectionType.PROMOTION,
            chamada="SEGUNDA OFERTA",
            titulo="Segunda promoção",
            valor="Consulte",
            descricao="Condição especial",
            ordem=5,
            ativo=True,
        )
        text = EventMedia.objects.create(
            secao=second,
            media_type=EventMedia.MediaType.CONTENT,
            titulo="Texto promocional",
            descricao="Detalhes da oferta",
            ordem=1,
        )
        photo = EventMedia.objects.create(
            secao=second,
            media_type=EventMedia.MediaType.IMAGE,
            titulo="Foto promocional",
            imagem=SimpleUploadedFile("promocao.gif", GIF_BYTES, content_type="image/gif"),
            ordem=2,
        )
        video = EventMedia.objects.create(
            secao=second,
            media_type=EventMedia.MediaType.VIDEO,
            titulo="Vídeo promocional",
            video_file=SimpleUploadedFile("promocao.mp4", MP4_BYTES, content_type="video/mp4"),
            ordem=3,
        )
        EventMedia.objects.create(
            secao=second,
            media_type=EventMedia.MediaType.CONTENT,
            ordem=4,
        )

        content = self.client.get(reverse("eventos:index")).content.decode()

        self.assertLess(content.index(first.titulo), content.index(second.titulo))
        self.assertIn('class="promotion-card"', content)
        self.assertIn('class="promotion-visual"', content)
        self.assertIn('class="promotion-note"', content)
        self.assertIn(text.titulo, content)
        self.assertIn(photo.titulo, content)
        self.assertIn(video.titulo, content)
        self.assertIn(photo.image_source, content)
        self.assertIn(video.video_source, content)
        self.assertIn('type="video/mp4"', content)

    def test_deleted_or_inactive_standard_section_is_not_rendered(self):
        page = EventPage.objects.get()
        about = page.secoes.get(tipo=EventSection.SectionType.ABOUT)
        about.titulo = "Empresa que deve desaparecer"
        about.save()
        about.delete()

        brands = page.secoes.get(tipo=EventSection.SectionType.BRANDS)
        brands.titulo = "Marcas que devem desaparecer"
        brands.ativo = False
        brands.save()

        response = self.client.get(reverse("eventos:index"))
        self.assertNotContains(response, "Empresa que deve desaparecer")
        self.assertNotContains(response, "Marcas que devem desaparecer")
        self.assertNotContains(response, 'href="#empresa"')
        self.assertNotContains(response, 'href="#marcas"')

    def test_uploaded_brand_image_is_rendered(self):
        page = EventPage.objects.get()
        brands = page.secoes.get(tipo=EventSection.SectionType.BRANDS)
        brand = brands.midias.first()
        brand.titulo = "Marca com imagem cadastrada"
        brand.media_type = EventMedia.MediaType.IMAGE
        brand.imagem = SimpleUploadedFile("marca.gif", GIF_BYTES, content_type="image/gif")
        brand.save()

        response = self.client.get(reverse("eventos:index"))
        self.assertContains(response, "Marca com imagem cadastrada")
        self.assertContains(response, brand.image_source)
        self.assertContains(response, 'class="brand-media-frame"')
        self.assertContains(response, 'class="brand-media"')
        self.assertContains(response, "--brand-bg:url(")

    def test_brand_without_image_uses_local_example(self):
        response = self.client.get(reverse("eventos:index"))
        self.assertContains(response, "/static/eventos/bomba-dona-do-chopp.png")

    def test_available_video_uses_dynamic_filefield_url(self):
        page = EventPage.objects.get()
        events = page.secoes.get(tipo=EventSection.SectionType.EVENTS)
        video = EventMedia.objects.create(
            secao=events,
            media_type=EventMedia.MediaType.VIDEO,
            titulo="Vídeo enviado pelo Admin",
            video_file=SimpleUploadedFile("video-admin.mp4", MP4_BYTES, content_type="video/mp4"),
            ordem=99,
        )

        response = self.client.get(reverse("eventos:index"))
        self.assertContains(response, video.video_file.url)
        self.assertContains(response, 'type="video/mp4"')
        self.assertContains(response, "playsinline")
        self.assertNotContains(response, "evento-1.mp4 na pasta assets/videos")
        self.assertNotContains(response, "method:'HEAD'")

    def test_unavailable_video_has_inline_message_without_play_button(self):
        page = EventPage.objects.get()
        events = page.secoes.get(tipo=EventSection.SectionType.EVENTS)
        EventMedia.objects.create(
            secao=events,
            media_type=EventMedia.MediaType.VIDEO,
            titulo="Vídeo sem arquivo",
            ordem=100,
        )

        response = self.client.get(reverse("eventos:index"))
        self.assertContains(response, "Vídeo ainda não disponível.")
        self.assertNotContains(response, 'aria-label="Reproduzir Vídeo sem arquivo"')

    def test_video_upload_persists_field_and_storage_object(self):
        page = EventPage.objects.get()
        events = page.secoes.get(tipo=EventSection.SectionType.EVENTS)
        video = EventMedia(
            secao=events,
            media_type=EventMedia.MediaType.VIDEO,
            titulo="Persistência real",
            video_file=SimpleUploadedFile("persistencia.m4v", MP4_BYTES, content_type="video/mp4"),
        )
        video.full_clean()
        video.save()
        video.refresh_from_db()

        self.assertTrue(video.video_file.name.endswith(".m4v"))
        self.assertTrue(video.video_file.storage.exists(video.video_file.name))
        self.assertEqual(video.video_content_type, "video/mp4")


class ModelValidationTests(TemporaryMediaMixin, TestCase):
    def test_only_one_page_configuration_is_allowed(self):
        with self.assertRaises(ValidationError):
            EventPage(titulo="Segunda").full_clean()

    def test_invalid_cta_destination_is_rejected(self):
        page = EventPage.objects.get()
        page.hero_cta_url = "javascript:alert(1)"
        with self.assertRaises(ValidationError) as context:
            page.full_clean()
        self.assertIn("hero_cta_url", context.exception.message_dict)

    def test_promotions_can_repeat_but_structural_sections_remain_unique(self):
        page = EventPage.objects.get()
        EventSection.objects.create(
            pagina=page,
            tipo=EventSection.SectionType.PROMOTION,
            titulo="Outra promoção",
            ativo=False,
        )
        self.assertEqual(page.secoes.filter(tipo=EventSection.SectionType.PROMOTION).count(), 2)

        duplicate_about = EventSection(
            pagina=page,
            tipo=EventSection.SectionType.ABOUT,
            titulo="Outra empresa",
        )
        with self.assertRaises(ValidationError):
            duplicate_about.full_clean()

    def test_promotion_whatsapp_url_contains_encoded_promotion_data(self):
        page = EventPage.objects.get()
        promotion = page.secoes.get(tipo=EventSection.SectionType.PROMOTION)
        promotion.titulo = "Chopp & festa"
        promotion.valor = "R$ 120"
        promotion.descricao = "Condição especial para o evento."

        parsed = urlparse(promotion.promotion_whatsapp_url)
        message = parse_qs(parsed.query)["text"][0]

        self.assertEqual(parsed.netloc, "wa.me")
        self.assertEqual(parsed.path, "/5585991803678")
        self.assertIn("*Promoção:* Chopp & festa", message)
        self.assertIn("*Valor:* R$ 120", message)
        self.assertIn("*Detalhes:* Condição especial para o evento.", message)

        promotion.valor = "120"
        self.assertEqual(promotion.promotion_display_value, "R$ 120")
        self.assertIn("*Valor:* R$ 120", parse_qs(urlparse(promotion.promotion_whatsapp_url).query)["text"][0])

    def test_image_requires_an_image_file(self):
        page = EventPage.objects.get()
        section = page.secoes.get(tipo=EventSection.SectionType.GALLERY)
        media = EventMedia(secao=section, media_type=EventMedia.MediaType.IMAGE)
        with self.assertRaises(ValidationError):
            media.full_clean()

    def test_video_requires_exactly_one_source(self):
        page = EventPage.objects.get()
        section = page.secoes.get(tipo=EventSection.SectionType.VIDEOS)
        media = EventMedia(secao=section, media_type=EventMedia.MediaType.VIDEO)
        with self.assertRaises(ValidationError):
            media.full_clean()

    def test_gallery_rejects_video_media(self):
        page = EventPage.objects.get()
        section = page.secoes.get(tipo=EventSection.SectionType.GALLERY)
        media = EventMedia(
            secao=section,
            media_type=EventMedia.MediaType.VIDEO,
            video_url="https://example.com/evento.mp4",
        )
        with self.assertRaises(ValidationError) as context:
            media.full_clean()
        self.assertIn("media_type", context.exception.message_dict)

    def test_text_only_item_is_valid_outside_media_galleries(self):
        page = EventPage.objects.get()
        section = page.secoes.get(tipo=EventSection.SectionType.FAQ)
        item = EventMedia(
            secao=section,
            media_type=EventMedia.MediaType.CONTENT,
            titulo="Pergunta",
            descricao="Resposta",
        )
        item.full_clean()

    @override_settings(MEDIA_MAX_UPLOAD_SIZE=8)
    def test_video_size_uses_configured_limit(self):
        upload = SimpleUploadedFile("grande.mp4", b"123456789", content_type="video/mp4")
        with self.assertRaises(ValidationError):
            validate_video_size(upload)


class AdminTests(TestCase):
    def setUp(self):
        self.page = EventPage.objects.get()
        self.page.titulo = "Título original"
        self.page.save()
        user_model = get_user_model()
        self.regular_user = user_model.objects.create_user(username="comum", password="senha-forte-123")
        self.admin_user = user_model.objects.create_superuser(username="admin", email="admin@example.com", password="senha-forte-123")

    def test_regular_user_cannot_access_admin_change(self):
        self.client.force_login(self.regular_user)
        response = self.client.get(reverse("admin:eventos_eventpage_change", args=(self.page.pk,)))
        self.assertEqual(response.status_code, 302)

    def test_admin_can_add_and_delete_standard_sections(self):
        self.client.force_login(self.admin_user)
        about = self.page.secoes.get(tipo=EventSection.SectionType.ABOUT)
        delete_response = self.client.get(reverse("admin:eventos_eventsection_delete", args=(about.pk,)))
        self.assertEqual(delete_response.status_code, 200)
        confirmed_delete = self.client.post(
            reverse("admin:eventos_eventsection_delete", args=(about.pk,)),
            {"post": "yes"},
        )
        self.assertEqual(confirmed_delete.status_code, 302)
        self.assertFalse(EventSection.objects.filter(pk=about.pk).exists())

        add_response = self.client.get(reverse("admin:eventos_eventsection_add"))
        self.assertEqual(add_response.status_code, 200)
        self.assertContains(add_response, "Sobre a empresa")
        self.assertContains(add_response, ">Promoção<")
        self.assertNotContains(add_response, ">Marcas de chopp<")
        self.assertNotContains(add_response, ">Dúvidas frequentes<")

    def test_admin_section_list_hides_legacy_sections(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse("admin:eventos_eventsection_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sobre a empresa")
        self.assertContains(response, "Marcas de chopp")
        self.assertContains(response, "Eventos — fotos e vídeos")
        self.assertContains(response, "Promoção")
        self.assertNotContains(response, "Palavras-chave")
        self.assertNotContains(response, "Galeria de fotos")
        self.assertNotContains(response, ">Vídeos<")
        self.assertNotContains(response, "Dúvidas frequentes")
        self.assertNotContains(response, "Tipos de evento")

    def test_admin_hides_technical_page_fields(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse("admin:eventos_eventpage_change", args=(self.page.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'name="hero_cta_url"')
        self.assertNotContains(response, 'name="seo_title"')
        self.assertNotContains(response, 'name="ativo"')
        self.assertContains(response, "1920 × 1080 px")
        self.assertContains(response, "MP4 com vídeo H.264 e áudio AAC")

    def test_events_admin_combines_photo_and_video_fields(self):
        self.client.force_login(self.admin_user)
        events = self.page.secoes.get(tipo=EventSection.SectionType.EVENTS)
        response = self.client.get(reverse("admin:eventos_eventsection_change", args=(events.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="midias-0-media_type"')
        self.assertContains(response, 'name="midias-0-imagem"')
        self.assertContains(response, 'name="midias-0-video_file"')
        self.assertContains(response, 'name="midias-0-thumbnail"')
        self.assertNotContains(response, 'name="tipo"')
        self.assertNotContains(response, 'name="pagina"')

    def test_promotion_admin_has_value_and_rich_content_fields(self):
        self.client.force_login(self.admin_user)
        promotion = self.page.secoes.get(tipo=EventSection.SectionType.PROMOTION)
        response = self.client.get(reverse("admin:eventos_eventsection_change", args=(promotion.pk,)))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="valor"')
        self.assertContains(response, 'name="ordem"')
        self.assertContains(response, 'name="midias-0-media_type"')
        self.assertContains(response, 'name="midias-0-imagem"')
        self.assertContains(response, 'name="midias-0-video_file"')
        self.assertContains(response, ">Texto<")
        self.assertContains(response, ">Foto<")
        self.assertContains(response, ">Vídeo<")
        self.assertContains(response, "Botão do WhatsApp")
        self.assertNotContains(response, 'name="cta_url"')

    def test_legacy_section_is_not_available_in_simplified_admin(self):
        self.client.force_login(self.admin_user)
        occasions = self.page.secoes.get(tipo=EventSection.SectionType.OCCASIONS)
        response = self.client.get(reverse("admin:eventos_eventsection_change", args=(occasions.pk,)))
        self.assertEqual(response.status_code, 302)

    def test_brand_admin_only_shows_simple_brand_fields(self):
        self.client.force_login(self.admin_user)
        brands = self.page.secoes.get(tipo=EventSection.SectionType.BRANDS)
        response = self.client.get(reverse("admin:eventos_eventsection_change", args=(brands.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="midias-0-titulo"')
        self.assertContains(response, 'name="midias-0-descricao"')
        self.assertContains(response, 'name="midias-0-imagem"')
        self.assertContains(response, "Imagem ou logo")
        self.assertContains(response, "Visível")
        self.assertNotContains(response, 'name="midias-0-media_type"')
        self.assertNotContains(response, 'name="midias-0-video_file"')

    def test_whatsapp_admin_only_shows_text_and_button(self):
        self.client.force_login(self.admin_user)
        whatsapp = self.page.secoes.get(tipo=EventSection.SectionType.WHATSAPP)
        response = self.client.get(reverse("admin:eventos_eventsection_change", args=(whatsapp.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="cta_text"')
        self.assertContains(response, 'name="cta_url"')
        self.assertContains(response, "Visível na página")
        self.assertNotContains(response, 'name="midias-0-titulo"')
        self.assertNotContains(response, 'name="conteudo_extra"')

    def test_admin_can_change_title_and_public_page_reflects_it(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(
            reverse("admin:eventos_eventpage_change", args=(self.page.pk,)),
            {
                "titulo": "Título alterado no Admin",
                "subtitulo": self.page.subtitulo,
                "descricao": "Descrição atualizada",
                "hero_cta_text": self.page.hero_cta_text,
                "hero_cta_url": self.page.hero_cta_url,
                "secondary_cta_text": self.page.secondary_cta_text,
                "secondary_cta_url": self.page.secondary_cta_url,
                "seo_title": self.page.seo_title,
                "seo_description": self.page.seo_description,
                "ativo": "on",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertContains(self.client.get(reverse("eventos:index")), "Título alterado no Admin")


class MediaSyncCommandTests(TestCase):
    def test_dry_run_plans_assets_without_uploading(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            assets = root / "assets"
            media = root / "media"
            assets.mkdir()
            media.mkdir()
            (assets / "foto.jpg").write_bytes(GIF_BYTES)
            (assets / "foto.jpg:Zone.Identifier").write_text("metadata")
            with override_settings(BASE_DIR=root, MEDIA_ROOT=media, GCS_ENABLED=True):
                with patch("eventos.management.commands.sync_media_to_gcs.default_storage.exists", return_value=False), patch(
                    "eventos.management.commands.sync_media_to_gcs.default_storage.save"
                ) as save:
                    call_command("sync_media_to_gcs")
                    save.assert_not_called()
