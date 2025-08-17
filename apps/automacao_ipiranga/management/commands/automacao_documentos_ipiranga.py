import asyncio
import logging
import os
import re
from argparse import ArgumentParser
from typing import Any

from asgiref.sync import sync_to_async
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from playwright.async_api import Page, async_playwright, expect
from django.conf import settings # Added import

from apps.automacao_ipiranga.models import (
    CertificadoVeiculo,
)
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

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Adiciona argumentos ao comando."""
        parser.add_argument(
            "certificado_id",
            type=int,
            help="O ID do CertificadoVeiculo a ser processado.",
        )

    async def handle_async(
        self, certificado_id: int, *args: Any, **options: Any
    ) -> None:
        """Lógica assínrona principal do comando de automação."""
        logger.info(
            f"[AUTOMACAO_IPIRANGA] handle_async iniciado para certificado ID: {certificado_id}"
        )

        # Global timeout for the automation process (90 seconds)
        automation_timeout = 90

        try:
            await asyncio.wait_for(
                self._run_automation_steps(certificado_id), timeout=automation_timeout
            )
        except TimeoutError:
            logger.error(
                f"AUTOMATION TIMEOUT: Automação para o certificado ID {certificado_id} excedeu o tempo limite de {automation_timeout} segundos."
            )
            raise CommandError(
                f"Automação excedeu o tempo limite de {automation_timeout} segundos."
            ) from None
        except Exception as e:
            logger.error(
                f"FALHA GERAL na automação para o certificado ID {certificado_id}: {e}",
                exc_info=True,
            )
            raise CommandError(f"Erro geral na automação: {e}") from e

    async def _run_automation_steps(self, certificado_id: int) -> None:
        certificado: CertificadoVeiculo | None = None
        file_path_upload: str | None = None
        try:
            certificado = await sync_to_async(
                CertificadoVeiculo.objects.select_related("veiculo").get
            )(pk=certificado_id)
            assert certificado is not None

            # Increment attempt counter at the very beginning
            certificado.tentativas_automacao = (certificado.tentativas_automacao or 0) + 1
            await sync_to_async(certificado.save)()
            logger.info(f"[AUTOMACAO_IPIRANGA] Certificado ID {certificado_id}: Tentativa {certificado.tentativas_automacao}")

            # Define max attempts (can be moved to settings.py)
            MAX_AUTOMATION_ATTEMPTS = 3

            # Check if max attempts reached
            if certificado.tentativas_automacao > MAX_AUTOMATION_ATTEMPTS:
                logger.error(f"Certificado ID {certificado_id} excedeu o número máximo de tentativas ({MAX_AUTOMATION_ATTEMPTS}). Marcando como falha_max_tentativas.")
                certificado.status = "falha_max_tentativas"
                await sync_to_async(certificado.save)()
                raise CommandError(f"Certificado ID {certificado_id} excedeu o número máximo de tentativas.")

            file_path_upload = certificado.arquivo.path
            logger.info(
                f"[AUTOMACAO_IPIRANGA] Certificado ID {certificado_id} encontrado."
            )
        except CertificadoVeiculo.DoesNotExist as err:
            logger.error(f"Certificado com ID {certificado_id} não encontrado.")
            raise CommandError(
                f"Certificado com ID {certificado_id} não encontrado."
            ) from err

        if file_path_upload is None:
            raise CommandError(
                "Caminho do arquivo de upload não encontrado para o certificado."
            )

        async with async_playwright() as p:
            browser: Any = None
            page: Page | None = None
            try:
                browser = await p.chromium.launch(headless=False)
                page = await browser.new_page()
                assert page is not None  # Ensure page is not None
                page.set_default_timeout(60000)
                logger.info("[AUTOMACAO_IPIRANGA] Página criada. Iniciando login...")

                await login_to_portran(page, logger)
                logger.info("Login realizado com sucesso.")

                placa_alvo: str = certificado.veiculo.placa  # type: ignore[reportUnknownMemberType]
                nome_certificado_alvo: str = certificado.nome  # type: ignore[reportUnknownMemberType]

                logger.info(
                    f"--- INÍCIO DA AUTOMAÇÃO PARA O CERTIFICADO ID: {certificado.id} ---"  # type: ignore[reportUnknownMemberType]
                )
                logger.info(f"Veículo Placa: {placa_alvo}")
                logger.info(f"Certificado: {nome_certificado_alvo}")
                logger.info(f"Arquivo: {file_path_upload}")

                if not os.path.exists(file_path_upload):
                    raise CommandError(
                        f"O arquivo do certificado não foi encontrado em: {file_path_upload}"
                    )

                vencidos_url = settings.IPIRANGA_VENCIDOS_URL # Used setting
                a_vencer_url = settings.IPIRANGA_A_VENCER_URL # Used setting

                placa_encontrada = False
                logger.info("Iniciando loop de navegação para páginas de veículos...")

                for url, nome_pagina in [
                    (vencidos_url, "Vencidos"),
                    (a_vencer_url, "À vencer"),
                ]:
                    logger.info(
                        f"[NAVEGACAO] Tentando navegar para a página: {nome_pagina} ({url})"
                    )
                    try:
                        await page.goto(url, timeout=60000)
                        logger.info(
                            f"[NAVEGACAO] Navegação para {nome_pagina} iniciada. URL atual após goto: {page.url}. Aguardando carregamento da rede..."
                        )
                        await page.wait_for_load_state("networkidle", timeout=60000)
                        logger.info(
                            f"[NAVEGACAO] Página {nome_pagina} carregada. URL final após networkidle: {page.url}"
                        )
                    except Exception as nav_error:
                        logger.error(
                            f"[ERRO_NAVEGACAO] Erro ao navegar ou carregar a página {nome_pagina} ({url}). URL atual: {page.url}. Erro: {nav_error}",
                            exc_info=True,
                        )
                        continue

                    logger.info(
                        f"[TABELA] Aguardando visibilidade da tabela 'table#tabela-veiculo' na página {nome_pagina}..."
                    )
                    try:
                        await page.locator("table#tabela-veiculo").wait_for(
                            state="visible", timeout=30000
                        )
                        logger.info(
                            f"[TABELA] Tabela 'table#tabela-veiculo' visível na página {nome_pagina}. URL atual: {page.url}"
                        )
                    except Exception as table_error:
                        logger.warning(
                            f"[ERRO_TABELA] Tabela 'table#tabela-veiculo' NÃO visível na página {nome_pagina} ({page.url}). Erro: {table_error}. Tentando próxima URL.",
                            exc_info=True,
                        )
                        continue

                    rows_locator = page.locator("table#tabela-veiculo tbody tr")
                    num_rows = await rows_locator.count()
                    logger.info(
                        f"[TABELA] Número de linhas encontradas na tabela: {num_rows} na página {nome_pagina}. URL atual: {page.url}"
                    )

                    for i in range(num_rows):
                        row_locator = rows_locator.nth(i)
                        placa_text = (
                            await row_locator.locator("td:nth-child(2)").text_content()
                            or ""
                        ).strip()
                        logger.info(
                            f"Verificando linha {i + 1}: Placa encontrada '{placa_text}' (Procurando por '{placa_alvo}')"
                        )
                        if placa_alvo in placa_text:
                            logger.info(
                                f"Placa '{placa_alvo}' encontrada na página {nome_pagina}! Clicando em 'alterar-veiculo-js'."
                            )
                            await row_locator.locator(
                                "a.btn.btn--square.alterar-veiculo-js"
                            ).click()
                            await page.wait_for_load_state("networkidle", timeout=60000)
                            logger.info(
                                f"Redirecionado após clique. URL atual: {page.url}"
                            )
                            placa_encontrada = True
                            break
                    if placa_encontrada:
                        break

                if not placa_encontrada:
                    raise CommandError(
                        f"Certificado '{nome_certificado_alvo}' (Vencido) não encontrado."  # type: ignore[reportUnknownMemberType]
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
                        str(nome_certificado_alvo).upper() in str(current_name).upper()  # type: ignore[reportUnknownArgumentType, reportUnknownMemberType]
                        and is_vencido
                    ):
                        logger.info(
                            f"Certificado '{nome_certificado_alvo}' (Vencido) encontrado."
                        )
                        # Add robust wait for the "Atualizar" button to be visible
                        logger.info("Aguardando botão 'Atualizar' ficar visível...")
                        await fieldset.locator(
                            "button.btn-atualizar-requisito"
                        ).wait_for(state="visible", timeout=30000)
                        logger.info("Botão 'Atualizar' visível. Clicando...")
                        await fieldset.locator("button.btn-atualizar-requisito").click()
                        await page.wait_for_load_state("networkidle")

                        # --- Start of new PDF processing logic ---
                        logger.info("Iniciando extração de texto do PDF...")
                        pdf_text = extract_text_from_pdf_image(file_path_upload, logger)
                        logger.info(
                            "Texto do PDF extraído. Identificando tipo de certificado..."
                        )

                        numero_documento_valor: str = "N/A"
                        vencimento_valor_pdf: str = "N/A"

                        if "CIPP" in str(nome_certificado_alvo).upper():  # type: ignore[reportUnknownMemberType]
                            logger.info(
                                "Tipo de certificado identificado como CIPP. Extraindo dados específicos..."
                            )
                            try:
                                numero_documento_valor, vencimento_valor_pdf = (
                                    extract_cipp_data(pdf_text, logger)
                                )
                                # NEW: Ensure numero_documento_valor contains only digits
                                numero_documento_valor = str(
                                    re.sub(r"\D", "", numero_documento_valor)
                                )  # type: ignore[reportUnknownMemberType]
                            except ValueError as ve:
                                logger.error(
                                    f"Erro na extração de dados do PDF: {ve}. Texto do PDF: {pdf_text[:1000]}..."
                                )
                                raise CommandError(
                                    f"Erro na extração de dados do PDF: {ve}"
                                ) from ve
                        else:
                            logger.warning(
                                f"Tipo de certificado '{nome_certificado_alvo}' não reconhecido. Extração de dados genérica ou falha."  # type: ignore[reportUnknownMemberType]
                            )

                        logger.info(
                            f"Número do Documento Extraído: {numero_documento_valor}"  # type: ignore[reportUnknownMemberType]
                        )
                        logger.info(
                            f"Data de Vencimento Extraída: {vencimento_valor_pdf}"  # type: ignore[reportUnknownMemberType]
                        )
                        # --- End of new PDF processing logic ---

                        # Construct dynamic IDs based on sequential numbering
                        # NEW: Extract the dynamic ID number from the input field within the current fieldset
                        # Find the input field for "Número do Documento" within the current fieldset
                        numero_input_locator = fieldset.locator(
                            "input[name^='licenca-numero-']"
                        )
                        logger.info(
                            f"DEBUG: numero_input_locator found: {await numero_input_locator.count() > 0}"
                        )

                        numero_input_id: (
                            str | None
                        ) = await numero_input_locator.get_attribute("id")
                        logger.info(f"DEBUG: numero_input_id: {numero_input_id}")

                        # Extract the number from the ID (e.g., "licenca-numero-2" -> "2")
                        match_id_number = re.search(
                            r"licenca-numero-(\d+)", numero_input_id or ""
                        )
                        if not match_id_number:
                            logger.error(
                                f"ERRO: Não foi possível extrair o número do ID para o campo 'Número do Documento' no certificado {nome_certificado_alvo}. numero_input_id: {numero_input_id}"  # type: ignore[reportUnknownMemberType]
                            )
                            raise CommandError(
                                f"Não foi possível extrair o número do ID para o campo 'Número do Documento' no certificado {nome_certificado_alvo}."  # type: ignore[reportUnknownMemberType]
                            )
                        dynamic_id_number: str = str(match_id_number.group(1))
                        logger.info(f"DEBUG: dynamic_id_number: {dynamic_id_number}")

                        # Construct dynamic IDs using the extracted number
                        numero_id: str = f"#licenca-numero-{dynamic_id_number}"
                        vencimento_id: str = f"#licenca-vencimento-{dynamic_id_number}"
                        logger.info(f"DEBUG: Constructed numero_id: {numero_id}")
                        logger.info(
                            f"DEBUG: Constructed vencimento_id: {vencimento_id}"
                        )

                        logger.info(
                            f"Preenchendo campo de número do documento: {numero_id} com valor {numero_documento_valor}"  # type: ignore[reportUnknownMemberType]
                        )
                        await page.wait_for_selector(numero_id, timeout=30000)
                        await page.fill(numero_id, numero_documento_valor)
                        logger.info(
                            f"Campo de número do documento preenchido. Valor: {numero_documento_valor}"  # type: ignore[reportUnknownMemberType]
                        )
                        await page.screenshot(
                            path=f"logs/screenshot_after_numero_fill_{certificado.id}.png"  # type: ignore[reportUnknownMemberType]
                        )

                        vencimento_formatado: str = convert_date_format(
                            vencimento_valor_pdf, logger
                        )
                        logger.info(
                            f"Preenchendo campo de vencimento: {vencimento_id} com valor {vencimento_formatado}"  # type: ignore[reportUnknownMemberType]
                        )
                        logger.info(
                            f"[AUTOMACAO_IPIRANGA] Vencimento formatado para preenchimento: {vencimento_formatado}"  # type: ignore[reportUnknownMemberType]
                        )
                        await page.wait_for_selector(vencimento_id, timeout=30000)
                        await page.fill(vencimento_id, vencimento_formatado)
                        await page.screenshot(
                            path=f"logs/screenshot_after_vencimento_fill_{certificado.id}.png"  # type: ignore[reportUnknownMemberType]
                        )
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
                await page.wait_for_load_state("networkidle", timeout=60000)
                await expect(page).to_have_url(
                    re.compile(r".*/veiculo/index"), timeout=60000
                )  # type: ignore[reportCallIssue]
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
                if certificado:
                    try:
                        certificado.status = "falha"
                        await sync_to_async(certificado.save)()
                        logger.info(f"Certificado ID {certificado_id} marcado como 'falha'.")
                    except Exception as save_error:
                        logger.error(f"Falha ao salvar status 'falha' para certificado ID {certificado_id}: {save_error}")

                if page:
                    try:
                        screenshot_path = os.path.join(
                            "logs",
                            f"error_screenshot_cert_{certificado_id}.png",  # type: ignore[reportUnknownMemberType]
                        )
                        await page.screenshot(path=screenshot_path)
                        logger.info(f"Screenshot de erro salvo em: {screenshot_path}")
                    except Exception as screenshot_error:
                        logger.error(f"Falha ao tirar screenshot: {screenshot_error}")

                raise CommandError(f"Erro na automação: {e}") from e

            finally:
                logger.info("FINALLY BLOCK: Entering finally block.")
                if browser:
                    await browser.close()
                    logger.info("FINALLY BLOCK: Browser closed.")
                # Cleanup: Delete certificate and associated file regardless of success or failure
                if certificado and certificado.pk:
                    logger.info(
                        f"FINALLY BLOCK: Attempting to delete Certificado ID {certificado.id} from DB."  # type: ignore[reportUnknownMemberType]
                    )
                    await sync_to_async(certificado.delete)()
                    logger.info(
                        f"FINALLY BLOCK: Certificado ID {certificado.id} deleted from DB."  # type: ignore[reportUnknownMemberType]
                    )
                    if file_path_upload and os.path.exists(file_path_upload):
                        logger.info(
                            f"FINALLY BLOCK: Attempting to delete file {file_path_upload}."
                        )
                        os.remove(file_path_upload)
                        logger.info(f"FINALLY BLOCK: File {file_path_upload} deleted.")
                    else:
                        logger.info(
                            f"FINALLY BLOCK: File {file_path_upload} not found or path not set. Skipping file deletion."
                        )
                    logger.info(
                        f"Certificado ID {certificado.id} e arquivo associado removidos no cleanup final."  # type: ignore[reportUnknownMemberType]
                    )
                else:
                    logger.info(
                        "FINALLY BLOCK: No certificate or primary key found for specific cleanup."
                    )

                logger.info("FINALLY BLOCK: Calling cleanup_automation_data.")

                await sync_to_async(call_command)("cleanup_automation_data")
                logger.info("FINALLY BLOCK: cleanup_automation_data called.")

    def handle(self, *args: Any, **options: Any) -> None:
        """Executa o comando de automação de forma síncrona."""
        try:
            asyncio.run(self.handle_async(options["certificado_id"], *args, **options))
        except CommandError as e:
            self.stderr.write(self.style.ERROR(f"Erro no comando: {e}"))
