import os
import shutil
import logging # Added logging import
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection # Keep connection for potential future use, but remove specific query

from apps.automacao_ipiranga.models import CertificadoVeiculo

logger = logging.getLogger(__name__) # Initialize logger


class Command(BaseCommand):
    """Comando Django para limpar dados de teste de CertificadoVeiculo e arquivos associados."""

    help = "Limpa todos os CertificadoVeiculo e seus arquivos associados."

    def handle(self, *args: Any, **options: Any) -> None:
        """Lógica principal para limpar dados de teste."""
        self.stdout.write(self.style.SUCCESS("Iniciando limpeza de dados de teste..."))

        # Deletar objetos CertificadoVeiculo do banco de dados
        count = CertificadoVeiculo.objects.all().count()
        CertificadoVeiculo.objects.all().delete()
        self.stdout.write(
            self.style.SUCCESS(
                f"Deletados {count} registros de CertificadoVeiculo do banco de dados."
            )
        )

        # Deletar arquivos associados do sistema de arquivos
        media_root = settings.MEDIA_ROOT
        certificados_dir = os.path.join(media_root, "certificados_veiculos")

        if os.path.exists(certificados_dir):
            self.stdout.write(
                self.style.SUCCESS(
                    f"Iniciando a limpeza de arquivos órfãos em {certificados_dir}..."
                )
            )
            for filename in os.listdir(certificados_dir):
                file_path = os.path.join(certificados_dir, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                        self.stdout.write(
                            self.style.SUCCESS(f"Deletado arquivo: {filename}")
                        )
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                        self.stdout.write(
                            self.style.SUCCESS(f"Deletado diretório: {filename}")
                        )
                except OSError as e: # Changed from generic Exception to OSError for file operations
                    logger.error(f"Falha ao deletar {file_path}. Motivo: {e}")
                    self.stderr.write(
                        self.style.ERROR(f"Falha ao deletar {file_path}. Motivo: {e}")
                    )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"Diretório de certificados não encontrado: {certificados_dir}"
                )
            )

        self.stdout.write(self.style.SUCCESS("Limpeza de dados de teste concluída."))
