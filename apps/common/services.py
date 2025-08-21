import asyncio
import logging
import re

from decouple import config
from django.conf import settings
from playwright.async_api import Page, expect


async def login_to_portran(page: Page, logger: logging.Logger) -> None:
    """Realiza o login no portal Portran/Ipiranga de forma centralizada e robusta."""
    logger.info("--- Iniciando etapa de login centralizada ---")

    portran_user = config("PORTRAN_USER")
    portran_password = config("PORTRAN_PASSWORD")

    if not portran_user or not portran_password:
        logger.error(
            "As variáveis de ambiente PORTRAN_USER e PORTRAN_PASSWORD devem ser configuradas."
        )
        raise ValueError("Credenciais não encontradas no .env")

    try:
        logger.info("Navegando para a página de login...")
        await page.goto(
            settings.IPIRANGA_LOGIN_URL,
            timeout=60000,
        )

        logger.info("Aguardando seletor de usuário.")
        user_selector = page.locator("#codigoUsuario")
        await user_selector.wait_for(state="visible", timeout=60000)

        logger.info("Preenchendo usuário...")
        await user_selector.fill(str(portran_user))

        logger.info("Preenchendo senha...")
        await page.locator("#senha").fill(str(portran_password))

        logger.info("Clicando em 'Autenticar'...")
        await page.locator('input[type="submit"][value="Autenticar"]').click()

        # --- Lógica de Resiliência para Instabilidade de Login ---
        try:
            # Espera principal: redirecionamento para o dashboard
            logger.info("Aguardando redirecionamento para o dashboard...")
            await expect(page).to_have_url(
                settings.IPIRANGA_DASHBOARD_URL,
                timeout=15000,  # Timeout reduzido para falhar rápido
            )
        except Exception:
            logger.warning(
                "Redirecionamento para o dashboard não ocorreu no tempo esperado. Verificando possível erro de instabilidade."
            )

            # Verifica se a mensagem de erro inesperado está visível
            error_message_locator = page.locator(
                'p:has-text("Erro Inesperado. Favor tente novamente.")'
            )
            if await error_message_locator.is_visible():
                logger.warning(
                    "Detectada página de 'Erro Inesperado'. Tentando recuperar a sessão..."
                )
                await asyncio.sleep(
                    5
                )  # Pausa estratégica para aguardar a estabilização da sessão após erro inesperado.
                logger.info("Atualizando a página para tentar autenticar a sessão.")
                await page.reload(wait_until="domcontentloaded")

                # Tenta verificar o URL do dashboard novamente após o reload
                logger.info(
                    "Aguardando redirecionamento para o dashboard após a atualização..."
                )
                await expect(page).to_have_url(
                    "https://sites.redeipiranga.com.br/WAPortranNew/dashboard/index",
                    timeout=60000,
                )
            else:
                logger.error(
                    "A página de erro inesperado não foi encontrada, mas o login falhou."
                )
                raise  # Re-levanta a exceção original se o erro não for o esperado
        # --- Fim da Lógica de Resiliência ---

        logger.info("Login realizado com sucesso!")
        logger.info("--- Fim da etapa de login ---")

    except Exception as e:
        logger.error(f"Falha na etapa de login: {e}")
        await page.screenshot(path="login_error_screenshot.png")
        logger.error(
            "Screenshot de erro de login capturado em 'login_error_screenshot.png'."
        )
        raise  # Re-levanta a exceção para que o comando que chamou saiba que falhou


def extract_certificate_data_from_filename(
    filename: str, logger: logging.Logger
) -> tuple[str, str]:
    """Extrai o número do certificado e a data de vencimento do nome do arquivo.

    Formato esperado: PLACA_TIPOLICENCA_NUMEROCERTIFICADO_DDMMYYYY.pdf
    Exemplo: ABC1234_CIPP_T123456_25122025.pdf
    """
    logger.info(f"Extraindo dados do nome do arquivo: {filename}")

    # Regex para o novo formato: PLACA_TIPOLICENCA_NUMEROCERTIFICADO_DDMMYYYY.pdf
    match = re.match(
        r"([A-Z0-9]+)_([A-Z0-9]+)_([A-Z0-9]+)_(\d{8})\.pdf", filename, re.IGNORECASE
    )

    if not match:
        logger.error(f"Formato de nome de arquivo inválido: {filename}")
        raise ValueError(f"Formato de nome de arquivo inválido: {filename}")

    numero_certificado = match.group(3)
    data_vencimento_raw = match.group(4)

    # Converte DDMMYYYY para DD/MM/YYYY
    if len(data_vencimento_raw) == 8:
        day = data_vencimento_raw[0:2]
        month = data_vencimento_raw[2:4]
        year = data_vencimento_raw[4:8]
        data_vencimento_formatada = f"{day}/{month}/{year}"
    else:
        logger.error(
            f"Formato de data de vencimento inválido no nome do arquivo: {data_vencimento_raw}"
        )
        raise ValueError(
            f"Formato de data de vencimento inválido: {data_vencimento_raw}"
        )

    logger.info(
        f"Dados extraídos: Número do Certificado={numero_certificado}, Data de Vencimento={data_vencimento_formatada}"
    )
    return numero_certificado, data_vencimento_formatada
