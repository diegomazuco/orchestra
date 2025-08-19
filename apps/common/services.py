import asyncio
import io
import logging
import re

import fitz  # type: ignore # PyMuPDF
import numpy as np
import pytesseract  # type: ignore
from decouple import config
from django.conf import settings  # Added import
from PIL import Image
from playwright.async_api import Page, expect
from pytesseract import Output  # Moved to top
from skimage.transform import rotate
from skimage.filters import unsharp_mask
from scipy.ndimage import gaussian_filter


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


def extract_text_from_pdf_image(
    pdf_path: str, logger: logging.Logger, tesseract_config: str = ""
) -> str:
    """Extrai texto de imagens dentro de um arquivo PDF usando PyMuPDF e Tesseract OCR."""
    text = ""
    # Always use PSM 11 for better recognition of sparse text
    tesseract_config = "--psm 11"

    doc: fitz.Document | None = None
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page: fitz.Page = doc.load_page(page_num)

            numero_documento_roi = settings.OCR_NUMERO_DOCUMENTO_ROI # Used setting
            data_vencimento_roi = settings.OCR_DATA_VENCIMENTO_ROI # Used setting

            # Extract text from each ROI
            numero_documento_text: str = extract_text_from_roi(
                page, numero_documento_roi, logger, tesseract_config, page_num
            )
            data_vencimento_text: str = extract_text_from_roi(
                page, data_vencimento_roi, logger, tesseract_config, page_num
            )

            text += f"Numero Documento: {numero_documento_text}\nData Vencimento: {data_vencimento_text}"

    except Exception as e:
        logger.error(f"Erro ao extrair texto de imagem do PDF {pdf_path}: {e}")
        raise
    finally:
        if doc:
            doc.close()
    return text


def extract_text_from_roi(
    page: fitz.Page,
    roi: tuple[int, int, int, int],
    logger: logging.Logger,
    tesseract_config: str,
    page_num: int, # Added page_num
) -> str:
    """Extracts text from a specific region of interest on a page."""
    try:
        logger.debug(f"OCR: Extraindo texto do ROI: {roi}")
        pix: fitz.Pixmap = page.get_pixmap(
            matrix=fitz.Matrix(1200 / 72, 1200 / 72), clip=roi
        )
        img: Image.Image = Image.open(io.BytesIO(pix.tobytes()))  # type: ignore[reportUnknownArgumentType]
        logger.info("OCR: Imagem do ROI carregada.")

        # Convert to grayscale using Pillow
        logger.debug("OCR: Convertendo imagem para escala de cinza com Pillow.")
        img = img.convert("L")

        # Convert PIL Image to NumPy array for scikit-image/scipy processing
        img_np: np.ndarray = np.array(img)

        # Deskewing (Skew Correction) using Hough Transform
        try:
            from skimage.transform import hough_line, hough_line_peaks
            from skimage.feature import canny
            from skimage.filters import threshold_otsu

            # Convert to binary image
            thresh = threshold_otsu(img_np)
            binary = img_np > thresh

            # Edge detection
            edges = canny(binary, sigma=1.0)

            # Hough Transform
            h, theta, d = hough_line(edges)

            # Find the strongest lines
            _, angles, _ = hough_line_peaks(h, theta, d)

            # Calculate the average angle, convert to degrees
            if angles.size > 0:
                angle = np.rad2deg(np.mean(angles)) - 90 # Adjust for vertical lines
                if abs(angle) > 0.1: # Only rotate if angle is significant
                    logger.info(f"OCR: Deskewing - Rotating by {angle:.2f} degrees using Hough Transform.")
                    img_np = (rotate(img_np, angle, resize=False, mode='edge') * 255).astype(np.uint8)
                    img = Image.fromarray(img_np)
            else:
                logger.info("OCR: Deskewing - No strong lines found for Hough Transform.")
        except Exception as e:
            logger.warning(f"OCR: Deskewing failed (Hough Transform): {e}")

        # Noise Reduction (Gaussian Blur)
        logger.debug("OCR: Aplicando redução de ruído (Gaussian Blur).")
        img_np = gaussian_filter(img_np, sigma=1.0) # sigma value can be tuned
        img = Image.fromarray(img_np)

        # Contrast Enhancement (Unsharp Mask)
        logger.debug("OCR: Aplicando realce de contraste (Unsharp Mask).")
        img_np = (unsharp_mask(img_np, radius=1.0, amount=1.0) * 255).astype(np.uint8)
        img = Image.fromarray(img_np)

        # Binarization using Otsu's method
        logger.debug("OCR: Iniciando binarização com método de Otsu.")
        thresh = threshold_otsu(img_np) # Use Otsu's method to find optimal threshold
        img_np = (img_np > thresh).astype(np.uint8) * 255 # Apply threshold and convert to 0 or 255
        img = Image.fromarray(img_np)

        # Save screenshot of the processed image before OCR
        screenshot_path = f"logs/ocr_processed_image_{page_num}.png"
        img.save(screenshot_path)
        logger.info(f"OCR: Processed image saved to {screenshot_path}")

        logger.debug("OCR: Iniciando extração de texto com Tesseract.")

        page_text: str = pytesseract.image_to_string(
            img, lang="por", config=tesseract_config, output_type=Output.STRING
        )  # type: ignore[reportAssignmentType]
        logger.debug("OCR: Extração de texto com Tesseract concluída.")
        return page_text.strip()
    except Exception as e:
        logger.error(f"Erro ao extrair texto do ROI {roi}: {e}")
        raise


