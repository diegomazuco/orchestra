import asyncio
import io
import logging
import re

import fitz  # type: ignore # PyMuPDF
import numpy as np
import pytesseract  # type: ignore
from decouple import config
from PIL import Image
from playwright.async_api import Page, expect


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
        tesseract_config = "--psm 6"  # Assume a single uniform block of text.

    doc: fitz.Document | None = None
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page: fitz.Page = doc.load_page(page_num)

            numero_documento_roi = (100, 500, 400, 600)  # Example coordinates
            data_vencimento_roi = (400, 500, 700, 600)  # Example coordinates

            # Extract text from each ROI
            numero_documento_text: str = extract_text_from_roi(
                page, numero_documento_roi, logger, tesseract_config
            )
            data_vencimento_text: str = extract_text_from_roi(
                page, data_vencimento_roi, logger, tesseract_config
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
) -> str:
    """Extracts text from a specific region of interest on a page."""
    try:
        logger.debug(f"OCR: Extraindo texto do ROI: {roi}")
        pix: fitz.Pixmap = page.get_pixmap(
            matrix=fitz.Matrix(600 / 72, 600 / 72), clip=roi
        )
        img: Image.Image = Image.open(io.BytesIO(pix.tobytes()))  # type: ignore[reportUnknownArgumentType]
        logger.info("OCR: Imagem do ROI carregada.")

        # Convert to grayscale using Pillow
        logger.debug("OCR: Convertendo imagem para escala de cinza com Pillow.")
        img = img.convert("L")

        # Binarization using NumPy
        logger.debug("OCR: Iniciando binarização com NumPy.")

        img_np: np.ndarray = np.array(img)
        img_np = np.where(img_np < 128, 0, 255).astype(np.uint8)
        img = Image.fromarray(img_np)

        logger.debug("OCR: Iniciando extração de texto com Tesseract.")
        from pytesseract import Output

        # ... (rest of the file)

        page_text: str = pytesseract.image_to_string(
            img, lang="por", config=tesseract_config, output_type=Output.STRING
        )  # type: ignore[reportAssignmentType]
        logger.debug("OCR: Extração de texto com Tesseract concluída.")
        return page_text.strip()
    except Exception as e:
        logger.error(f"Erro ao extrair texto do ROI {roi}: {e}")
        return ""


def extract_cipp_data(pdf_text: str, logger: logging.Logger) -> tuple[str, str]:
    """Extrai dados específicos (número do documento e vencimento) de um certificado CIPP."""
    logger.info("Iniciando extração de dados específicos para certificado CIPP...")

    # Normalize the text to make regex more robust against OCR noise
    normalized_pdf_text: str = normalize_text(pdf_text)
    logger.info(
        f"OCR: Normalized PDF text (first 500 chars): {normalized_pdf_text[:500]}..."
    )

    # Use a more flexible regex for "CERTIFICADO DE INSPEÇÃO"
    # Allowing for common OCR errors like 'C' instead of 'Ç', 'A' instead of 'Ã', 'O' instead of 'Õ'
    # Use a more flexible regex for "CERTIFICADO DE INSPEÇÃO"
    # Allowing for common OCR errors and variations in spacing/characters
    match: re.Match[str] | None = re.search(
        r"(CERTIFICADO\s*(DE|D|E)?\s*INSPE[CÇ][AÃ]O.*?)(?=(CERTIFICADO\s*(DE|D|E)?\s*INSPE[CÇ][AÃ]O|$))",
        normalized_pdf_text,
        re.IGNORECASE | re.DOTALL,
    )

    if not match:
        logger.warning(
            "Não foi possível encontrar um bloco de 'CERTIFICADO DE INSPEÇÃO' no PDF CIPP."
        )
        raise ValueError("Bloco de certificado CIPP não encontrado.")

    first_block: str = match.group(1)
    logger.info(f"Bloco de certificado CIPP encontrado: {first_block[:500]}...")

    match_numero: re.Match[str] | None = re.search(
        r"SP\s*([A-Z][0-9T]{6})", first_block, re.IGNORECASE | re.DOTALL
    )
    if match_numero:
        extracted_raw: str = match_numero.group(1)
        logger.info(f"OCR: Extracted raw numero: {extracted_raw}")
        # Apply a more targeted cleaning for the document number
        # Replace common OCR misreads for digits, specifically 'T' for '6' or '7'
        cleaned_num: str = extracted_raw.replace("T", "6")  # Prioritize 'T' as '6'
        cleaned_num = (
            cleaned_num.replace("I", "1")
            .replace("O", "0")
            .replace("S", "5")
            .replace("Z", "2")
        )
        cleaned_num = re.sub(
            r"[^A-Z0-9]", "", cleaned_num
        ).upper()  # Remove non-alphanumeric
        numero_documento_valor: str = cleaned_num
        logger.info(f"OCR: Final numero_documento_valor: {numero_documento_valor}")
    else:
        logger.warning("Número do documento CIPP não encontrado.")
        raise ValueError("Número do documento CIPP não encontrado.")

    all_dates: list[tuple[str, str, str]] = re.findall(
        r"(\d{1,2}|[OISZ]{1,2})\s*/\s*([A-Z]{3})\s*/\s*(\d{2,4})",
        first_block,
        re.IGNORECASE,
    )
    vencimento_valor_pdf: str | None = "/".join(all_dates[-1]) if all_dates else None
    if vencimento_valor_pdf is None:
        raise ValueError("Data de vencimento CIPP não encontrada.")
    logger.info(f"Data de vencimento CIPP extraída: {vencimento_valor_pdf}")

    return numero_documento_valor, vencimento_valor_pdf


def normalize_text(text: str) -> str:
    """Normaliza o texto removendo caracteres que não são alfanuméricos, espaços ou barras (/), e espaços extras."""
    # Permite letras, números, espaços e barras (para datas)
    normalized_text: str = re.sub(r"[^a-zA-Z0-9\s/ R]", "", text)
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
