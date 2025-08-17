import logging
from typing import Any

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.automacao_documentos.models import Documento, LogExecucaoAutomacao
from apps.automacao_ipiranga.models import CertificadoVeiculo, VeiculoIpiranga

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Django command to clean up all automation-related data from the database."""

    help = "Cleans up all automation-related data from the database."

    def handle(self, *args: Any, **options: Any) -> None:
        """Handles the command execution to clean up automation data."""
        self.stdout.write(
            self.style.SUCCESS("Iniciando limpeza de dados da automação...")
        )

        with transaction.atomic():
            # Clear CertificadoVeiculo records and associated files
            certificados_to_delete = list(CertificadoVeiculo.objects.all())
            deleted_certificados = 0
            for certificado in certificados_to_delete:
                try:
                    if certificado.arquivo and certificado.arquivo.storage.exists(certificado.arquivo.name):
                        certificado.arquivo.delete(save=False)
                        self.stdout.write(f"  Arquivo {certificado.arquivo.name} de CertificadoVeiculo deletado.")
                    certificado.delete()
                    deleted_certificados += 1
                except Exception as e:
                    logger.error(f"Erro ao deletar CertificadoVeiculo ID {certificado.id} ou seu arquivo: {e}")
            self.stdout.write(
                f"  {deleted_certificados} registros de CertificadoVeiculo deletados."
            )

            # Clear VeiculoIpiranga records
            try:
                deleted_veiculos, _ = VeiculoIpiranga.objects.all().delete()
                self.stdout.write(
                    f"  {deleted_veiculos} registros de VeiculoIpiranga deletados."
                )
            except Exception as e:
                logger.error(f"Erro ao deletar registros de VeiculoIpiranga: {e}")

            # Clear LogExecucaoAutomacao records
            try:
                deleted_logs, _ = LogExecucaoAutomacao.objects.all().delete()
                self.stdout.write(
                    f"  {deleted_logs} registros de LogExecucaoAutomacao deletados."
                )
            except Exception as e:
                logger.error(f"Erro ao deletar registros de LogExecucaoAutomacao: {e}")

            # Clear Documento records and associated files
            documentos_to_delete = list(Documento.objects.all())
            deleted_documentos = 0
            for documento in documentos_to_delete:
                try:
                    if documento.arquivo_pdf and documento.arquivo_pdf.storage.exists(documento.arquivo_pdf.name):
                        documento.arquivo_pdf.delete(save=False)
                        self.stdout.write(f"  Arquivo {documento.arquivo_pdf.name} de Documento deletado.")
                    documento.delete()
                    deleted_documentos += 1
                except Exception as e:
                    logger.error(f"Erro ao deletar Documento ID {documento.id} ou seu arquivo: {e}")
            self.stdout.write(
                f"  {deleted_documentos} registros de Documento deletados."
            )

        self.stdout.write(
            self.style.SUCCESS("Limpeza de dados da automação concluída.")
        )