def extract_cipp_data(pdf_text: str, logger: logging.Logger) -> tuple[str, str]:
    """Extrai dados específicos (número do documento e vencimento) de um certificado CIPP."""
    logger.info("Iniciando extração de dados específicos para certificado CIPP...")

    normalized_pdf_text: str = normalize_text(pdf_text)
    logger.info(
        f"OCR: Normalized PDF text (first 500 chars): {normalized_pdf_text[:500]}..."
    )

    # Search for "Número do Certificado" block
    match_certificado_block: re.Match[str] | None = re.search(
        r"(Número do Certificado:.*?)(?=DATA DE VENCIMENTO|$)",
        normalized_pdf_text,
        re.IGNORECASE | re.DOTALL,
    )

    if not match_certificado_block:
        logger.warning(
            "Não foi possível encontrar o bloco 'Número do Certificado' no PDF CIPP."
        )
        raise ValueError("Bloco 'Número do Certificado' não encontrado.")

    certificado_block: str = match_certificado_block.group(1)
    logger.info(f"Bloco 'Número do Certificado' encontrado: {certificado_block[:500]}...")

    # Extract "Número do Certificado" value
    match_numero: re.Match[str] | None = re.search(
        r"Número do Certificado:\s*([A-Z0-9]+)", certificado_block, re.IGNORECASE
    )
    if match_numero:
        extracted_raw_numero: str = match_numero.group(1)
        logger.info(f"OCR: Extracted raw numero do certificado: {extracted_raw_numero}")
        # Filter out non-numeric characters for the portal field
        numero_documento_valor: str = re.sub(r"[^0-9]", "", extracted_raw_numero)
        logger.info(f"OCR: Final numero_documento_valor (apenas números): {numero_documento_valor}")
    else:
        logger.warning("Número do Certificado não encontrado.")
        raise ValueError("Número do Certificado não encontrado.")

    # Extract "DATA DE VENCIMENTO"
    match_data_vencimento: re.Match[str] | None = re.search(
        r"DATA DE VENCIMENTO:\s*(\d{1,2}/\s*[A-Z]{3}/\s*\d{2,4})",
        normalized_pdf_text,
        re.IGNORECASE,
    )
    if match_data_vencimento:
        vencimento_valor_pdf_raw: str = match_data_vencimento.group(1)
        logger.info(f"Data de vencimento bruta extraída: {vencimento_valor_pdf_raw}")
        vencimento_valor_portal: str = convert_date_format(vencimento_valor_pdf_raw, logger)
        logger.info(f"Data de vencimento formatada para portal: {vencimento_valor_portal}")
    else:
        logger.warning("Data de vencimento não encontrada.")
        raise ValueError("Data de vencimento não encontrada.")

    return numero_documento_valor, vencimento_valor_portal


def normalize_text(text: str) -> str:
    """Normaliza o texto removendo caracteres que não são alfanuméricos, espaços ou barras (/), e espaços extras."""
    # Permite letras, números, espaços e barras (para datas)
    normalized_text: str = re.sub(r"[^a-zA-Z0-9\s/]", "", text)
    normalized_text = re.sub(r"\s+", " ", normalized_text).strip()
    return normalized_text


def convert_date_format(date_str: str, logger: logging.Logger) -> str:
    """Converte uma string de data do formato 'DD/MON/YY' para 'DD/MM/YYYY'."""
    month_map: dict[str, str] = {
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
        day: str
        month_abbr: str
        year: str
        day, month_abbr, year = date_str.upper().split("/")
        day_cleaned: str = (
            day.replace("O", "0").replace("I", "1").replace("S", "5").replace("Z", "2")
        )
        month: str = month_map.get(month_abbr, "00")
        year_full: str = f"20{year}" if len(year) == 2 else year
        return f"{day_cleaned}/{month}/{year_full}"
    except Exception as e:
        logger.error(f"Erro ao converter data '{date_str}': {e}")
        raise ValueError(f"Erro ao converter data '{date_str}': {e}") from e
