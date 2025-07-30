import logging
from decouple import config
from playwright.async_api import Page, expect

async def login_to_portran(page: Page, logger: logging.Logger):
    """
    Realiza o login no portal Portran/Ipiranga de forma centralizada e robusta.

    Args:
        page: A instância da página do Playwright.
        logger: A instância do logger para registrar os passos.
    """
    logger.info("--- Iniciando etapa de login centralizada ---")
    
    portran_user = config('PORTRAN_USER')
    portran_password = config('PORTRAN_PASSWORD')

    if not portran_user or not portran_password:
        logger.error("As variáveis de ambiente PORTRAN_USER e PORTRAN_PASSWORD devem ser configuradas.")
        raise ValueError("Credenciais não encontradas no .env")

    try:
        logger.info("Navegando para a página de login...")
        await page.goto('https://sites.redeipiranga.com.br/WAPortranNew/usuario/exibir', timeout=60000)
        
        logger.info("Aguardando seletor de usuário.")
        user_selector = page.locator('#codigoUsuario')
        await user_selector.wait_for(state='visible', timeout=60000)
        
        logger.info("Preenchendo usuário...")
        await user_selector.fill(str(portran_user))
        
        logger.info("Preenchendo senha...")
        await page.locator('#senha').fill(str(portran_password))
        
        logger.info("Clicando em 'Autenticar'...")
        await page.locator('input[type="submit"][value="Autenticar"]').click()
        
        logger.info("Aguardando redirecionamento para o dashboard...")
        await expect(page).to_have_url('https://sites.redeipiranga.com.br/WAPortranNew/dashboard/index', timeout=60000)
        
        logger.info("Login realizado com sucesso!")
        logger.info("--- Fim da etapa de login ---")

    except Exception as e:
        logger.error(f"Falha na etapa de login: {e}")
        await page.screenshot(path='login_error_screenshot.png')
        logger.error("Screenshot de erro de login capturado em 'login_error_screenshot.png'.")
        raise  # Re-levanta a exceção para que o comando que chamou saiba que falhou
