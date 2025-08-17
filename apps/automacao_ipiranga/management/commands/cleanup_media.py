import os
import logging
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.automacao_ipiranga.models import CertificadoVeiculo

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Deletes all files from the media/certificados_veiculos folder and CertificadoVeiculo records from the database."""

    help = "Deleta todos os arquivos da pasta media/certificados_veiculos e os registros de CertificadoVeiculo no banco de dados."

    def handle(self, *args: Any, **options: Any) -> None:
        """Handles the command execution to clean up media files and database records."""
        self.stdout.write(
            self.style.SUCCESS(
                "Iniciando a limpeza de registros de CertificadoVeiculo e arquivos associados..."
            )
        )

        media_dir = os.path.join(settings.MEDIA_ROOT, "certificados_veiculos")

        # 1. Delete files associated with database records
        # Fetch paths first to avoid issues after deleting records
        file_paths_to_delete = []
        for certificado in CertificadoVeiculo.objects.all():
            if certificado.arquivo and os.path.isfile(certificado.arquivo.path):
                file_paths_to_delete.append(certificado.arquivo.path)

        # 2. Bulk delete CertificadoVeiculo records from the database
        with transaction.atomic():
            deleted_count, _ = CertificadoVeiculo.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(f"  {deleted_count} registros de CertificadoVeiculo deletados do banco de dados.")
            )

        # 3. Delete associated files
        for file_path in file_paths_to_delete:
            try:
                os.remove(file_path)
                self.stdout.write(
                    self.style.SUCCESS(f"  Arquivo {file_path} deletado.")
                )
            except OSError as e:
                logger.error(f"Erro ao deletar arquivo {file_path}: {e}")
                self.stdout.write(
                    self.style.ERROR(f"Erro ao deletar arquivo {file_path}: {e}")
                )

        # 4. Delete any remaining orphaned files in the media directory
        if os.path.exists(media_dir):
            self.stdout.write(
                self.style.SUCCESS(
                    f"Iniciando a limpeza de arquivos órfãos em {media_dir}..."
                )
            )
            for filename in os.listdir(media_dir):
                file_path = os.path.join(media_dir, filename)
                if os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                        self.stdout.write(
                            self.style.SUCCESS(f"  Arquivo órfão {file_path} deletado.")
                        )
                    except OSError as e:
                        logger.error(f"Erro ao deletar arquivo órfão {file_path}: {e}")
                        self.stdout.write(
                            self.style.ERROR(f"Erro ao deletar arquivo órfão {file_path}: {e}")
                        )

        self.stdout.write(self.style.SUCCESS("Limpeza concluída."))
