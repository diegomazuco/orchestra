import asyncio
import io
import logging

import fitz  # PyMuPDF # type: ignore
import pytesseract  # type: ignore
from decouple import config
from PIL import Image
from playwright.async_api import Page, expect


async def login_to_portran(page: Page, logger: logging.Logger):
    """Realiza o login no portal Portran/Ipiranga de forma centralizada e robusta.

    Args:
        page: A instância da página do Playwright.
        logger: A instância do logger para registrar os passos.
    """
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
            "https://sites.redeipiranga.com.br/WAPortranNew/usuario/exibir",
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
                "https://sites.redeipiranga.com.br/WAPortranNew/dashboard/index",
                timeout=15000,
            )  # Timeout reduzido para falhar rápido
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
                await asyncio.sleep(5)  # Pausa estratégica
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


def extract_text_from_pdf_image(
    pdf_path: str, logger: logging.Logger, tesseract_config: str = ""
) -> str:
    """Extrai texto de imagens dentro de um arquivo PDF usando PyMuPDF e Tesseract OCR.

    Args:
        pdf_path: O caminho absoluto para o arquivo PDF.
        logger: A instância do logger para registrar os passos.
        tesseract_config: Configurações adicionais para o Tesseract (ex: '--psm 6').

    Returns:
        O texto extraído das imagens do PDF.
    """
    text = ""
    # Configurações padrão para o Tesseract, se não forem fornecidas
    if not tesseract_config:
        tesseract_config = "--psm 6"  # Modo padrão para documentos estruturados

    doc = None  # Inicializa doc como None
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)

            # Renderiza a página como uma imagem (pixmap) com alta resolução
            # Aumentar a resolução para 300 DPI (padrão é 72 DPI)
            pix = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72))  # type: ignore
            img = Image.open(io.BytesIO(pix.tobytes()))

            # Pré-processamento básico da imagem (binarização)
            img = img.convert("L")  # Converte para escala de cinza
            img = img.point(lambda x: 0 if x < 128 else 255, "1")  # type: ignore # Binarização simples

            # Realiza OCR na imagem
            page_text = pytesseract.image_to_string(
                img, lang="por", config=tesseract_config
            )  # lang='por' para português
            text += page_text
            logger.info(
                f"Texto extraído da página {page_num + 1}:\n{page_text[:500]}..."
            )  # Log dos primeiros 500 caracteres

    except Exception as e:
        logger.error(f"Erro ao extrair texto de imagem do PDF {pdf_path}: {e}")
        raise
    finally:
        if "doc" in locals() and doc:
            doc.close()
    return text


def convert_date_format(date_str: str) -> str:
    """Converte uma string de data do formato 'DD/MON/YY' para 'DD/MM/YYYY'.

    Ex: '30/JUL/26' -> '30/07/2026'.
    """
    month_map = {
        "JAN": "01",
        "FEB": "02",
        "MAR": "03",
        "APR": "04",
        "MAY": "05",
        "JUN": "06",
        "JUL": "07",
        "AUG": "08",
        "SEP": "09",
        "OCT": "10",
        "NOV": "11",
        "DEC": "12",
    }
    parts = date_str.split("/")
    day = parts[0]
    month = month_map[parts[1].upper()]
    year = (
        f"20{parts[2]}" if int(parts[2]) < 50 else f"19{parts[2]}"
    )  # Assume anos 2000 para YY < 50 e 1900 para YY >= 50
    return f"{day}/{month}/{year}"
