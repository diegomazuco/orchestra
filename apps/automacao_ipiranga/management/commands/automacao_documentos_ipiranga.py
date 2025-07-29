import asyncio
import logging
from django.core.management.base import BaseCommand, CommandError
from playwright.async_api import async_playwright, TimeoutError
from decouple import config
import os

# Configuração do logger
logger = logging.getLogger(__name__)
log_file_path = os.path.join(os.getcwd(), 'temp_automation.log')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=log_file_path, filemode='w')

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

        logger.info("--- INÍCIO DA AUTOMAÇÃO ---")
        logger.info(f"Placa Alvo: {placa_alvo}")
        logger.info(f"Certificado Alvo: {nome_certificado_alvo}")
        logger.info(f"Caminho do Arquivo: {file_path_upload}")

        if not os.path.exists(file_path_upload):
            raise CommandError(f'O arquivo especificado não existe: {file_path_upload}')

        portran_user = config('PORTRAN_USER')
        portran_password = config('PORTRAN_PASSWORD')

        if not portran_user or not portran_password:
            raise CommandError('As variáveis de ambiente PORTRAN_USER e PORTRAN_PASSWORD devem ser configuradas.')

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            try:
                # --- Lógica de Login ---
                logger.info("Iniciando etapa de login...")
                await page.goto('https://sites.redeipiranga.com.br/WAPortranNew/usuario/exibir', timeout=60000)
                logger.info("Página de login carregada. Aguardando seletor de usuário.")
                await page.wait_for_selector('#codigoUsuario', state='visible', timeout=60000)
                
                logger.info("Preenchendo usuário...")
                await page.fill('#codigoUsuario', str(portran_user)) # type: ignore
                logger.info("Preenchendo senha...")
                await page.fill('#senha', str(portran_password)) # type: ignore
                
                logger.info("Clicando em 'Autenticar'...")
                await page.click('input[type="submit"][value="Autenticar"]')
                
                logger.info("Aguardando redirecionamento para o dashboard...")
                await page.wait_for_url('https://sites.redeipiranga.com.br/WAPortranNew/dashboard/index', timeout=60000)
                logger.info("Login realizado com sucesso!")
                # --- Fim da Lógica de Login ---

                # --- Função para buscar placa ---
                async def find_and_process_placa(url, page_name):
                    logger.info(f"--- Iniciando busca na página: {page_name} ---")
                    logger.info(f"Navegando para a URL: {url}")
                    await page.goto(url, timeout=60000)
                    
                    table_container_selector = 'tbody.table--body.veiculo'
                    logger.info(f"Aguardando o contêiner da tabela: '{table_container_selector}'")
                    try:
                        await page.wait_for_selector(table_container_selector, state='visible', timeout=30000)
                        logger.info("Contêiner da tabela de veículos encontrado e visível.")
                    except TimeoutError:
                        logger.warning(f"Timeout ao esperar pelo contêiner da tabela na página {page_name}. Pode não haver veículos ou a página mudou.")
                        return False

                    table_rows = page.locator(f'{table_container_selector} tr')
                    num_rows = await table_rows.count()
                    logger.info(f"Encontradas {num_rows} linhas de veículos.")

                    if num_rows == 0:
                        logger.warning("Nenhuma linha de veículo encontrada na tabela.")
                        return False

                    found_placa = False
                    for i in range(num_rows):
                        row = table_rows.nth(i)
                        placa_element = row.locator('td.text-center.text-nowrap')
                        
                        try:
                            current_placa = (await placa_element.inner_text(timeout=5000)).strip() if await placa_element.inner_text(timeout=5000) else "" # type: ignore # type: ignore
                        except TimeoutError:
                            logger.warning(f"Não foi possível ler o texto da placa na linha {i+1}. Pulando.")
                            continue
                        
                        logger.info(f"Lendo linha {i+1}: Placa encontrada: '{current_placa.strip()}'")

                        if current_placa.strip().upper() == placa_alvo.upper():
                            logger.info(f"SUCESSO: Placa '{placa_alvo}' encontrada!")
                            edit_button = row.locator('a.btn.btn--square.alterar-veiculo-js')
                            
                            logger.info("Verificando visibilidade do botão 'Editar'.")
                            if await edit_button.is_visible():
                                logger.info("Botão 'Editar' está visível. Clicando...")
                                await edit_button.click()
                                await page.wait_for_load_state('networkidle', timeout=60000)
                                logger.info("Página de edição do veículo carregada.")
                                found_placa = True
                                break
                            else:
                                logger.warning("Botão 'Editar' não está visível.")
                        else:
                            logger.debug(f"Placa '{current_placa.strip()}' não corresponde a '{placa_alvo}'.")
                    
                    logger.info(f"--- Fim da busca na página: {page_name} ---")
                    return found_placa

                # --- Busca nas páginas Vencidos e À Vencer ---
                vencidos_url = "https://sites.redeipiranga.com.br/WAPortranNew/veiculo/index?situacoesDocumentos=2&status=1,2,3,4,7"
                a_vencer_url = "https://sites.redeipiranga.com.br/WAPortranNew/veiculo/index?situacoesDocumentos=3&status=1,2,3,4,7"
                todos_url = "https://sites.redeipiranga.com.br/WAPortranNew/veiculo/index"

                if not await find_and_process_placa(vencidos_url, "Vencidos"):
                    logger.warning(f"Placa '{placa_alvo}' não encontrada em 'Vencidos'. Tentando 'À vencer'...")
                    if not await find_and_process_placa(a_vencer_url, "À vencer"):
                        logger.warning(f"Placa '{placa_alvo}' não encontrada em 'À vencer'. Tentando em 'Todos'...")
                        if not await find_and_process_placa(todos_url, "Todos"):
                            raise CommandError(f"FALHA: Placa '{placa_alvo}' não encontrada em 'Vencidos', 'À vencer' ou 'Todos'.")

                # --- Lógica de Certificados ---
                logger.info("Iniciando etapa de certificados...")
                await page.click('a#certificados-tab')
                await page.wait_for_load_state('networkidle')
                logger.info("Aba 'Certificados' clicada e carregada.")

                logger.info(f"Procurando pelo certificado '{nome_certificado_alvo}'.")
                certificate_containers = page.locator('div.licenca-titulo.d-flex.mb-32.align-items-center:has(.titulo.h3)')
                num_certificates = await certificate_containers.count()
                logger.info(f"Encontrados {num_certificates} contêineres de certificados.")

                found_certificate = False
                for i in range(num_certificates):
                    container = certificate_containers.nth(i)
                    name_element = container.locator('.titulo.h3')
                    current_name = (await name_element.text_content()).strip() if await name_element.text_content() else "" # type: ignore
                    logger.info(f"Lendo certificado {i+1}: '{current_name.strip()}'")

                    full_container = container
                    vencido_badge = full_container.locator('span.licenca-titulo-badge .badge--vermelho:has-text("Vencido")')

                    if nome_certificado_alvo.upper() in current_name.strip().upper() and await vencido_badge.is_visible():
                        logger.info(f"Certificado '{nome_certificado_alvo}' (Vencido) encontrado.")
                        update_button = full_container.locator('div.row.btn-atualizar-doc button.btn-atualizar-requisito')
                        
                        logger.info("Clicando no botão 'Atualizar'...")
                        await update_button.click()
                        await page.wait_for_load_state('networkidle')
                        logger.info("Página de atualização de certificado carregada.")
                        found_certificate = True
                        break
                
                if not found_certificate:
                    raise CommandError(f"Certificado '{nome_certificado_alvo}' (Vencido) não encontrado.")

                # --- Lógica de Upload ---
                logger.info("Iniciando etapa de upload...")
                file_input_selector = 'input[type="file"]'
                await page.wait_for_selector(file_input_selector, state='visible', timeout=10000)
                logger.info(f"Realizando upload do arquivo: {file_path_upload}")
                await page.set_input_files(file_input_selector, file_path_upload)
                logger.info("Upload do arquivo concluído com sucesso.")
                await asyncio.sleep(5)

                logger.info("--- FIM DA AUTOMAÇÃO ---")

            except TimeoutError as e:
                logger.error(f"TIMEOUT: A operação demorou mais que o esperado. {e}")
                await page.screenshot(path='timeout_screenshot.png')
                logger.error("Screenshot 'timeout_screenshot.png' capturado.")
                raise CommandError(f"Erro de Timeout na automação: {e}")
            except Exception as e:
                logger.error(f"ERRO INESPERADO: {e}")
                await page.screenshot(path='error_screenshot.png')
                logger.error("Screenshot 'error_screenshot.png' capturado.")
                raise CommandError(f"Erro inesperado na automação: {e}")
            finally:
                logger.info("Fechando o navegador.")
                await browser.close()

    def handle(self, *args, **options):
        return asyncio.run(self.handle_async(*args, **options))
