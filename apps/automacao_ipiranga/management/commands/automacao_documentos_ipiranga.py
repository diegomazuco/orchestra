import asyncio
from django.core.management.base import BaseCommand, CommandError
from playwright.async_api import async_playwright
from decouple import config
import os # Importar para lidar com caminhos de arquivo

class Command(BaseCommand):
    help = 'Automatiza o processo de atualização de documentos no portal Ipiranga.'

    def add_arguments(self, parser):
        parser.add_argument('placa', type=str, help='A placa do veículo a ser processado.')
        parser.add_argument('nome_certificado', type=str, help='O nome do certificado a ser atualizado.')
        parser.add_argument('file_path', type=str, help='O caminho absoluto do arquivo a ser enviado.')

    async def handle_async(self, *args, **options):
        placa_alvo = options['placa']
        nome_certificado_alvo = options['nome_certificado']
        file_path_upload = options['file_path']

        if not os.path.exists(file_path_upload):
            raise CommandError(f'O arquivo especificado não existe: {file_path_upload}')

        self.stdout.write(self.style.SUCCESS(f'Iniciando processamento para a placa {placa_alvo} e certificado {nome_certificado_alvo} com arquivo {file_path_upload}...'))

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

                # --- Função para processar cards (Vencidos/À vencer) ---
                async def process_card(card_selector, card_name):
                    self.stdout.write(f'Processando veículos no card "{card_name}"...')
                    await page.click(card_selector)
                    await page.wait_for_selector('td.text-center.text-nowrap') # Wait for at least one plate to appear
                    await asyncio.sleep(5) # Pausa para visualização após clicar no card

                    # Encontrar a linha da placa alvo
                    # A placa está dentro de um <td> com class="text-center text-nowrap"
                    # A linha da tabela tem class="table--body veiculo" e id="linhaX"
                    # Vamos procurar a placa dentro de todas as linhas da tabela
                    
                    # Primeiro, encontrar todas as linhas da tabela
                    table_rows = page.locator('tr.table--body.veiculo')
                    num_rows = await table_rows.count()
                    
                    found_placa = False
                    for i in range(num_rows):
                        row = table_rows.nth(i)
                        placa_element = row.locator('td.text-center.text-nowrap')
                        current_placa = await placa_element.text_content()
                        self.stdout.write(f'DEBUG: Placa lida do portal: "{current_placa}"') # Add this debug log

                        if current_placa and current_placa.strip().upper() == placa_alvo.upper(): # Change comparison to upper()
                            self.stdout.write(f'Placa {placa_alvo} encontrada na linha {i} do card "{card_name}".')
                            
                            # Clicar no botão "Editar" desta linha específica
                            edit_button = row.locator('a.btn.btn--square.alterar-veiculo-js')
                            if await edit_button.is_visible():
                                self.stdout.write(f'Clicando no botão "Editar" para a placa {placa_alvo}...')
                                await edit_button.click()
                                await page.wait_for_load_state('networkidle')
                                await asyncio.sleep(5)
                                self.stdout.write(self.style.SUCCESS(f'Navegado para a página de edição da placa {placa_alvo}.'))
                                found_placa = True
                                break
                            else:
                                self.stdout.write(self.style.WARNING(f'Botão "Editar" não visível para a placa {placa_alvo} na linha {i}.'))
                        else:
                            self.stdout.write(f'Placa {current_placa} na linha {i} não corresponde à placa alvo {placa_alvo}.')

                    return found_placa

                # Tentar processar primeiro os "Vencidos"
                vencidos_card_selector = 'a.box.box-basica.text-center:has-text("Vencidos")'
                if not await process_card(vencidos_card_selector, "Vencidos"):
                    self.stdout.write(self.style.WARNING(f'Placa {placa_alvo} não encontrada no card "Vencidos". Tentando "À vencer"...'))
                    # Se não encontrou nos "Vencidos", voltar para o dashboard e tentar "À vencer"
                    await page.goto('https://sites.redeipiranga.com.br/WAPortranNew/dashboard/index') # Voltar para o dashboard
                    await page.wait_for_load_state('networkidle')
                    await asyncio.sleep(3)
                    a_vencer_card_selector = 'a.box.box-basica.text-center:has-text("À vencer")'
                    if not await process_card(a_vencer_card_selector, "À vencer"):
                        raise CommandError(f'Placa {placa_alvo} não encontrada nem no card "Vencidos" nem no card "À vencer".')
                
                # --- Clicar na aba "Certificados" ---
                self.stdout.write('Clicando na aba "Certificados"...')
                certificados_tab_selector = 'a#certificados-tab'
                await page.click(certificados_tab_selector)
                await page.wait_for_load_state('networkidle') # Espera a aba carregar
                await asyncio.sleep(5) # Pausa para visualização após clicar na aba Certificados
                self.stdout.write(self.style.SUCCESS('Aba "Certificados" clicada.'))

                # --- Encontrar o certificado alvo e clicar em "Atualizar" ---
                self.stdout.write(f'Procurando pelo certificado "{nome_certificado_alvo}" e seu botão "Atualizar"...')
                
                # Encontrar todos os contêineres de certificado
                certificate_containers = page.locator('div.licenca-titulo.d-flex.mb-32.align-items-center:has(.titulo.h3)')
                num_certificates = await certificate_containers.count()
                
                found_certificate = False
                for i in range(num_certificates):
                    licenca_titulo_element = certificate_containers.nth(i)
                    certificate_name_element = licenca_titulo_element.locator('.titulo.h3')
                    current_certificate_name = await certificate_name_element.text_content()
                    
                    # Get the parent of the licenca_titulo_element, which should be the container for the whole certificate entry
                    certificate_full_container = licenca_titulo_element.locator('xpath=..')

                    # Check if this certificate container has the "Vencido" badge
                    vencido_badge = certificate_full_container.locator('div.badge.badge--vermelho:has-text("Vencido")')

                    if current_certificate_name and current_certificate_name.strip() == nome_certificado_alvo and await vencido_badge.is_visible():
                        self.stdout.write(f'Certificado "{nome_certificado_alvo}" (Vencido) encontrado. Tentando clicar no botão "Atualizar"...')
                        
                        # Now, find the "Atualizar" button within the same certificate_full_container
                        atualizar_button_selector = 'div.row.btn-atualizar-doc button.btn-atualizar-requisito'
                        atualizar_button = certificate_full_container.locator(atualizar_button_selector)

                        try:
                            await atualizar_button.wait_for(state='visible', timeout=10000)
                            self.stdout.write('Botão "Atualizar" encontrado e visível.')
                            self.stdout.write('Clicando no botão "Atualizar"...')
                            await atualizar_button.click()
                            await page.wait_for_load_state('networkidle')
                            await asyncio.sleep(5)
                            self.stdout.write(self.style.SUCCESS('Botão "Atualizar" clicado. Navegado para a página de atualização.'))
                            found_certificate = True
                            break
                        except Exception as e:
                            self.stdout.write(self.style.WARNING(f'Botão "Atualizar" não encontrado ou não ficou visível dentro do tempo limite para o certificado {nome_certificado_alvo}: {e}'))
                    else:
                        self.stdout.write(f'Certificado "{current_certificate_name}" não corresponde ao alvo ou não está vencido.')

                if not found_certificate:
                    raise CommandError(f'Certificado "{nome_certificado_alvo}" (Vencido) não encontrado para a placa {placa_alvo}.')

                # --- Upload do arquivo ---
                self.stdout.write(f'Realizando upload do arquivo: {file_path_upload}...')
                # Identificar o input de arquivo. Pode variar, então use um seletor genérico ou específico.
                # Exemplo: input[type="file"] ou um ID/classe específico do seu portal
                file_input_selector = 'input[type="file"]'; # Ajuste este seletor conforme o HTML do portal
                await page.wait_for_selector(file_input_selector, state='visible', timeout=10000)
                await page.set_input_files(file_input_selector, file_path_upload)
                self.stdout.write(self.style.SUCCESS('Arquivo enviado com sucesso!'))
                await asyncio.sleep(5) # Pausa para visualização após upload

                # Clicar no botão de salvar/confirmar após o upload (se houver)
                # Exemplo: await page.click('button#saveButton') # Ajuste este seletor
                # self.stdout.write(self.style.SUCCESS('Documento atualizado e salvo no portal.'))

                self.stdout.write(self.style.SUCCESS('Processamento de veículos concluído.'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Ocorreu um erro durante a automação: {e}'))
                raise CommandError(f'Erro na automação: {e}')
            finally:
                await browser.close()

    def handle(self, *args, **options):
        return asyncio.run(self.handle_async(*args, **options))