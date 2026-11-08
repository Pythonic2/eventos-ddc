import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from eventos.models import EventMedia, EventPage, EventSection


GIF_BYTES = b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"


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

    def test_prepage_asset_is_available(self):
        response = self.client.get("/assets/fotoboa1.jpg")
        self.assertEqual(response.status_code, 200)

    def test_event_page_returns_200_without_configuration(self):
        EventPage.objects.all().delete()
        response = self.client.get(reverse("eventos:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "O seu evento merece chopp gelado")

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
        gallery = page.secoes.get(tipo=EventSection.SectionType.GALLERY)
        EventMedia.objects.create(
            secao=gallery,
            media_type=EventMedia.MediaType.IMAGE,
            imagem=SimpleUploadedFile("segunda.gif", GIF_BYTES, content_type="image/gif"),
            legenda="Segunda imagem",
            ordem=2,
        )
        EventMedia.objects.create(
            secao=gallery,
            media_type=EventMedia.MediaType.IMAGE,
            imagem=SimpleUploadedFile("primeira.gif", GIF_BYTES, content_type="image/gif"),
            legenda="Primeira imagem",
            ordem=1,
        )
        EventMedia.objects.create(
            secao=gallery,
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
        self.assertContains(response, "Confraternizações")
        self.assertContains(response, "Fortaleza–CE e Região Metropolitana")

    def test_whatsapp_uses_official_number_and_site_source(self):
        response = self.client.get(reverse("eventos:index"))
        self.assertContains(response, "5585991803678")
        self.assertContains(response, "Vim pelo site de eventos da Dona do Chopp")

    def test_standard_sections_are_seeded_and_editable(self):
        page = EventPage.objects.get()
        self.assertTrue(set(EventSection.PUBLIC_TYPES).issubset(set(page.secoes.values_list("tipo", flat=True))))

        keywords = page.secoes.get(tipo=EventSection.SectionType.KEYWORDS)
        keywords.titulo = "Palavras-chave alteradas no Admin"
        keywords.conteudo_extra = "Texto complementar administrável"
        keywords.save()
        first_item = keywords.midias.first()
        first_item.titulo = "Card administrável"
        first_item.save()

        response = self.client.get(reverse("eventos:index"))
        self.assertContains(response, "Palavras-chave alteradas no Admin")
        self.assertContains(response, "Texto complementar administrável")
        self.assertContains(response, "Card administrável")

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

    def test_brand_without_image_uses_local_example(self):
        response = self.client.get(reverse("eventos:index"))
        self.assertContains(response, "/static/eventos/bomba-dona-do-chopp.png")


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
        self.assertNotContains(add_response, ">Marcas de chopp<")
        self.assertNotContains(add_response, ">Dúvidas frequentes<")

    def test_admin_section_list_hides_legacy_sections(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse("admin:eventos_eventsection_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sobre a empresa")
        self.assertContains(response, "Marcas de chopp")
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
        self.assertContains(response, "o vídeo será ajustado sem cortes")

    def test_gallery_admin_shows_media_without_structural_fields(self):
        self.client.force_login(self.admin_user)
        gallery = self.page.secoes.get(tipo=EventSection.SectionType.GALLERY)
        response = self.client.get(reverse("admin:eventos_eventsection_change", args=(gallery.pk,)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="midias-0-imagem"')
        self.assertNotContains(response, 'name="tipo"')
        self.assertNotContains(response, 'name="pagina"')
        self.assertContains(response, "1600 × 1200 px")
        self.assertContains(response, "serão exibidas inteiras, sem deformação")

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
