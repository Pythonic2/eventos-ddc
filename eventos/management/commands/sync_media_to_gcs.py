from pathlib import Path, PurePosixPath

from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Copia mídias e imagens atuais para o GCS sem sobrescrever objetos."

    def add_arguments(self, parser):
        parser.add_argument("--execute", action="store_true", help="Executa os uploads; o padrão é somente planejar.")

    def _sources(self):
        return (
            (Path(settings.MEDIA_ROOT), PurePosixPath("uploads")),
            (Path(settings.BASE_DIR) / "assets", PurePosixPath("imagens-iniciais")),
        )

    def handle(self, *args, **options):
        if not settings.GCS_ENABLED:
            raise CommandError("GCS_ENABLED precisa ser true para usar este comando.")
        execute = options["execute"]
        pending = uploaded = existing = 0
        for source_root, destination_root in self._sources():
            if not source_root.is_dir():
                continue
            for local_path in sorted(path for path in source_root.rglob("*") if path.is_file()):
                if local_path.name.endswith(":Zone.Identifier"):
                    continue
                relative = PurePosixPath(local_path.relative_to(source_root).as_posix())
                if relative.is_absolute() or ".." in relative.parts:
                    raise CommandError(f"Caminho local inseguro: {relative}")
                destination = str(destination_root / relative)
                if default_storage.exists(destination):
                    existing += 1
                    continue
                pending += 1
                if not execute:
                    self.stdout.write(f"UPLOAD {destination}")
                    continue
                with local_path.open("rb") as stream:
                    stored_name = default_storage.save(destination, File(stream, name=local_path.name))
                if stored_name != destination:
                    raise CommandError(f"O storage alterou o nome de {destination} para {stored_name}.")
                uploaded += 1
                self.stdout.write(self.style.SUCCESS(f"OK {destination}"))
        amount = uploaded if execute else pending
        action = "enviados" if execute else "planejados"
        self.stdout.write(self.style.SUCCESS(f"Concluído: {amount} {action}; {existing} já existentes."))
