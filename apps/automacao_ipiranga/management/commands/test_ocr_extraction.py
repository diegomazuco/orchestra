import logging

from django.core.management.base import BaseCommand

from apps.common.services import extract_text_from_pdf_image

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Comando para testar a extração de texto OCR de um PDF específico."""

    help = "Testa a extração de texto OCR de um arquivo PDF e verifica a presença de informações específicas."

    def add_arguments(self, parser):
        """Adiciona argumentos ao comando."""
        parser.add_argument(
            "pdf_path",
            type=str,
            help="O caminho completo para o arquivo PDF a ser testado.",
        )

    def handle(self, *args, **options):
        """Lida com a execução do comando."""
        pdf_path = options["pdf_path"]
        self.stdout.write(
            self.style.SUCCESS(f"Iniciando teste de OCR para: {pdf_path}")
        )

        try:
            # Tesseract config: PSM 6 assumes a single uniform block of text.
            # OEM 3 is the default engine, but we specify it for clarity.
            tesseract_config = "--oem 3 --psm 6"
            extracted_text = extract_text_from_pdf_image(
                pdf_path, logger, tesseract_config=tesseract_config
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
            data_encontrada = "05/FEV/26" in extracted_text.replace(" ", "")

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

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Ocorreu um erro durante o teste: {e}"))
