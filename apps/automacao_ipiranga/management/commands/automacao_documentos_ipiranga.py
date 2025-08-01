import asyncio
import logging
import os
import re
from django.core.management.base import BaseCommand, CommandError
from playwright.async_api import async_playwright
from asgiref.sync import sync_to_async

from apps.common.services import login_to_portran, convert_date_format, extract_text_from_pdf_image
from apps.automacao_ipiranga.models import CertificadoVeiculo

# Configuração do logger (agora centralizada em settings.py)
logger = logging.getLogger(__name__)

                for certificado_id in certificado_ids:
                    certificado = None # Inicializa certificado para garantir que esteja sempre definido
                    try:
                        certificado = await sync_to_async(CertificadoVeiculo.objects.select_related('veiculo').get)(pk=certificado_id) # type: ignore
                        
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
                            pdf_text = extract_text_from_pdf_image(file_path_upload, logger)
                            
                            # --- Lógica de Extração de Dados do PDF ---
                            pdf_blocks = re.split(r'CERTIFICADO DE INSPEÇÃO VEICULAR', pdf_text)
                            
                            if len(pdf_blocks) < 2:
                                raise CommandError("Não foi possível encontrar um bloco de 'CERTIFICADO DE INSPEÇÃO VEICULAR' no PDF.")

                            first_block = pdf_blocks[1]
                            logger.info("Analisando o primeiro bloco do certificado encontrado no PDF.")

                            # 1. Extrair Número do Documento e remover todos os caracteres não numéricos.
                            match_numero = re.search(r'([A-Z0-9]{1,3}\.\d{3}\.\d{3})', first_block)
                            numero_documento_valor = re.sub(r'\D', '', match_numero.group(1)) if match_numero else "N/A"

                            # 2. Extrair a Data de Vencimento (a última data no formato DD/MON/YY encontrada no bloco).
                            vencimento_valor_pdf = "N/A"
                            all_dates = re.findall(r'\b(\d{2}/[A-Z]{3}/\d{2})\b', first_block, re.IGNORECASE)
                            if all_dates:
                                vencimento_valor_pdf = all_dates[-1] # Pega a última data encontrada
                            else:
                                logger.warning("Nenhuma data no formato DD/MON/YY foi encontrada no bloco do PDF.")

                            logger.info(f"Número do Documento Extraído (Apenas Números): {numero_documento_valor}")
                            logger.info(f"Data de Vencimento Extraída (DD/MON/YY): {vencimento_valor_pdf}")
                        except Exception as e:
                            logger.error(f"Erro ao extrair dados do PDF: {e}")
                            await sync_to_async(setattr)(certificado, 'status', 'falha')
                            await sync_to_async(certificado.save)()
                            raise CommandError(f"Falha ao processar o arquivo PDF: {e}")

                        async def find_and_process_placa(url, page_name):
                            logger.info(f"Navegando para a página de veículos: {page_name}")
                            await page.goto(url, timeout=60000)
                            await page.wait_for_load_state('networkidle', timeout=60000)
                            
                            # CORREÇÃO: O ID da tabela mudou de 'veiculos-grid-table' para 'tabela-veiculo'
                            rows = page.locator('table#tabela-veiculo tbody tr')
                            count = await rows.count()
                            logger.info(f"Encontradas {count} linhas na tabela de veículos.")

                            for i in range(count):
                                row = rows.nth(i)
                                try:
                                    placa_text_element = row.locator('td:nth-child(2)') # CORREÇÃO: A coluna da placa é a segunda (index 2)
                                    placa_text = (await placa_text_element.text_content() or '').strip()
                                    logger.info(f"Lendo linha {i+1}: Placa encontrada no HTML: '{placa_text}'")

                                    if placa_text and placa_alvo in placa_text:
                                        logger.info(f"SUCESSO: Placa '{placa_alvo}' encontrada na página {page_name}!")
                                        await row.locator('a.btn.btn--square.alterar-veiculo-js').click()
                                        await page.wait_for_load_state('networkidle', timeout=60000)
                                        return True
                                except Exception as e:
                                    logger.error(f"Erro ao processar a linha {i+1}: {e}")
                            
                            logger.warning(f"Placa '{placa_alvo}' não encontrada na página {page_name}.")
                            return False

                        vencidos_url = "https://sites.redeipiranga.com.br/WAPortranNew/veiculo/index?situacoesDocumentos=2&status=1,2,3,4,7"
                        a_vencer_url = "https://sites.redeipiranga.com.br/WAPortranNew/veiculo/index?situacoesDocumentos=3&status=1,2,3,4,7"

                        if not await find_and_process_placa(vencidos_url, "Vencidos") and not await find_and_process_placa(a_vencer_url, "À vencer"):
                            raise CommandError(f"FALHA: Placa '{placa_alvo}' não encontrada em nenhuma das páginas (Vencidos ou À vencer).")

                        logger.info("Iniciando etapa de certificados...")
                        await page.locator('a#certificados-tab').click()
                        await page.wait_for_load_state('networkidle')

                        certificate_fieldsets = page.locator('fieldset.certificado-box')
                        count = await certificate_fieldsets.count()
                        logger.info(f"Encontrados {count} 'fieldset.certificado-box' na página.")
                        found_certificate = False
                        for i in range(count):
                            fieldset_container = certificate_fieldsets.nth(i)
                            try:
                                name_element = fieldset_container.locator('.licenca-titulo .titulo.h3')
                                current_name = (await name_element.text_content() or '').strip()
                                if not current_name:
                                    logger.warning(f"Certificado {i+1} não possui um título legível. Pulando.")
                                    continue

                                # CORREÇÃO: Usar count() > 0 em vez de is_visible() para maior robustez
                                vencido_badge = fieldset_container.locator('*.badge--vermelho:has-text("Vencido")')
                                is_vencido = await vencido_badge.count() > 0

                                logger.info(f"Analisando certificado {i+1}: Nome lido='{current_name}', É Vencido?={is_vencido}")

                                if nome_certificado_alvo.upper() in current_name.upper() and is_vencido:
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
                                    
                                    # 1. Clica no botão para enviar o certificado específico
                                    logger.info("Clicando em 'Enviar novo certificado'...")
                                    await fieldset_container.locator('button:has-text("Enviar novo certificado")').click()

                                    # 2. Aguarda a confirmação do upload do certificado
                                    logger.info("Aguardando confirmação de upload do certificado...")
                                    success_message_locator = page.locator('span.js-successArea:has-text("sucesso")')
                                    await success_message_locator.wait_for(timeout=30000)
                                    logger.info("Mensagem de sucesso do upload do certificado detectada.")

                                    found_certificate = True
                                    break # Sai do loop após encontrar e processar o certificado
                            except Exception as e:
                                logger.error(f"Erro ao processar o fieldset de certificado {i+1}: {e}. Pulando para o próximo.")
                                continue
                        
                        if not found_certificate:
                            raise CommandError(f"Certificado '{nome_certificado_alvo}' (Vencido) não foi encontrado ou processado.")

                        # 3. Clica no botão 'Salvar' final da página
                        logger.info("Clicando no botão 'Salvar' final da página...")
                        await page.locator('a#botaoAtualizar').click()

                        # --- Lógica de Confirmação Final ---
                        # Aguarda o redirecionamento para a página de listagem de veículos como confirmação.
                        logger.info("Aguardando redirecionamento para a página de listagem de veículos...")
                        await expect(page).to_have_url(re.compile(r'.*/veiculo/index'), timeout=60000)
                        logger.info("Redirecionamento confirmado. A operação foi salva com sucesso.")

                        # Limpeza em caso de sucesso
                        logger.info(f"Removendo certificado ID {certificado.id} do banco de dados...")
                        await sync_to_async(certificado.delete)()
                        if os.path.exists(file_path_upload):
                            os.remove(file_path_upload)
                            logger.info(f"Arquivo PDF associado removido: {file_path_upload}")
                        if os.path.exists('login_error_screenshot.png'):
                            os.remove('login_error_screenshot.png')
                            logger.info("Screenshot de erro de login removido (automação bem-sucedida).")

                        await sync_to_async(setattr)(certificado, 'status', 'enviado')
                        await sync_to_async(certificado.save)()
                        logger.info(f"SUCESSO: Status do certificado ID {certificado.id} atualizado para 'enviado'.")
                        
                        logger.info("--- FIM DA AUTOMAÇÃO ---")

                    except Exception as e:
                        logger.error(f"FALHA: {e}")
                        # Apenas tenta atualizar o status se o certificado foi recuperado com sucesso
                        if certificado:
                            await sync_to_async(setattr)(certificado, 'status', 'falha')
                            await sync_to_async(certificado.save)()
                            await page.screenshot(path=f'error_screenshot_cert_{certificado.id}.png')
                            logger.error(f"Erro na automação para o certificado ID {certificado.id}: {e}")
                        else:
                            logger.error(f"Erro inesperado antes de processar certificado ID {certificado_id}: {e}")
                        continue # Pula para o próximo certificado
                        
        except Exception as e:
            logger.error(f"Erro fatal durante a inicialização do navegador ou login: {e}")
            raise CommandError(f"Erro fatal: {e}")
        finally:
            if browser:
                await browser.close()
            # Limpeza de arquivos temporários e de depuração (incondicional)
            temp_files_to_remove = [
                'temp_automation.log',
                'debug_placa_nao_encontrada.png',
                'debug_pagina_veiculos.html',
                'debug_certificados.png',
                'debug_certificados.html',
            ]
            for f in temp_files_to_remove:
                if os.path.exists(f):
                    os.remove(f)
                    logger.info(f"Arquivo temporário removido: {f}")

    def handle(self, *args, **options):
        asyncio.run(self.handle_async(*args, **options))
