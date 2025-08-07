import asyncio
import logging
import os
import re

from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand, CommandError
from playwright.async_api import async_playwright, expect

from apps.automacao_ipiranga.models import CertificadoVeiculo
from apps.common.services import (
    convert_date_format,
    extract_text_from_pdf_image,
    login_to_portran,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Comando Django para automatizar a atualização de documentos no portal Ipiranga."""

    help = "Automatiza o processo de atualização de um único certificado no portal Ipiranga."

    def add_arguments(self, parser):
        """Adiciona argumentos ao comando."""
        parser.add_argument(
            "certificado_id",
            type=int,
            help="O ID do CertificadoVeiculo a ser processado.",
        )

    async def handle_async(self, certificado_id, *args, **options):
        """Lógica assíncrona principal do comando de automação."""
        logger.info(
            f"[AUTOMACAO_IPIRANGA] handle_async iniciado para certificado ID: {certificado_id}"
        )
        browser = None
        certificado = None
        try:
            logger.info(
                "[AUTOMACAO_IPIRANGA] Buscando certificado no banco de dados..."
            )
            certificado = await sync_to_async(
                CertificadoVeiculo.objects.select_related("veiculo").get
            )(pk=certificado_id)
            logger.info(
                f"[AUTOMACAO_IPIRANGA] Certificado ID {certificado_id} encontrado."
            )

            logger.info("[AUTOMACAO_IPIRANGA] Iniciando Playwright...")
            async with async_playwright() as p:
                logger.info("[AUTOMACAO_IPIRANGA] Lançando navegador Chromium...")
                browser = await p.chromium.launch(headless=False)
                logger.info(
                    "[AUTOMACAO_IPIRANGA] Navegador lançado. Criando nova página..."
                )
                page = await browser.new_page()
                page.set_default_timeout(
                    30000
                )  # Timeout padrão de 30 segundos para operações da página
                logger.info("[AUTOMACAO_IPIRANGA] Página criada. Iniciando login...")

                logger.info("Iniciando login no portal Ipiranga...")
                await login_to_portran(page, logger)
                logger.info("Login realizado com sucesso.")
                logger.info(f"URL atual após login: {page.url}")

                placa_alvo = certificado.veiculo.placa
                nome_certificado_alvo = certificado.nome
                file_path_upload = certificado.arquivo.path

                logger.info(
                    f"--- INÍCIO DA AUTOMAÇÃO PARA O CERTIFICADO ID: {certificado.id} ---"
                )
                logger.info(f"Veículo Placa: {placa_alvo}")
                logger.info(f"Certificado: {nome_certificado_alvo}")
                logger.info(f"Arquivo: {file_path_upload}")

                if not os.path.exists(file_path_upload):
                    raise CommandError(
                        f"O arquivo do certificado não foi encontrado em: {file_path_upload}"
                    )

                try:
                    logger.info("Iniciando extração de texto do PDF...")
                    pdf_text = extract_text_from_pdf_image(file_path_upload, logger)
                    logger.info(
                        "Texto do PDF extraído. Buscando bloco de certificado..."
                    )
                    match = re.search(
                        r"(CERTIFICADO DE INSPEÇÃO(?: VEICULAR)?.*)",
                        pdf_text,
                        re.IGNORECASE | re.DOTALL,
                    )

                    if not match:
                        raise CommandError(
                            "Não foi possível encontrar um bloco de 'CERTIFICADO DE INSPEÇÃO' no PDF."
                        )

                    first_block = match.group(1)
                    logger.info(
                        "Bloco de certificado encontrado. Extraindo número do documento..."
                    )
                    match_numero = re.search(
                        r"([A-Z0-9]{1,3}\.\d{3}\.\d{3})", first_block
                    )
                    numero_documento_valor = (
                        re.sub(r"\D", "", match_numero.group(1))
                        if match_numero
                        else "N/A"
                    )
                    logger.info("Número do documento extraído. Extraindo datas...")
                    all_dates = re.findall(
                        r"\b(\d{2}/[A-Z]{3}/\d{2})\b", first_block, re.IGNORECASE
                    )
                    vencimento_valor_pdf = all_dates[-1] if all_dates else "N/A"
                    logger.info("Datas extraídas. Processamento do PDF concluído.")

                except Exception as e:
                    logger.error(
                        f"Erro durante o processamento do PDF: {e}", exc_info=True
                    )
                    raise CommandError(
                        f"Erro durante o processamento do PDF: {e}"
                    ) from e

                logger.info(f"Número do Documento Extraído: {numero_documento_valor}")
                logger.info(f"Data de Vencimento Extraída: {vencimento_valor_pdf}")

                vencidos_url = "https://sites.redeipiranga.com.br/WAPortranNew/veiculo/index?situacoesDocumentos=2&status=1,2,3,4,7"
                a_vencer_url = "https://sites.redeipiranga.com.br/WAPortranNew/veiculo/index?situacoesDocumentos=3&status=1,2,3,4,7"

                placa_encontrada = False
                logger.info("Iniciando loop de navegação para páginas de veículos...")
                try:
                    for url, nome_pagina in [
                        (vencidos_url, "Vencidos"),
                        (a_vencer_url, "À vencer"),
                    ]:
                        logger.info(f"Navegando para a página: {nome_pagina} ({url})")
                        await page.goto(url, timeout=60000)
                        await page.wait_for_load_state("networkidle", timeout=60000)

                        # Esperar pelo seletor da tabela
                        await page.locator("table#tabela-veiculo").wait_for(
                            state="visible", timeout=30000
                        )

                        table_content = await page.locator(
                            "table#tabela-veiculo"
                        ).text_content()
                        logger.info(f"""Conteúdo da tabela na página {nome_pagina}:
{(table_content or "")[:1000]}...""")  # Log dos primeiros 1000 caracteres

                        rows = page.locator("table#tabela-veiculo tbody tr")
                        num_rows = await rows.count()
                        logger.info(
                            f"Número de linhas encontradas na tabela: {num_rows}"
                        )

                        for i in range(num_rows):
                            row = rows.nth(i)
                            placa_text = (
                                await row.locator("td:nth-child(2)").text_content()
                                or ""
                            ).strip()
                            logger.info(
                                f"Verificando linha {i + 1}: Placa encontrada na linha: '{placa_text}'"
                            )
                            if placa_alvo in placa_text:
                                logger.info(
                                    f"Placa '{placa_alvo}' encontrada na página {nome_pagina}!"
                                )
                                await row.locator(
                                    "a.btn.btn--square.alterar-veiculo-js"
                                ).click()
                                await page.wait_for_load_state(
                                    "networkidle", timeout=60000
                                )
                                placa_encontrada = True
                                break
                        if placa_encontrada:
                            break
                except Exception as e:
                    logger.error(
                        f"Erro durante a navegação ou busca de placa: {e}",
                        exc_info=True,
                    )
                    raise CommandError(
                        f"Erro durante a navegação ou busca de placa: {e}"
                    ) from e

                if not placa_encontrada:
                    raise CommandError(
                        f"Placa '{placa_alvo}' não encontrada nas páginas de vencidos/a vencer."
                    )

                logger.info("Clicando na aba 'Certificados'...")
                await page.locator("a#certificados-tab").click()
                await page.wait_for_load_state("networkidle")

                certificate_fieldsets = page.locator("fieldset.certificado-box")
                found_certificate = False
                num_certificates = await certificate_fieldsets.count()
                logger.info(f"Número de certificados encontrados: {num_certificates}")

                for i in range(num_certificates):
                    fieldset = certificate_fieldsets.nth(i)
                    current_name = (
                        await fieldset.locator(
                            ".licenca-titulo .titulo.h3"
                        ).text_content()
                        or ""
                    ).strip()
                    is_vencido = (
                        await fieldset.locator(
                            '*.badge--vermelho:has-text("Vencido")'
                        ).count()
                        > 0
                    )

                    logger.info(
                        f"Verificando certificado {i + 1}: Nome: '{current_name}' , Vencido: {is_vencido}"
                    )

                    if (
                        nome_certificado_alvo.upper() in current_name.upper()
                        and is_vencido
                    ):
                        logger.info(
                            f"Certificado '{nome_certificado_alvo}' (Vencido) encontrado."
                        )
                        await fieldset.locator("button.btn-atualizar-requisito").click()
                        await page.wait_for_load_state("networkidle")

                        logger.info(
                            f"Preenchendo número do documento: {numero_documento_valor}"
                        )
                        await page.fill("#licenca-numero-1", numero_documento_valor)
                        vencimento_formatado = convert_date_format(vencimento_valor_pdf)
                        logger.info(
                            f"Preenchendo data de vencimento: {vencimento_formatado}"
                        )
                        await page.fill("#licenca-vencimento-1", vencimento_formatado)
                        logger.info(f"Anexando arquivo: {file_path_upload}")
                        await fieldset.locator(
                            'input[type="file"]:visible'
                        ).set_input_files(file_path_upload)

                        logger.info("Clicando em 'Enviar novo certificado'...")
                        await fieldset.locator(
                            'button:has-text("Enviar novo certificado")'
                        ).click()
                        logger.info("Aguardando mensagem de sucesso...")
                        await page.locator(
                            'span.js-successArea:has-text("sucesso")'
                        ).wait_for(timeout=30000)
                        logger.info("Mensagem de sucesso encontrada.")

                        found_certificate = True
                        break

                if not found_certificate:
                    raise CommandError(
                        f"Certificado '{nome_certificado_alvo}' (Vencido) não encontrado."
                    )

                logger.info("Clicando no botão 'Atualizar'...")
                await page.locator("a#botaoAtualizar").click()
                logger.info("Aguardando redirecionamento para a página de veículos...")
                await expect(page).to_have_url(
                    re.compile(r".*/veiculo/index"), timeout=60000
                )
                logger.info("Operação salva com sucesso.")

                await sync_to_async(certificado.delete)()
                if os.path.exists(file_path_upload):
                    os.remove(file_path_upload)

                logger.info(
                    f"SUCESSO: Certificado ID {certificado.id} processado e removido."
                )

        except Exception as e:
            logger.error(
                f"FALHA na automação para o certificado ID {certificado_id}: {e}",
                exc_info=True,
            )
            if certificado:
                await sync_to_async(setattr)(certificado, "status", "falha")
                await sync_to_async(certificado.save)()
            if browser and page:
                screenshot_path = os.path.join(
                    "logs", f"error_screenshot_cert_{certificado_id}.png"
                )
                await page.screenshot(path=screenshot_path)
                logger.error(f"Screenshot de erro salvo em: {screenshot_path}")
            raise CommandError(f"Erro na automação: {e}") from e
        finally:
            if browser:
                await browser.close()

    def handle(self, *args, **options):
        """Executa o comando de automação de forma síncrona."""
        try:
            asyncio.run(self.handle_async(*args, **options))
        except CommandError as e:
            self.stderr.write(self.style.ERROR(f"Erro no comando: {e}"))
