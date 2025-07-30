import asyncio
import logging
import os
from django.core.management.base import BaseCommand, CommandError
from playwright.async_api import async_playwright, TimeoutError, expect
from asgiref.sync import sync_to_async # Importar sync_to_async

from apps.common.services import login_to_portran
from apps.automacao_ipiranga.models import CertificadoVeiculo

# Configuração do logger
logger = logging.getLogger(__name__)
log_file_path = os.path.join(os.getcwd(), 'temp_automation.log')
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=log_file_path, filemode='w')

class Command(BaseCommand):
    help = 'Executa a automação de upload de um certificado de veículo específico do portal Ipiranga.'

    def add_arguments(self, parser):
        parser.add_argument('certificado_id', type=int, help='O ID do CertificadoVeiculo a ser processado.')

    async def handle_async(self, *args, **options):
        certificado_id = options['certificado_id']
        
        try:
            # Usar sync_to_async para chamar a operação de banco de dados síncrona
            certificado = await sync_to_async(CertificadoVeiculo.objects.select_related('veiculo').get)(pk=certificado_id)
        except CertificadoVeiculo.DoesNotExist:
            raise CommandError(f'CertificadoVeiculo com ID "{certificado_id}" não encontrado.')

        placa_alvo = certificado.veiculo.placa
        nome_certificado_alvo = certificado.nome
        file_path_upload = certificado.arquivo.path

        logger.info(f"--- INÍCIO DA AUTOMAÇÃO PARA O CERTIFICADO ID: {certificado.id} ---")
        logger.info(f"Veículo Placa: {placa_alvo}")
        logger.info(f"Certificado: {nome_certificado_alvo}")
        logger.info(f"Arquivo: {file_path_upload}")

        if not os.path.exists(file_path_upload):
            # Usar sync_to_async para salvar o status
            await sync_to_async(setattr)(certificado, 'status', 'falha')
            await sync_to_async(certificado.save)()
            raise CommandError(f'O arquivo do certificado não foi encontrado em: {file_path_upload}')

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            page = await browser.new_page()

            try:
                await login_to_portran(page, logger)

                # --- Função para buscar placa ---
                async def find_and_process_placa(url, page_name):
                    logger.info(f"--- Iniciando busca na página: {page_name} ---")
                    logger.info(f"Navegando para a URL: {url}")
                    await page.goto(url, timeout=60000)
                    
                    table_container = page.locator('tbody.table--body.veiculo')
                    try:
                        await table_container.wait_for(state='visible', timeout=30000)
                        logger.info("Contêiner da tabela de veículos encontrado.")
                    except TimeoutError:
                        logger.warning(f"Timeout ao esperar pela tabela na página {page_name}.")
                        return False

                    table_rows = table_container.locator('tr')
                    num_rows = await table_rows.count()
                    logger.info(f"Encontradas {num_rows} linhas de veículos.")

                    if num_rows == 0:
                        return False

                    for i in range(num_rows):
                        row = table_rows.nth(i)
                        placa_element = row.locator('td.text-center.text-nowrap')
                        current_placa = (await placa_element.inner_text(timeout=5000)).strip()
                        
                        logger.info(f"Lendo linha {i+1}: Placa '{current_placa}'")

                        if current_placa.upper() == placa_alvo.upper():
                            logger.info(f"SUCESSO: Placa '{placa_alvo}' encontrada!")
                            edit_button = row.locator('a.btn.btn--square.alterar-veiculo-js')
                            await edit_button.click()
                            await page.wait_for_load_state('networkidle', timeout=60000)
                            logger.info("Página de edição do veículo carregada.")
                            return True
                    
                    logger.info(f"--- Fim da busca na página: {page_name} ---")
                    return False

                # --- Busca nas páginas Vencidos, À Vencer e Todos ---
                vencidos_url = "https://sites.redeipiranga.com.br/WAPortranNew/veiculo/index?situacoesDocumentos=2&status=1,2,3,4,7"
                a_vencer_url = "https://sites.redeipiranga.com.br/WAPortranNew/veiculo/index?situacoesDocumentos=3&status=1,2,3,4,7"
                todos_url = "https://sites.redeipiranga.com.br/WAPortranNew/veiculo/index"

                if not await find_and_process_placa(vencidos_url, "Vencidos"):
                    if not await find_and_process_placa(a_vencer_url, "À vencer"):
                        raise CommandError(f"FALHA: Placa '{placa_alvo}' não encontrada nas páginas 'Vencidos' ou 'À vencer'.")

                # --- Lógica de Certificados ---
                logger.info("Iniciando etapa de certificados...")
                await page.locator('a#certificados-tab').click()
                await page.wait_for_load_state('networkidle')

                # Agora, vamos pegar o fieldset que contém o certificado
                certificate_fieldsets = page.locator('fieldset.certificado-box')
                num_certificates = await certificate_fieldsets.count()
                logger.info(f"Encontrados {num_certificates} contêineres de certificados (fieldsets).")

                found_certificate = False
                for i in range(num_certificates):
                    fieldset_container = certificate_fieldsets.nth(i)
                    # O seletor do nome agora é relativo ao fieldset
                    name_element = fieldset_container.locator('.licenca-titulo .titulo.h3')
                    try:
                        await name_element.wait_for(state='visible', timeout=5000) # Espera o título ficar visível
                        current_name = (await name_element.text_content() or '').strip()
                    except TimeoutError:
                        logger.warning(f"Timeout ao esperar pelo título do certificado na linha {i+1}. Pulando.")
                        continue
                    logger.info(f"Lendo certificado {i+1}: '{current_name}'")

                    vencido_badge = fieldset_container.locator('span.licenca-titulo-badge .badge--vermelho:has-text("Vencido")')

                    if nome_certificado_alvo.upper() in current_name.upper() and await vencido_badge.is_visible():
                        logger.info(f"Certificado '{nome_certificado_alvo}' (Vencido) encontrado.")
                        update_button = fieldset_container.locator('div.row.btn-atualizar-doc button.btn-atualizar-requisito')
                        
                        await update_button.wait_for(state='visible', timeout=10000) # Espera o botão ficar visível
                        await update_button.click()
                        await page.wait_for_load_state('networkidle')
                        logger.info("Página de atualização de certificado carregada.")
                        found_certificate = True
                        break
                
                if not found_certificate:
                    raise CommandError(f"Certificado '{nome_certificado_alvo}' não encontrado.")

                # --- Lógica de Upload ---
                logger.info("Iniciando etapa de upload...")
                # Usar um seletor mais específico para o campo de upload visível dentro do fieldset correto
                file_input_selector = fieldset_container.locator('input[type="file"]:visible')
                await file_input_selector.set_input_files(file_path_upload)
                logger.info(f"Arquivo {file_path_upload} selecionado.")

                # Lógica de confirmação de upload (FALTANTE)
                # Ex: await page.locator('#btn-salvar-upload').click()
                # await expect(page.locator(".mensagem-sucesso")).to_be_visible()
                logger.warning("Lógica de confirmação de upload não implementada.")
                await asyncio.sleep(5)

                # Atualiza o status para sucesso
                # Usar sync_to_async para salvar o status
                await sync_to_async(setattr)(certificado, 'status', 'enviado')
                await sync_to_async(certificado.save)()
                logger.info(f"SUCESSO: Status do certificado ID {certificado.id} atualizado para 'enviado'.")
                logger.info("--- FIM DA AUTOMAÇÃO ---")

            except Exception as e:
                # Usar sync_to_async para salvar o status
                await sync_to_async(setattr)(certificado, 'status', 'falha')
                await sync_to_async(certificado.save)()
                logger.error(f"FALHA: {e}")
                await page.screenshot(path=f'error_screenshot_cert_{certificado.id}.png')
                raise CommandError(f"Erro na automação para o certificado ID {certificado.id}: {e}")
            finally:
                await browser.close()

    def handle(self, *args, **options):
        asyncio.run(self.handle_async(*args, **options))
