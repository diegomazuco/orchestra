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
from scipy.ndimage import interpolation, rotate  # type: ignore
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
                "https://sites2.ipiranga.com.br/WAPortranNew/dashboard/index",
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
                    "https://sites2.ipiranga.com.br/WAPortranNew/dashboard/index",
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
            logger.debug("OCR: Iniciando get_pixmap.")
            pix = page.get_pixmap(matrix=fitz.Matrix(600 / 72, 600 / 72))
            logger.debug("OCR: get_pixmap concluído.")
            img = Image.open(io.BytesIO(pix.tobytes()))
            logger.info(f"OCR: Imagem da página {page_num + 1} carregada.")

            # Convert PIL Image to NumPy array for scikit-image processing
            logger.debug("OCR: Convertendo imagem para array NumPy.")
            img_np = np.array(img)
            logger.debug(
                "OCR: Imagem convertida para array NumPy. Shape: %s, Dtype: %s",
                img_np.shape,
                img_np.dtype,
            )

            # Convert to grayscale if not already
            if img_np.ndim == 3:
                logger.debug("OCR: Convertendo imagem para escala de cinza.")
                img_np = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
                logger.debug(
                    "OCR: Imagem convertida para escala de cinza. Shape: %s, Dtype: %s",
                    img_np.shape,
                    img_np.dtype,
                )

            # Apply skew correction
            logger.debug("OCR: Verificando e corrigindo inclinação da imagem.")
            angle = determine_skew(img_np, logger)
            if angle != 0:
                img_np = rotate(img_np, angle, reshape=False, mode="constant", cval=255)
                logger.info(
                    f"OCR: Imagem rotacionada em {angle:.2f} graus para correção de inclinação. Shape: %s, Dtype: %s",
                    img_np.shape,
                    img_np.dtype,
                )
            else:
                logger.info("OCR: Nenhuma inclinação significativa detectada.")

            # Noise Reduction (Median Filter)
            logger.debug("OCR: Iniciando redução de ruído.")
            img_np = filters.median(img_np, behavior="ndimage")
            logger.debug(
                "OCR: Ruído da imagem reduzido. Shape: %s, Dtype: %s",
                img_np.shape,
                img_np.dtype,
            )

            # Contrast Enhancement (Adaptive Equalization)
            logger.debug("OCR: Iniciando aprimoramento de contraste.")
            img_np = exposure.equalize_adapthist(img_np, clip_limit=0.03)
            img_np = (img_np * 255).astype(np.uint8)  # Convert back to uint8
            logger.debug(
                "OCR: Contraste da imagem aprimorado. Shape: %s, Dtype: %s",
                img_np.shape,
                img_np.dtype,
            )

            # Binarization (Otsu's method for adaptive thresholding)
            logger.debug("OCR: Iniciando binarização.")
            if img_np is None:
                raise ValueError("img_np should not be None at this point.")
            thresh = filters.threshold_otsu(img_np)  # type: ignore
            img_np = (img_np > thresh).astype(np.uint8) * 255
            logger.debug(
                "OCR: Imagem binarizada. Shape: %s, Dtype: %s",
                img_np.shape,
                img_np.dtype,
            )

            # Convert back to PIL Image for Tesseract
            logger.debug("OCR: Preparando imagem para Tesseract.")
            img = Image.fromarray(img_np)
            logger.debug(
                "OCR: Imagem preparada para Tesseract. Mode: %s, Size: %s",
                img.mode,
                img.size,
            )

            logger.debug("OCR: Iniciando extração de texto com Tesseract.")
            page_text = pytesseract.image_to_string(
                img, lang="por", config=tesseract_config
            )
            logger.debug("OCR: Extração de texto com Tesseract concluída.")
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


def determine_skew(image, logger: logging.Logger):
    """Determina o ângulo de inclinação de uma imagem."""
    logger.debug("OCR: determine_skew - Iniciando.")
    # Convert to binary
    thresh = filters.threshold_otsu(image)
    binary = (image > thresh).astype(float)
    logger.debug("OCR: determine_skew - Imagem binarizada.")

    # Find the skew angle
    h, w = binary.shape

    # Find the angle of the maximum projection
    angles = np.arange(-5, 5, 0.1)
    scores = []
    for angle in angles:
        rotated = rotate(binary, angle, reshape=False)
        scores.append(np.sum(rotated.astype(np.float64), axis=1).max())
    best_angle = angles[np.argmax(scores)]
    logger.debug(
        f"OCR: determine_skew - Melhor ângulo encontrado: {best_angle:.2f} graus."
    )
    return best_angle


def extract_cipp_data(pdf_text: str, logger: logging.Logger) -> tuple[str, str]:
    """Extrai dados específicos (número do documento e vencimento) de um certificado CIPP."""
    logger.info("Iniciando extração de dados específicos para certificado CIPP...")

    # Normalize the text to make regex more robust against OCR noise
    normalized_pdf_text = normalize_text(pdf_text)

    # Use a more flexible regex for "CERTIFICADO DE INSPEÇÃO"
    # Allowing for common OCR errors like 'C' instead of 'Ç', 'A' instead of 'Ã', 'O' instead of 'Õ'
    # Use a more flexible regex for "CERTIFICADO DE INSPEÇÃO"
    # Allowing for common OCR errors and variations in spacing/characters
    match = re.search(
        r"(CERTIFICADO\s*(DE|D|E)?\s*INSPE[CÇ][AÃ]O.*?)(?=(CERTIFICADO\s*(DE|D|E)?\s*INSPE[CÇ][AÃ]O|$))",
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
