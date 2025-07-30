import asyncio
import logging
from django.core.management.base import BaseCommand
from playwright.async_api import async_playwright
from apps.common.services import login_to_portran

# Configuração básica do logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Command(BaseCommand):
    help = 'Realiza apenas o login no portal Portran para teste.'

    async def handle_async(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando automação de login no Portran...'))

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False) # headless=False para ver a automação
            page = await browser.new_page()

            try:
                await login_to_portran(page, logger)
                self.stdout.write(self.style.SUCCESS("Login no Portran realizado com sucesso!"))
                # Mantém o navegador aberto por alguns segundos para visualização
                await asyncio.sleep(5)

            except Exception as e:
                self.stderr.write(self.style.ERROR(f'Ocorreu um erro durante a automação: {e}'))
            finally:
                await browser.close()

    def handle(self, *args, **options):
        asyncio.run(self.handle_async(*args, **options))
