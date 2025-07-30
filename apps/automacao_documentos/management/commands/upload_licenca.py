import os
import asyncio
import logging
from django.core.management.base import BaseCommand, CommandError
from playwright.async_api import async_playwright

from apps.automacao_documentos.models import LicencaAmbiental
from apps.common.services import login_to_portran

# Configuração do logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Command(BaseCommand):
    help = 'Automatiza o upload de uma licença ambiental para um portal (requer URL real).'

    def add_arguments(self, parser):
        parser.add_argument('licenca_id', type=int, help='ID da Licença Ambiental a ser processada.')

    async def handle_async(self, *args, **options):
        licenca_id = options['licenca_id']

        try:
            licenca = LicencaAmbiental.objects.get(pk=licenca_id)
        except LicencaAmbiental.DoesNotExist:
            raise CommandError(f'Licença Ambiental com ID "{licenca_id}" não encontrada.')

        self.stdout.write(self.style.SUCCESS(f'Iniciando automação para a licença: {licenca.numero}'))

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                # 1. Realizar login usando o serviço centralizado
                await login_to_portran(page, logger)

                # 2. Navegar até a página de upload (URL de exemplo, precisa ser ajustada)
                upload_url = 'https://www.ibama.gov.br/upload-licenca' # <-- ATENÇÃO: URL FICTÍCIA
                self.stdout.write(self.style.WARNING(f'Navegando para a URL de upload (FICTÍCIA): {upload_url}'))
                logger.warning(f"A URL de upload '{upload_url}' é um exemplo e precisa ser substituída pela URL real.")
                await page.goto(upload_url)

                # 3. Fazer upload do arquivo
                self.stdout.write(f'Fazendo upload do arquivo: {licenca.arquivo.path}')
                file_path = os.path.abspath(licenca.arquivo.path)
                
                # ATENÇÃO: O seletor 'input[type="file"]' é genérico. Use um mais específico.
                file_input_selector = 'input[type="file"]' 
                await page.locator(file_input_selector).set_input_files(file_path)

                # 4. Clicar no botão de envio e aguardar confirmação (LÓGICA FALTANTE)
                # Exemplo: 
                # await page.locator('#botao-enviar').click()
                # await expect(page.locator('#mensagem-sucesso')).to_be_visible()
                self.stdout.write(self.style.SUCCESS('Arquivo enviado (simulado)! Lógica de confirmação precisa ser implementada.'))

                # 5. Atualizar status da licença
                licenca.status = 'enviado'
                licenca.save()
                self.stdout.write(self.style.SUCCESS(f'Status da licença {licenca.numero} atualizado para "enviado".'))

            except Exception as e:
                licenca.status = 'falha'
                licenca.save()
                self.stderr.write(self.style.ERROR(f"Erro na automação: {e}"))
                # A exceção será re-levantada pelo serviço de login se a falha for lá
            finally:
                await browser.close()

        self.stdout.write(self.style.SUCCESS('Automação concluída.'))

    def handle(self, *args, **options):
        asyncio.run(self.handle_async(*args, **options))
