import asyncio
import logging
from argparse import ArgumentParser
from typing import Any

from django.core.management.base import BaseCommand, CommandError

from apps.common.services import extract_text_from_pdf_image

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Comando para testar a extração de texto OCR de um PDF específico."""

    help = "Testa a extração de texto OCR de um arquivo PDF e verifica a presença de informações específicas."

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Adiciona argumentos ao comando."""
        parser.add_argument(
            "pdf_path",
            type=str,
            help="O caminho completo para o arquivo PDF a ser testado.",
        )
        parser.add_argument(
            "--timeout",
            type=int,
            default=60,  # Default timeout of 60 seconds
            help="Tempo limite em segundos para a execução do OCR.",
        )

    async def handle_async(
        self, *args: Any, **options: Any
    ) -> None:  # Added type hints
        """Executa o comando de forma assíncrona para testar a extração de OCR."""
        pdf_path: str = options["pdf_path"]  # Added type hint
        timeout: int = options["timeout"]  # Added type hint
        self.stdout.write(
            self.style.SUCCESS(
                f"Iniciando teste de OCR para: {pdf_path} com timeout de {timeout} segundos."
            )
        )

        try:
            extracted_text: str = await asyncio.wait_for(  # Added type hint
                asyncio.to_thread(extract_text_from_pdf_image, pdf_path, logger),
                timeout=timeout,
            )

            self.stdout.write(self.style.SUCCESS("\n--- Texto Extraído ---"))
            self.stdout.write(extracted_text)
            self.stdout.write(self.style.SUCCESS("--- Fim do Texto Extraído ---\n"))

            # Valores a serem encontrados
            numero_documento = "A760379"
            data_vencimento = "05/FEV/26"

            # Limpeza e normalização do texto para busca
            # Remove espaços e converte para maiúsculas para uma busca mais robusta
            cleaned_text = "".join(extracted_text.split()).upper()

            # Verificação
            numero_encontrado = numero_documento in cleaned_text
            data_encontrada = data_vencimento in cleaned_text

            self.stdout.write(self.style.SUCCESS("--- Resultados da Verificação ---"))
            if numero_encontrado:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  [OK] Número do documento '{numero_documento}' encontrado."
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"  [FALHA] Número do documento '{numero_documento}' NÃO encontrado."
                    )
                )

            if data_encontrada:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  [OK] Data de vencimento '{data_vencimento}' encontrada."
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f"  [FALHA] Data de vencimento '{data_vencimento}' NÃO encontrada."
                    )
                )

        except TimeoutError:  # Changed TimeoutError to asyncio.TimeoutError
            self.stderr.write(
                self.style.ERROR(f"O OCR excedeu o tempo limite de {timeout} segundos.")
            )
            raise CommandError(
                f"O OCR excedeu o tempo limite de {timeout} segundos."
            ) from None
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Ocorreu um erro durante o teste: {e}"))
            raise CommandError(f"Erro durante o teste de OCR: {e}") from e

    def handle(self, *args: Any, **options: Any) -> None:  # Added type hints
        """Executa o comando de automação de forma síncrona, chamando a versão assíncrona."""
        asyncio.run(self.handle_async(*args, **options))
