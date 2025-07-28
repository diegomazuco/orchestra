import asyncio
from django.core.management.base import BaseCommand, CommandError
from playwright.async_api import async_playwright
from decouple import config

class Command(BaseCommand):
    help = 'Processa veículos vencidos e a vencer no portal Portran.'

    async def handle_async(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando processamento de veículos no Portran...'))

        portran_user = config('PORTRAN_USER')
        portran_password = config('PORTRAN_PASSWORD')

        if not portran_user or not portran_password:
            raise CommandError('As variáveis de ambiente PORTRAN_USER e PORTRAN_PASSWORD devem ser configuradas no arquivo .env.')

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False) # Keep headless=False for visibility
            page = await browser.new_page()

            try:
                # --- Login Logic (reused from login_portran) ---
                self.stdout.write('Navegando para a página de login do Portran...')
                await page.goto('https://sites.redeipiranga.com.br/WAPortranNew/usuario/exibir')

                user_selector = '#codigoUsuario'
                await page.fill(user_selector, portran_user)
                password_selector = '#senha'
                await page.fill(password_selector, portran_password)
                login_button_selector = 'input[type="submit"][value="Autenticar"]
                await page.click(login_button_selector)
                await page.wait_for_url('https://sites.redeipiranga.com.br/WAPortranNew/dashboard/index') # Wait for dashboard
                self.stdout.write(self.style.SUCCESS('Login no Portran realizado com sucesso!'))
                # --- End Login Logic ---

                # --- Processar Veículos Vencidos ---
                self.stdout.write('Processando veículos Vencidos...')
                vencidos_card_selector = 'a.box.box-basica.text-center:has-text("Vencidos")'
                await page.click(vencidos_card_selector)
                await page.wait_for_selector('td.text-center.text-nowrap') # Wait for at least one plate to appear

                # Clicar no botão "Editar" do primeiro elemento da lista
                edit_button_selector = 'a.btn.btn--square.alterar-veiculo-js'
                first_edit_button = page.locator(edit_button_selector).first
                
                if await first_edit_button.is_visible():
                    self.stdout.write('Clicando no botão "Editar" do primeiro veículo vencido...')
                    await first_edit_button.click()
                    # Aguardar a navegação para a página de edição
                    await page.wait_for_load_state('networkidle') # Espera a rede ficar ociosa
                    self.stdout.write(self.style.SUCCESS('Navegado para a página de edição do primeiro veículo vencido.'))
                else:
                    self.stdout.write(self.style.WARNING('Nenhum botão "Editar" encontrado para veículos vencidos.'))

                self.stdout.write(self.style.SUCCESS('Processamento de veículos concluído.'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Ocorreu um erro durante a automação: {e}'))
                raise CommandError(f'Erro na automação: {e}')
            finally:
                await browser.close()

    def handle(self, *args, **options):
        return asyncio.run(self.handle_async(*args, **options))