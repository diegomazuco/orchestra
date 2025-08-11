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
    extract_cipp_data,
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

        certificado = None
        file_path_upload = None
        try:
            certificado = await sync_to_async(
                CertificadoVeiculo.objects.select_related("veiculo").get
            )(pk=certificado_id)
            file_path_upload = certificado.arquivo.path
            logger.info(
                f"[AUTOMACAO_IPIRANGA] Certificado ID {certificado_id} encontrado."
            )
        except CertificadoVeiculo.DoesNotExist as err:
            logger.error(f"Certificado com ID {certificado_id} não encontrado.")
            raise CommandError(
                f"Certificado com ID {certificado_id} não encontrado."
            ) from err

        async with async_playwright() as p:
            browser = None
            page = None
            try:
                browser = await p.chromium.launch(
                    headless=False
                )  # Keep headless=False for debugging
                page = await browser.new_page()
                page.set_default_timeout(60000)
                logger.info("[AUTOMACAO_IPIRANGA] Página criada. Iniciando login...")

                await login_to_portran(page, logger)
                logger.info("Login realizado com sucesso.")

                placa_alvo = certificado.veiculo.placa
                nome_certificado_alvo = certificado.nome

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

                # --- Start of new PDF processing logic ---
                logger.info("Iniciando extração de texto do PDF...")
                pdf_text = extract_text_from_pdf_image(file_path_upload, logger)
                logger.info(
                    "Texto do PDF extraído. Identificando tipo de certificado..."
                )

                numero_documento_valor = "N/A"
                vencimento_valor_pdf = "N/A"

                if "CIPP" in nome_certificado_alvo.upper():
                    logger.info(
                        "Tipo de certificado identificado como CIPP. Extraindo dados específicos..."
                    )
                    try:
                        numero_documento_valor, vencimento_valor_pdf = (
                            extract_cipp_data(pdf_text, logger)
                        )
                    except ValueError as ve:
                        raise CommandError(
                            f"Erro na extração de dados do PDF: {ve}"
                        ) from ve
                else:
                    logger.warning(
                        f"Tipo de certificado '{nome_certificado_alvo}' não reconhecido. Extração de dados genérica ou falha."
                    )
                    # For now, it will remain "N/A" if not CIPP

                logger.info(f"Número do Documento Extraído: {numero_documento_valor}")
                logger.info(f"Data de Vencimento Extraída: {vencimento_valor_pdf}")
                # --- End of new PDF processing logic ---

                vencidos_url = "https://sites.redeipiranga.com.br/WAPortranNew/veiculo/index?situacoesDocumentos=2&status=1,2,3,4,7"
                a_vencer_url = "https://sites.redeipiranga.com.br/WAPortranNew/veiculo/index?situacoesDocumentos=3&status=1,2,3,4,7"

                placa_encontrada = False
                logger.info("Iniciando loop de navegação para páginas de veículos...")

                for url, nome_pagina in [
                    (vencidos_url, "Vencidos"),
                    (a_vencer_url, "À vencer"),
                ]:
                    await page.goto(url, timeout=60000)
                    await page.wait_for_load_state("networkidle", timeout=60000)

                    await page.locator("table#tabela-veiculo").wait_for(
                        state="visible", timeout=30000
                    )

                    rows = page.locator("table#tabela-veiculo tbody tr")
                    num_rows = await rows.count()
                    logger.info(f"Número de linhas encontradas na tabela: {num_rows}")

                    for i in range(num_rows):
                        row = rows.nth(i)
                        placa_text = (
                            await row.locator("td:nth-child(2)").text_content() or ""
                        ).strip()
                        if placa_alvo in placa_text:
                            logger.info(
                                f"Placa '{placa_alvo}' encontrada na página {nome_pagina}!"
                            )
                            await row.locator(
                                "a.btn.btn--square.alterar-veiculo-js"
                            ).click()
                            await page.wait_for_load_state("networkidle", timeout=60000)
                            placa_encontrada = True
                            break
                    if placa_encontrada:
                        break

                if not placa_encontrada:
                    raise CommandError(
                        f"Certificado '{nome_certificado_alvo}' (Vencido) não encontrado."
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

                    if (
                        nome_certificado_alvo.upper() in current_name.upper()
                        and is_vencido
                    ):
                        logger.info(
                            f"Certificado '{nome_certificado_alvo}' (Vencido) encontrado."
                        )
                        await fieldset.locator("button.btn-atualizar-requisito").click()
                        await page.wait_for_load_state("networkidle")

                        # Construct dynamic IDs based on sequential numbering
                        numero_id = f"#licenca-numero-{i + 1}"
                        vencimento_id = f"#licenca-vencimento-{i + 1}"

                        await page.wait_for_selector(numero_id, timeout=30000)
                        await page.fill(numero_id, numero_documento_valor)
                        vencimento_formatado = convert_date_format(
                            vencimento_valor_pdf, logger
                        )
                        logger.info(
                            f"[AUTOMACAO_IPIRANGA] Vencimento formatado para preenchimento: {vencimento_formatado}"
                        )
                        await page.wait_for_selector(vencimento_id, timeout=30000)
                        await page.fill(vencimento_id, vencimento_formatado)
                        await fieldset.locator(
                            'input[type="file"]:visible'
                        ).set_input_files(file_path_upload)

                        await fieldset.locator(
                            'button:has-text("Enviar novo certificado")'
                        ).click()
                        await page.locator(
                            'span.js-successArea:has-text("sucesso")'
                        ).wait_for(timeout=60000)
                        logger.info("Mensagem de sucesso encontrada.")

                        found_certificate = True
                        break

                if not found_certificate:
                    raise CommandError(
                        f"Certificado '{nome_certificado_alvo}' (Vencido) não encontrado."
                    )

                logger.info("Clicando no botão 'Atualizar'...")
                await page.locator("a#botaoAtualizar").click()
                await page.wait_for_load_state(
                    "networkidle", timeout=60000
                )  # Added this
                await expect(page).to_have_url(
                    re.compile(r".*/veiculo/index"), timeout=60000
                )
                logger.info("Operação salva com sucesso.")

                logger.info("Clicando no botão 'Salvar'...")
                await page.locator("#botaoAtualizar").click()
                await page.wait_for_load_state("networkidle", timeout=60000)
                logger.info("Botão 'Salvar' clicado com sucesso.")

            except Exception as e:
                logger.error(
                    f"FALHA na automação para o certificado ID {certificado_id}: {e}",
                    exc_info=True,
                )
                if "certificado" in locals() and certificado:
                    await sync_to_async(setattr)(certificado, "status", "falha")
                    await sync_to_async(certificado.save)()

                if page:
                    try:
                        screenshot_path = os.path.join(
                            "logs", f"error_screenshot_cert_{certificado_id}.png"
                        )
                        await page.screenshot(path=screenshot_path)
                        logger.info(f"Screenshot de erro salvo em: {screenshot_path}")
                    except Exception as screenshot_error:
                        logger.error(f"Falha ao tirar screenshot: {screenshot_error}")

                raise CommandError(f"Erro na automação: {e}") from e

            finally:
                if browser:
                    await browser.close()
                # Cleanup: Delete certificate and associated file regardless of success or failure
                if certificado and certificado.pk:
                    await sync_to_async(certificado.delete)()
                    if file_path_upload and os.path.exists(file_path_upload):
                        os.remove(file_path_upload)
                    logger.info(
                        f"Certificado ID {certificado.id} e arquivo associado removidos no cleanup final."
                    )

    def handle(self, *args, **options):
        """Executa o comando de automação de forma síncrona."""
        try:
            asyncio.run(self.handle_async(*args, **options))
        except CommandError as e:
            self.stderr.write(self.style.ERROR(f"Erro no comando: {e}"))
