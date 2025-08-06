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
                browser = await p.chromium.launch(headless=True)
                logger.info(
                    "[AUTOMACAO_IPIRANGA] Navegador lançado. Criando nova página..."
                )
                page = await browser.new_page()
                logger.info("[AUTOMACAO_IPIRANGA] Página criada. Iniciando login...")

                logger.info("Iniciando login no portal Ipiranga...")
                await login_to_portran(page, logger)
                logger.info("Login realizado com sucesso.")

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

                pdf_text = extract_text_from_pdf_image(file_path_upload, logger)
                pdf_blocks = re.split(r"CERTIFICADO DE INSPEÇÃO VEICULAR", pdf_text)

                if len(pdf_blocks) < 2:
                    raise CommandError(
                        "Não foi possível encontrar um bloco de 'CERTIFICADO DE INSPEÇÃO VEICULAR' no PDF."
                    )

                first_block = pdf_blocks[1]
                match_numero = re.search(r"([A-Z0-9]{1,3}\.\d{3}\.\d{3})", first_block)
                numero_documento_valor = (
                    re.sub(r"\D", "", match_numero.group(1)) if match_numero else "N/A"
                )
                all_dates = re.findall(
                    r"\b(\d{2}/[A-Z]{3}/\d{2})\b", first_block, re.IGNORECASE
                )
                vencimento_valor_pdf = all_dates[-1] if all_dates else "N/A"

                logger.info(f"Número do Documento Extraído: {numero_documento_valor}")
                logger.info(f"Data de Vencimento Extraída: {vencimento_valor_pdf}")

                vencidos_url = "https://sites.redeipiranga.com.br/WAPortranNew/veiculo/index?situacoesDocumentos=2&status=1,2,3,4,7"
                a_vencer_url = "https://sites.redeipiranga.com.br/WAPortranNew/veiculo/index?situacoesDocumentos=3&status=1,2,3,4,7"

                placa_encontrada = False
                for url, nome_pagina in [
                    (vencidos_url, "Vencidos"),
                    (a_vencer_url, "À vencer"),
                ]:
                    await page.goto(url, timeout=60000)
                    await page.wait_for_load_state("networkidle", timeout=60000)
                    rows = page.locator("table#tabela-veiculo tbody tr")
                    for i in range(await rows.count()):
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
                    raise CommandError(f"Placa '{placa_alvo}' não encontrada.")

                await page.locator("a#certificados-tab").click()
                await page.wait_for_load_state("networkidle")

                certificate_fieldsets = page.locator("fieldset.certificado-box")
                found_certificate = False
                for i in range(await certificate_fieldsets.count()):
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

                        await page.fill("#licenca-numero-1", numero_documento_valor)
                        vencimento_formatado = convert_date_format(vencimento_valor_pdf)
                        await page.fill("#licenca-vencimento-1", vencimento_formatado)
                        await fieldset.locator(
                            'input[type="file"]:visible'
                        ).set_input_files(file_path_upload)

                        await fieldset.locator(
                            'button:has-text("Enviar novo certificado")'
                        ).click()
                        await page.locator(
                            'span.js-successArea:has-text("sucesso")'
                        ).wait_for(timeout=30000)

                        found_certificate = True
                        break

                if not found_certificate:
                    raise CommandError(
                        f"Certificado '{nome_certificado_alvo}' (Vencido) não encontrado."
                    )

                await page.locator("a#botaoAtualizar").click()
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
