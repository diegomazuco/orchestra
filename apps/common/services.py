import asyncio
import io
import logging
import re

import cv2
import fitz  # PyMuPDF # type: ignore
import numpy as np
import pytesseract  # type: ignore
from decouple import config
from PIL import Image
from playwright.async_api import Page, expect
from scipy.ndimage import interpolation as ndi
from skimage import exposure, filters


async def login_to_portran(page: Page, logger: logging.Logger):
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


def extract_text_from_pdf_image(
    pdf_path: str, logger: logging.Logger, tesseract_config: str = ""
) -> str:
    """Extrai texto de imagens dentro de um arquivo PDF usando PyMuPDF e Tesseract OCR."""
    text = ""
    if not tesseract_config:
        tesseract_config = "--psm 3"  # Changed to PSM 3 (Automatic page segmentation)

    doc = None
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            # Increased DPI for potentially better OCR accuracy
            pix = page.get_pixmap(matrix=fitz.Matrix(600 / 72, 600 / 72))
            img = Image.open(io.BytesIO(pix.tobytes()))
            logger.info(f"OCR: Imagem da página {page_num + 1} carregada.")

            # Convert PIL Image to NumPy array for scikit-image processing
            img_np = np.array(img)
            logger.info("OCR: Imagem convertida para array NumPy.")

            # Convert to grayscale if not already
            if img_np.ndim == 3:
                img_np = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
                logger.info("OCR: Imagem convertida para escala de cinza.")

            # Deskewing (requires scikit-image)
            angle = determine_skew(img_np)
            if angle is not None:
                img_np = ndi.rotate(img_np, angle, reshape=False)
                logger.info(
                    f"OCR: Imagem corrigida para inclinação (ângulo: {angle:.2f} graus)."
                )
            else:
                logger.info("OCR: Nenhuma inclinação detectada ou corrigida.")

            # Noise Reduction (Median Filter)
            img_np = filters.median(img_np, behavior="ndimage")
            logger.info("OCR: Ruído da imagem reduzido.")

            # Contrast Enhancement (Adaptive Equalization)
            img_np = exposure.equalize_adapthist(img_np, clip_limit=0.03)
            img_np = (img_np * 255).astype(np.uint8)  # Convert back to uint8
            logger.info("OCR: Contraste da imagem aprimorado.")

            # Binarization (Otsu's method for adaptive thresholding)
            thresh = filters.threshold_otsu(img_np)
            img_np = (img_np > thresh).astype(np.uint8) * 255
            logger.info("OCR: Imagem binarizada.")

            # Convert back to PIL Image for Tesseract
            img = Image.fromarray(img_np)
            logger.info("OCR: Imagem preparada para Tesseract.")

            page_text = pytesseract.image_to_string(
                img, lang="por", config=tesseract_config
            )
            text += page_text
            logger.info(
                f"OCR: Texto extraído da página {page_num + 1}:\n{page_text[:500]}..."
            )

    except Exception as e:
        logger.error(f"Erro ao extrair texto de imagem do PDF {pdf_path}: {e}")
        raise
    finally:
        if doc:
            doc.close()
    return text


def determine_skew(image):
    """Determina o ângulo de inclinação de uma imagem."""
    # Convert to binary
    thresh = filters.threshold_otsu(image)
    binary = (image > thresh).astype(float)

    # Find the skew angle
    h, w = binary.shape

    # Find the angle of the maximum projection
    angles = np.arange(-5, 5, 0.1)
    scores = []
    for angle in angles:
        rotated = ndi.rotate(binary, angle, reshape=False)
        scores.append(np.sum(rotated.astype(np.float64), axis=1).max())
    best_angle = angles[np.argmax(scores)]
    return best_angle


def extract_cipp_data(pdf_text: str, logger: logging.Logger) -> tuple[str, str]:
    """Extrai dados específicos (número do documento e vencimento) de um certificado CIPP."""
    logger.info("Iniciando extração de dados específicos para certificado CIPP...")

    # Normalize the text to make regex more robust against OCR noise
    normalized_pdf_text = normalize_text(pdf_text)

    # Use a more flexible regex for "CERTIFICADO DE INSPEÇÃO"
    # Allowing for common OCR errors like 'C' instead of 'Ç', 'A' instead of 'Ã', 'O' instead of 'Õ'
    match = re.search(
        r"(CERTIFICADO DE INSPE[CÇ][AÃ]O.*?)(?=(CERTIFICADO DE INSPE[CÇ][AÃ]O|$))",
        normalized_pdf_text,
        re.IGNORECASE | re.DOTALL,
    )

    if not match:
        logger.warning(
            "Não foi possível encontrar um bloco de 'CERTIFICADO DE INSPEÇÃO' no PDF CIPP."
        )
        raise ValueError("Bloco de certificado CIPP não encontrado.")

    first_block = match.group(1)
    logger.info(f"Bloco de certificado CIPP encontrado: {first_block[:500]}...")

    match_numero = re.search(
        r"CIPP.*?([A-Z]?\d{6,})", first_block, re.IGNORECASE | re.DOTALL
    )
    numero_documento_valor = (
        re.sub(r"\D", "", match_numero.group(1)) if match_numero else None
    )
    if numero_documento_valor is None:
        raise ValueError("Número do documento CIPP não encontrado.")
    logger.info(f"Número do documento CIPP extraído: {numero_documento_valor}")

    all_dates = re.findall(
        r"(\d{1,2}|[OISZ]{1,2})\s*/\s*([A-Z]{3})\s*/\s*(\d{2,4})",
        first_block,
        re.IGNORECASE,
    )
    vencimento_valor_pdf = "/".join(all_dates[-1]) if all_dates else None
    if vencimento_valor_pdf is None:
        raise ValueError("Data de vencimento CIPP não encontrada.")
    logger.info(f"Data de vencimento CIPP extraída: {vencimento_valor_pdf}")

    return numero_documento_valor, vencimento_valor_pdf


def normalize_text(text: str) -> str:
    """Normaliza o texto removendo caracteres não alfanuméricos e espaços extras."""
    normalized_text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
    normalized_text = re.sub(r"\s+", " ", normalized_text).strip()
    return normalized_text


def convert_date_format(date_str: str, logger: logging.Logger) -> str:
    """Converte uma string de data do formato 'DD/MON/YY' para 'DD/MM/YYYY'."""
    month_map = {
        "JAN": "01",
        "FEV": "02",
        "MAR": "03",
        "ABR": "04",
        "MAI": "05",
        "JUN": "06",
        "JUL": "07",
        "AGO": "08",
        "SET": "09",
        "OUT": "10",
        "NOV": "11",
        "DEZ": "12",
        # Common OCR errors
        "FES": "02",
    }
    try:
        day, month_abbr, year = date_str.upper().split("/")
        day_cleaned = (
            day.replace("O", "0").replace("I", "1").replace("S", "5").replace("Z", "2")
        )
        month = month_map.get(month_abbr, "00")
        year_full = f"20{year}" if len(year) == 2 else year
        return f"{day_cleaned}/{month}/{year_full}"
    except Exception as e:
        logger.error(f"Erro ao converter data '{date_str}': {e}")
        raise ValueError(f"Erro ao converter data '{date_str}': {e}") from e
