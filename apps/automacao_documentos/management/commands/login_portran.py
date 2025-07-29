import asyncio
from django.core.management.base import BaseCommand
from playwright.async_api import async_playwright
from decouple import config

class Command(BaseCommand):
    help = 'Automatiza o login no portal Portran.'

    async def handle_async(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando automação de login no Portran...'))

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False) # headless=False para ver a automação
                page = await browser.new_page()

                self.stdout.write('Navegando para a página de login...')
                await page.goto('https://sites.redeipiranga.com.br/WAPortranNew/usuario/exibir')

                # Preenchendo o campo de usuário
                user_selector = '#codigoUsuario' # id="codigoUsuario"
                await page.fill(user_selector, str(config('PORTRAN_USER'))) # type: ignore
                self.stdout.write(f'Usuário preenchido: {config("PORTRAN_USER")}')

                # Preenchendo o campo de senha
                password_selector = '#senha' # id="senha"
                await page.fill(password_selector, str(config('PORTRAN_PASSWORD')))
                self.stdout.write('Senha preenchida.')

                # Clicando no botão de autenticar
                login_button_selector = 'input[type="submit"][value="Autenticar"]' # type="submit" value="Autenticar"
                await page.click(login_button_selector)
                self.stdout.write('Botão de autenticar clicado.')

                # Aguardar um pouco para ver o resultado do login
                # Em um cenário real, você esperaria por um elemento específico na página pós-login
                # ou por uma URL específica. Aqui, apenas um delay para observação.
                await page.wait_for_timeout(5000) # Espera 5 segundos

                self.stdout.write(self.style.SUCCESS('Automação de login concluída. Verifique o navegador para o resultado.'))

                await browser.close()

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Ocorreu um erro durante a automação: {e}')) # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore

    def handle(self, *args, **options):
        return asyncio.run(self.handle_async(*args, **options))