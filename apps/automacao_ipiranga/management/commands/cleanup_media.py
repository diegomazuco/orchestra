import logging
import os
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

        with transaction.atomic():
            certificados_ids_to_delete = []
            for certificado in CertificadoVeiculo.objects.all():
                try:
                    if certificado.arquivo and certificado.arquivo.storage.exists(certificado.arquivo.name):
                        certificado.arquivo.delete(save=False)  # Deletes file from storage
                        self.stdout.write(f"  Arquivo {certificado.arquivo.name} de CertificadoVeiculo deletado.")
                    certificados_ids_to_delete.append(certificado.id)
                except Exception as e:
                    logger.error(f"Erro ao deletar arquivo para CertificadoVeiculo ID {certificado.id}: {e}")
                    self.stdout.write(self.style.ERROR(f"Erro ao deletar arquivo para CertificadoVeiculo ID {certificado.id}: {e}"))

            deleted_count, _ = CertificadoVeiculo.objects.filter(id__in=certificados_ids_to_delete).delete()
            self.stdout.write(
                self.style.SUCCESS(f"  {deleted_count} registros de CertificadoVeiculo deletados do banco de dados.")
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
