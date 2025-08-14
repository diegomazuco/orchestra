import logging
import os
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.common.services import extract_cipp_data, extract_text_from_pdf_image

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Comando Django para testar a extração de texto e dados de um PDF usando OCR."""

    help = "Testa a extração de texto e dados de um PDF usando OCR."

    def handle(self, *args, **options):
        """Executa o comando para testar a extração de OCR."""
        self.stdout.write(self.style.SUCCESS("Iniciando teste de extração de OCR..."))

        pdf_path = Path(
            os.path.join(
                os.getcwd(), "media", "certificados_veiculos", "FJX1217_CIPP.pdf"
            )
        )

        if not pdf_path.exists():
            raise CommandError(f"Arquivo PDF não encontrado: {pdf_path}")

        self.stdout.write(f"Tentando extrair texto do PDF: {pdf_path}")

        try:
            pdf_text = extract_text_from_pdf_image(str(pdf_path), logger)
            self.stdout.write(self.style.SUCCESS("Texto extraído com sucesso!"))
            self.stdout.write("--- Conteúdo do PDF (primeiros 1000 caracteres) ---")
            self.stdout.write(pdf_text[:1000])
            self.stdout.write("----------------------------------------------------")

            self.stdout.write("Tentando extrair dados CIPP...")
            numero_documento, vencimento = extract_cipp_data(pdf_text, logger)
            self.stdout.write(self.style.SUCCESS("Dados CIPP extraídos com sucesso!"))
            self.stdout.write(f"Número do Documento: {numero_documento}")
            self.stdout.write(f"Data de Vencimento: {vencimento}")

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Erro durante a extração de OCR: {e}"))
            logger.error(
                f"Erro detalhado durante a extração de OCR: {e}", exc_info=True
            )
            raise CommandError(f"Falha no teste de extração de OCR: {e}") from e

        self.stdout.write(self.style.SUCCESS("Teste de extração de OCR concluído."))
