import asyncio
from django.core.management.base import BaseCommand, CommandError
from playwright.async_api import async_playwright
from decouple import config

class Command(BaseCommand):
    help = 'Automatiza o processo de atualização de documentos no portal Ipiranga.'

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
                await page.goto('https://sites.redeipiranga.com.br/WAPortranNew/usuario/exibir', timeout=60000)
                await page.wait_for_selector('#codigoUsuario', state='visible', timeout=60000) # Espera o campo de usuário ficar visível
                await asyncio.sleep(5) # Pausa para visualização

                user_selector = '#codigoUsuario'
                await page.fill(user_selector, portran_user)
                password_selector = '#senha'
                await page.fill(password_selector, portran_password)
                login_button_selector = 'input[type="submit"][value="Autenticar"]'
                await page.click(login_button_selector)
                await page.wait_for_url('https://sites.redeipiranga.com.br/WAPortranNew/dashboard/index') # Wait for dashboard
                await asyncio.sleep(5) # Pausa para visualização após login
                self.stdout.write(self.style.SUCCESS('Login no Portran realizado com sucesso!'))
                # --- End Login Logic ---

                # --- Processar Veículos Vencidos ---
                self.stdout.write('Processando veículos Vencidos...')
                vencidos_card_selector = 'a.box.box-basica.text-center:has-text("Vencidos")'
                await page.click(vencidos_card_selector)
                await page.wait_for_selector('td.text-center.text-nowrap') # Wait for at least one plate to appear
                await asyncio.sleep(5) # Pausa para visualização após clicar em Vencidos

                # Clicar no botão "Editar" do primeiro elemento da lista
                edit_button_selector = 'a.btn.btn--square.alterar-veiculo-js'
                first_edit_button = page.locator(edit_button_selector).first
                
                if await first_edit_button.is_visible():
                    self.stdout.write('Clicando no botão "Editar" do primeiro veículo vencido...')
                    await first_edit_button.click()
                    # Aguardar a navegação para a página de edição
                    await page.wait_for_load_state('networkidle') # Espera a rede ficar ociosa
                    await asyncio.sleep(5) # Pausa para visualização após clicar em Editar
                    self.stdout.write(self.style.SUCCESS('Navegado para a página de edição do primeiro veículo vencido.'))
                    await asyncio.sleep(5) # Pausa para visualização após clicar em Editar

                    # --- Clicar na aba "Certificados" ---
                    self.stdout.write('Clicando na aba "Certificados"...')
                    certificados_tab_selector = 'a#certificados-tab'
                    await page.click(certificados_tab_selector)
                    await page.wait_for_load_state('networkidle') # Espera a aba carregar
                    await asyncio.sleep(5) # Pausa para visualização após clicar na aba Certificados
                    self.stdout.write(self.style.SUCCESS('Aba "Certificados" clicada.'))

                    # --- Encontrar o primeiro elemento "Vencido" e clicar em "Atualizar" ---
                    # --- Encontrar o primeiro certificado "Vencido" e clicar em "Atualizar" ---
                    self.stdout.write('Procurando pelo certificado "Vencido" e seu botão "Atualizar"...')
                    licenca_titulos = page.locator('div.licenca-titulo.d-flex.mb-32.align-items-center')
                    count = await licenca_titulos.count()
                    found_and_clicked = False

                    for i in range(count):
                        licenca_titulo_element = licenca_titulos.nth(i)
                        
                        # Get the parent of the licenca_titulo_element, which should be the container for the whole certificate entry
                        certificate_container = licenca_titulo_element.locator('xpath=..')

                        # Check if this certificate container has the "Vencido" badge
                        vencido_badge = certificate_container.locator('div.badge.badge--vermelho:has-text("Vencido")')

                        if await vencido_badge.is_visible():
                            self.stdout.write('Certificado "Vencido" encontrado. Tentando clicar no botão "Atualizar"...')
                            
                            # Now, find the "Atualizar" button within the same certificate_container
                            atualizar_button_selector = 'div.row.btn-atualizar-doc button.btn-atualizar-requisito'
                            atualizar_button = certificate_container.locator(atualizar_button_selector)

                            try:
                                await atualizar_button.wait_for(state='visible', timeout=10000) # 10 segundos de timeout
                                self.stdout.write('Botão "Atualizar" encontrado e visível.')
                                self.stdout.write('Clicando no botão "Atualizar"...')
                                await atualizar_button.click()
                                await page.wait_for_load_state('networkidle') # Espera a página de atualização carregar
                                await asyncio.sleep(5) # Pausa para visualização após clicar em Atualizar
                                self.stdout.write(self.style.SUCCESS('Botão "Atualizar" clicado. Navegado para a página de atualização.'))
                                found_and_clicked = True
                                break # Sai do loop após encontrar e clicar no primeiro
                            except Exception as e:
                                self.stdout.write(self.style.WARNING(f'Botão "Atualizar" não encontrado ou não ficou visível dentro do tempo limite: {e}'))

                    if not found_and_clicked:
                        self.stdout.write(self.style.WARNING('Nenhum certificado "Vencido" com botão "Atualizar" visível foi encontrado.'))

                    self.stdout.write(self.style.SUCCESS('Processamento de veículos concluído.'))

                self.stdout.write(self.style.SUCCESS('Processamento de veículos concluído.'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Ocorreu um erro durante a automação: {e}'))
                raise CommandError(f'Erro na automação: {e}')
            finally:
                await browser.close()

    def handle(self, *args, **options):
        return asyncio.run(self.handle_async(*args, **options))