import asyncio
import logging
import os
from django.core.management.base import BaseCommand, CommandError
from playwright.async_api import async_playwright, TimeoutError, expect
from asgiref.sync import sync_to_async

from apps.common.services import login_to_portran, convert_date_format, extract_text_from_pdf_image
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
            await sync_to_async(setattr)(certificado, 'status', 'falha')
            await sync_to_async(certificado.save)()
            raise CommandError(f'O arquivo do certificado não foi encontrado em: {file_path_upload}')

        # Extrair dados do PDF antes de iniciar o browser
        try:
            # TODO: A lógica para extrair o número do documento e a data de vencimento
            # a partir do texto extraído precisa ser implementada aqui.
            # Por enquanto, estamos usando valores fixos como exemplo.
            pdf_text = extract_text_from_pdf_image(file_path_upload, logger)
            logger.info(f"Texto extraído do PDF: {pdf_text[:200]}...") # Log inicial
            numero_documento_valor = "A2.898.625"  # Placeholder
            vencimento_valor_pdf = "30/JUL/26"  # Placeholder
        except Exception as e:
            logger.error(f"Erro ao extrair dados do PDF: {e}")
            await sync_to_async(setattr)(certificado, 'status', 'falha')
            await sync_to_async(certificado.save)()
            raise CommandError(f"Falha ao processar o arquivo PDF: {e}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False) # Modo visual para depuração
            page = await browser.new_page()

            try:
                await login_to_portran(page, logger)

                async def find_and_process_placa(url, page_name):
                    logger.info(f"--- Iniciando busca na página: {page_name} ---")
                    await page.goto(url, timeout=60000)
                    table_container = page.locator('tbody.table--body.veiculo')
                    try:
                        await table_container.wait_for(state='visible', timeout=30000)
                    except TimeoutError:
                        logger.warning(f"Timeout ao esperar pela tabela na página {page_name}.")
                        return False
                    
                    table_rows = table_container.locator('tr')
                    for i in range(await table_rows.count()):
                        row = table_rows.nth(i)
                        current_placa = (await row.locator('td.text-center.text-nowrap').inner_text(timeout=5000)).strip()
                        if current_placa.upper() == placa_alvo.upper():
                            logger.info(f"SUCESSO: Placa '{placa_alvo}' encontrada!")
                            await row.locator('a.btn.btn--square.alterar-veiculo-js').click()
                            await page.wait_for_load_state('networkidle', timeout=60000)
                            return True
                    return False

                vencidos_url = "https://sites.redeipiranga.com.br/WAPortranNew/veiculo/index?situacoesDocumentos=2&status=1,2,3,4,7"
                a_vencer_url = "https://sites.redeipiranga.com.br/WAPortranNew/veiculo/index?situacoesDocumentos=3&status=1,2,3,4,7"

                if not await find_and_process_placa(vencidos_url, "Vencidos") and not await find_and_process_placa(a_vencer_url, "À vencer"):
                    raise CommandError(f"FALHA: Placa '{placa_alvo}' não encontrada.")

                logger.info("Iniciando etapa de certificados...")
                await page.locator('a#certificados-tab').click()
                await page.wait_for_load_state('networkidle')

                certificate_fieldsets = page.locator('fieldset.certificado-box')
                found_certificate = False
                for i in range(await certificate_fieldsets.count()):
                    fieldset_container = certificate_fieldsets.nth(i)
                    name_element = fieldset_container.locator('.licenca-titulo .titulo.h3')
                    current_name = (await name_element.text_content() or '').strip()
                    vencido_badge = fieldset_container.locator('span.licenca-titulo-badge .badge--vermelho:has-text("Vencido")')

                    if nome_certificado_alvo.upper() in current_name.upper() and await vencido_badge.is_visible():
                        logger.info(f"Certificado '{nome_certificado_alvo}' (Vencido) encontrado.")
                        await fieldset_container.locator('div.row.btn-atualizar-doc button.btn-atualizar-requisito').click()
                        await page.wait_for_load_state('networkidle')
                        
                        await page.fill('#licenca-numero-1', numero_documento_valor)
                        logger.info(f"Campo 'Número do Documento' preenchido com: {numero_documento_valor}")
                        
                        vencimento_valor_formatado = convert_date_format(vencimento_valor_pdf)
                        await page.fill('#licenca-vencimento-1', vencimento_valor_formatado)
                        logger.info(f"Campo 'Vencimento' preenchido com: {vencimento_valor_formatado}")
                        
                        await fieldset_container.locator('input[type="file"]:visible').set_input_files(file_path_upload)
                        logger.info(f"Arquivo {file_path_upload} selecionado para upload.")
                        
                        found_certificate = True
                        break
                
                if not found_certificate:
                    raise CommandError(f"Certificado '{nome_certificado_alvo}' (Vencido) não encontrado.")

                # --- Lógica de Confirmação de Upload ---
                logger.info("Aguardando confirmação de upload...")
                # TODO: Implementar a lógica de confirmação de upload aqui.
                # Esta é uma etapa crítica e o 'sleep' é apenas um placeholder.
                # A lógica deve verificar uma mensagem de sucesso, um elemento na página
                # ou uma mudança de URL que confirme o upload.
                # Ex: await expect(page.locator('#mensagem-sucesso')).to_be_visible(timeout=30000)
                await asyncio.sleep(5) # Reduzido o tempo do placeholder
                logger.info("Confirmação de upload (simulada) recebida.")

                await sync_to_async(setattr)(certificado, 'status', 'enviado')
                await sync_to_async(certificado.save)()
                logger.info(f"SUCESSO: Status do certificado ID {certificado.id} atualizado para 'enviado'.")
                
                logger.info("--- FIM DA AUTOMAÇÃO ---")

            except Exception as e:
                await sync_to_async(setattr)(certificado, 'status', 'falha')
                await sync_to_async(certificado.save)()
                logger.error(f"FALHA: {e}")
                await page.screenshot(path=f'error_screenshot_cert_{certificado.id}.png')
                raise CommandError(f"Erro na automação para o certificado ID {certificado.id}: {e}")
            finally:
                await browser.close()

    def handle(self, *args, **options):
        asyncio.run(self.handle_async(*args, **options))
