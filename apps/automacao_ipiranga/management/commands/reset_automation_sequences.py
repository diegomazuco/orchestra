"""Comando Django para resetar sequências de auto-incremento."""

import logging
from typing import Any

from django.core.management.base import BaseCommand
from django.db import connection

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Custom Django management command to reset auto-increment sequences."""

    help = "Resets the auto-increment sequences for automation-related tables."

    def handle(self, *args: str, **options: dict[str, Any]) -> None:
        """Handles the command execution to reset auto-increment sequences."""
        self.stdout.write(
            self.style.SUCCESS("Iniciando o reset das sequências de auto-incremento...")
        )

        tables_to_reset = [
            "automacao_ipiranga_certificadoveiculo",
            "automacao_ipiranga_veiculoipiranga",
        ]

        with connection.cursor() as cursor:
            for table_name in tables_to_reset:
                try:
                    # For SQLite, delete the entry from sqlite_sequence
                    cursor.execute(
                        f"DELETE FROM sqlite_sequence WHERE name='{table_name}';"
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Sequência para a tabela {table_name} resetada com sucesso."
                        )
                    )
                except Exception as e:
                    self.stderr.write(
                        self.style.ERROR(
                            f"Erro ao resetar sequência para a tabela {table_name}: {e}"
                        )
                    )

        self.stdout.write(self.style.SUCCESS("Reset das sequências concluído."))
