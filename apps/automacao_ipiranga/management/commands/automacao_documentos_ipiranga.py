"""Comando Django para automatizar a atualização de documentos no portal Ipiranga."""

import asyncio
import logging
import os
import re
from argparse import ArgumentParser
from typing import Any

from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from playwright.async_api import Page, async_playwright, expect

from apps.automacao_ipiranga.models import CertificadoVeiculo
from apps.common.services import (
    extract_certificate_data_from_filename,
    login_to_portran,
)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Comando Django para automatizar a atualização de documentos no portal Ipiranga."""

    help = "Automatiza o processo de atualização de um único certificado no portal Ipiranga."

    def add_arguments(self, parser: ArgumentParser) -> None:  # noqa: PLR6301
        """Adiciona argumentos ao comando."""
        parser.add_argument(
            "certificado_id",
            type=int,
            help="O ID do CertificadoVeiculo a ser processado.",
        )

    async def handle_async(
        self, certificado_id: int, *args: str, **options: dict[str, Any]
    ) -> None:
        """Lógica assíncrona principal do comando de automação."""
        logger.info(
            f"[AUTOMACAO_IPIRANGA] handle_async iniciado para certificado ID: {certificado_id}"
        )
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

    async def _get_and_validate_certificado(  # noqa: PLR6301
        self, certificado_id: int
    ) -> CertificadoVeiculo:
        """Busca o certificado e realiza as validações iniciais."""
        try:
            certificado = await sync_to_async(
                CertificadoVeiculo.objects.select_related("veiculo").get
            )(pk=certificado_id)
            assert certificado is not None

            certificado.tentativas_automacao = (
                certificado.tentativas_automacao or 0
            ) + 1
            await sync_to_async(certificado.save)()
            logger.info(
                f"[AUTOMACAO_IPIRANGA] Certificado ID {certificado_id}: Tentativa {certificado.tentativas_automacao}"
            )

            max_automation_attempts = settings.MAX_AUTOMATION_ATTEMPTS
            if certificado.tentativas_automacao > max_automation_attempts:
                logger.error(
                    f"Certificado ID {certificado_id} excedeu o número máximo de tentativas ({max_automation_attempts}). Marcando como falha_max_tentativas."
                )
                certificado.status = "falha_max_tentativas"
                await sync_to_async(certificado.save)()
                raise CommandError(
                    f"Certificado ID {certificado_id} excedeu o número máximo de tentativas."
                )

            if not certificado.arquivo or not certificado.arquivo.path:
                raise CommandError("Caminho do arquivo de upload não encontrado.")

            return certificado  # type: ignore[reportReturnType]
        except CertificadoVeiculo.DoesNotExist as err:
            logger.error(f"Certificado com ID {certificado_id} não encontrado.")
            raise CommandError(
                f"Certificado com ID {certificado_id} não encontrado."
            ) from err

    async def _navigate_and_find_placa(self, page: Page, placa_alvo: str) -> bool:  # noqa: PLR6301
        """Navega pelas páginas de veículos e busca pela placa."""
        logger.info("Iniciando loop de navegação para páginas de veículos...")
        for url, nome_pagina in [
            (settings.IPIRANGA_VENCIDOS_URL, "Vencidos"),
            (settings.IPIRANGA_A_VENCER_URL, "À vencer"),
        ]:
            logger.info(
                f"[NAVEGACAO] Tentando navegar para a página: {nome_pagina} ({url})"
            )
            try:
                await page.goto(url, timeout=60000)
                await page.wait_for_load_state("networkidle", timeout=60000)
                logger.info(f"[NAVEGACAO] Página {nome_pagina} carregada.")
            except Exception as nav_error:
                logger.error(
                    f"[ERRO_NAVEGACAO] Erro ao carregar a página {nome_pagina}: {nav_error}"
                )
                continue

            try:
                await page.locator("table#tabela-veiculo").wait_for(
                    state="visible", timeout=30000
                )
                logger.info(f"[TABELA] Tabela visível na página {nome_pagina}.")
            except Exception as table_error:
                logger.warning(
                    f"[ERRO_TABELA] Tabela não visível na página {nome_pagina}: {table_error}"
                )
                continue

            rows_locator = page.locator("table#tabela-veiculo tbody tr")
            num_rows = await rows_locator.count()
            for i in range(num_rows):
                row_locator = rows_locator.nth(i)
                placa_text = (
                    await row_locator.locator("td:nth-child(2)").text_content() or ""
                ).strip()
                if placa_alvo in placa_text:
                    logger.info(
                        f"Placa '{placa_alvo}' encontrada! Clicando para alterar."
                    )
                    await row_locator.locator(
                        "a.btn.btn--square.alterar-veiculo-js"
                    ).click()
                    await page.wait_for_load_state("networkidle", timeout=60000)
                    return True
        return False

    async def _update_certificate(  # noqa: PLR6301
        self, page: Page, certificado: CertificadoVeiculo
    ) -> None:
        """Encontra e atualiza o certificado específico na página do veículo."""
        await page.locator("a#certificados-tab").click()
        await page.wait_for_load_state("networkidle", timeout=60000)

        certificate_fieldsets = page.locator("fieldset.certificado-box")
        num_certificates = await certificate_fieldsets.count()
        logger.info(f"Número de certificados encontrados: {num_certificates}")

        for i in range(num_certificates):
            fieldset = certificate_fieldsets.nth(i)
            current_name = (
                await fieldset.locator(".licenca-titulo .titulo.h3").text_content()
                or ""
            ).strip()
            is_vencido = (
                await fieldset.locator('*.badge--vermelho:has-text("Vencido")').count()
                > 0
            )

            if (
                str(certificado.nome).upper() in str(current_name).upper()
                and is_vencido
            ):
                logger.info(f"Certificado '{certificado.nome}' (Vencido) encontrado.")
                await fieldset.locator("button.btn-atualizar-requisito").click()
                await page.wait_for_load_state("networkidle")

                try:
                    extracted_data = extract_certificate_data_from_filename(
                        os.path.basename(certificado.arquivo.path), logger
                    )
                except ValueError as ve:
                    raise CommandError(
                        f"Erro ao extrair dados do nome do arquivo: {ve}"
                    ) from ve

                numero_input_id = await fieldset.locator(
                    "input[name^='licenca-numero-']"
                ).get_attribute("id")
                match_id = re.search(r"licenca-numero-(\d+)", numero_input_id or "")
                if not match_id:
                    raise CommandError(
                        "Não foi possível extrair o ID dinâmico do campo."
                    )
                dynamic_id = match_id.group(1)

                await page.fill(
                    f"#licenca-numero-{dynamic_id}", extracted_data.numero_certificado
                )
                await page.fill(
                    f"#licenca-vencimento-{dynamic_id}",
                    extracted_data.data_vencimento_formatada,
                )
                await fieldset.locator('input[type="file"]:visible').set_input_files(
                    certificado.arquivo.path
                )
                await fieldset.locator(
                    'button:has-text("Enviar novo certificado")'
                ).click()
                await page.wait_for_timeout(3000)
                return

        raise CommandError(
            f"Certificado '{certificado.nome}' (Vencido) não encontrado."
        )

    async def _check_other_expired_and_save(  # noqa: PLR6301
        self, page: Page, certificado: CertificadoVeiculo
    ) -> None:
        """Verifica se há outros certificados vencidos antes de salvar."""
        logger.info("Verificando outros certificados vencidos antes de salvar...")
        certificate_fieldsets = page.locator("fieldset.certificado-box")
        num_certificates = await certificate_fieldsets.count()

        for i in range(num_certificates):
            fieldset = certificate_fieldsets.nth(i)
            current_name = (
                await fieldset.locator(".licenca-titulo .titulo.h3").text_content()
                or ""
            ).strip()
            is_vencido = (
                await fieldset.locator('*.badge--vermelho:has-text("Vencido")').count()
                > 0
            )

            if (
                is_vencido
                and str(certificado.nome).upper() not in str(current_name).upper()
            ):
                error_msg = f"Não foi possível salvar: Outro certificado vencido encontrado ({current_name}) para o veículo {certificado.veiculo.placa}."
                certificado.status = "falha_outros_vencidos"
                certificado.error_message = error_msg
                await sync_to_async(certificado.save)()
                raise CommandError(error_msg)

        logger.info(
            "Nenhum outro certificado vencido encontrado. Clicando em Salvar..."
        )
        await page.locator("a#botaoAtualizar").click()
        await expect(page).to_have_url(re.compile(r".*/veiculo/index"), timeout=60000)
        logger.info("Operação salva com sucesso e página redirecionada.")

    async def _run_automation_steps(self, certificado_id: int) -> None:
        """Orquestra as etapas da automação."""
        certificado = await self._get_and_validate_certificado(certificado_id)
        browser = None
        page = None
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=False)
                page = await browser.new_page()
                page.set_default_timeout(60000)

                await login_to_portran(page, logger)

                placa_encontrada = await self._navigate_and_find_placa(
                    page, certificado.veiculo.placa
                )
                if not placa_encontrada:
                    raise CommandError(
                        f"Placa {certificado.veiculo.placa} não encontrada no portal."
                    )

                await self._update_certificate(page, certificado)
                await self._check_other_expired_and_save(page, certificado)

        except Exception as e:
            logger.error(
                f"FALHA na automação para o certificado ID {certificado_id}: {e}",
                exc_info=True,
            )
            certificado.status = "falha"
            await sync_to_async(certificado.save)()
            if page:
                await page.screenshot(
                    path=f"logs/error_screenshot_cert_{certificado_id}.png"
                )
            raise CommandError(f"Erro na automação: {e}") from e
        finally:
            if browser:
                await browser.close()
            # Final cleanup is handled by a separate management command or process

    def handle(self, *args: str, **options: dict[str, Any]) -> None:
        """Executa o comando de automação de forma síncrona."""
        try:
            # Extract certificado_id from options, if it exists
            certificado_id = options.pop("certificado_id", None)
            if certificado_id is None:
                raise CommandError("certificado_id é um argumento obrigatório.")

            # Pass the extracted certificado_id and the remaining options to handle_async
            asyncio.run(self.handle_async(certificado_id, *args, **options))  # type: ignore[reportArgumentType]
        except CommandError as e:
            self.stderr.write(self.style.ERROR(f"Erro no comando: {e}"))
