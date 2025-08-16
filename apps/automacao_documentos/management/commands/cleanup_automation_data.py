import logging

from django.core.management.base import BaseCommand
from django.db import transaction

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Django command to clean up all automation-related data from the database."""

    help = "Cleans up all automation-related data from the database."

    from typing import Any

    def handle(self, *args: Any, **options: Any) -> None:
        """Handles the command execution to clean up automation data."""
        self.stdout.write(
            self.style.SUCCESS("Iniciando limpeza de dados da automação...")
        )

        from apps.automacao_documentos.models import Documento, LogExecucaoAutomacao
        from apps.automacao_ipiranga.models import CertificadoVeiculo, VeiculoIpiranga

        with transaction.atomic():
            # Clear CertificadoVeiculo records
            deleted_certificados, _ = CertificadoVeiculo.objects.all().delete()
            self.stdout.write(
                f"  {deleted_certificados} registros de CertificadoVeiculo deletados."
            )

            # Clear VeiculoIpiranga records
            deleted_veiculos, _ = VeiculoIpiranga.objects.all().delete()
            self.stdout.write(
                f"  {deleted_veiculos} registros de VeiculoIpiranga deletados."
            )

            # Clear LogExecucaoAutomacao records
            deleted_logs, _ = LogExecucaoAutomacao.objects.all().delete()
            self.stdout.write(
                f"  {deleted_logs} registros de LogExecucaoAutomacao deletados."
            )

            # Clear Documento records
            deleted_documentos, _ = Documento.objects.all().delete()
            self.stdout.write(
                f"  {deleted_documentos} registros de Documento deletados."
            )

        self.stdout.write(
            self.style.SUCCESS("Limpeza de dados da automação concluída.")
        )
