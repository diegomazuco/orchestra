from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from unittest.mock import patch, AsyncMock, MagicMock
import os
from io import StringIO

class AutomacaoDocumentosIpirangaCommandTest(TestCase):

    @patch('apps.automacao_ipiranga.management.commands.automacao_documentos_ipiranga.config')
    @patch('apps.automacao_ipiranga.management.commands.automacao_documentos_ipiranga.os.path.exists')
    @patch('apps.automacao_ipiranga.management.commands.automacao_documentos_ipiranga.async_playwright')
    def test_command_success_flow(self, mock_async_playwright, mock_exists, mock_config):
        # Mock config variables
        mock_config.side_effect = lambda key: {
            'PORTRAN_USER': 'test_user',
            'PORTRAN_PASSWORD': 'test_password',
        }[key]

        # Mock os.path.exists
        mock_exists.return_value = True

        # Mock Playwright objects
        mock_page = AsyncMock()
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        mock_playwright_context = MagicMock()
        mock_playwright_context.chromium.launch.return_value = mock_browser
        mock_async_playwright.return_value.__aenter__.return_value = mock_playwright_context

        # Mock page interactions
        mock_page.locator.return_value.inner_text.return_value = "ABC1234"
        mock_page.locator.return_value.text_content.return_value = "CERTIFICADO"
        mock_page.locator.return_value.is_visible.return_value = True
        mock_page.locator.return_value.count.return_value = 1 # Simulate one row/certificate

        # Simulate the find_and_process_placa logic
        mock_page.locator.return_value.nth.return_value.locator.return_value.inner_text.return_value = "ABC1234"
        mock_page.locator.return_value.nth.return_value.locator.return_value.is_visible.return_value = True

        # Simulate the certificate logic
        mock_page.locator.return_value.nth.return_value.locator.return_value.text_content.return_value = "CERTIFICADO"

        # Capture stdout for logging messages
        out = StringIO()
        
        call_command('automacao_documentos_ipiranga', 'ABC1234', 'CERTIFICADO', '/tmp/dummy_file.pdf', stdout=out)

        # Assertions for Playwright calls
        mock_async_playwright.assert_called_once()
        mock_playwright_context.chromium.launch.assert_called_once_with(headless=False)
        mock_browser.new_page.assert_called_once()
        mock_page.goto.assert_any_call('https://sites.redeipiranga.com.br/WAPortranNew/usuario/exibir', timeout=60000)
        mock_page.wait_for_selector.assert_any_call('#codigoUsuario', state='visible', timeout=60000)
        mock_page.fill.assert_any_call('#codigoUsuario', 'test_user')
        mock_page.fill.assert_any_call('#senha', 'test_password')
        mock_page.click.assert_any_call('input[type="submit"][value="Autenticar"]')
        mock_page.wait_for_url.assert_any_call('https://sites.redeipiranga.com.br/WAPortranNew/dashboard/index', timeout=60000)
        
        # Assertions for find_and_process_placa
        mock_page.goto.assert_any_call('https://sites.redeipiranga.com.br/WAPortranNew/veiculo/index?situacoesDocumentos=2&status=1,2,3,4,7', timeout=60000)
        mock_page.click.assert_any_call('a.btn.btn--square.alterar-veiculo-js')
        mock_page.wait_for_load_state.assert_any_call('networkidle', timeout=60000)

        # Assertions for certificate logic
        mock_page.click.assert_any_call('a#certificados-tab')
        mock_page.wait_for_load_state.assert_any_call('networkidle')
        mock_page.set_input_files.assert_called_once_with('input[type="file"]', '/tmp/dummy_file.pdf')
        mock_browser.close.assert_called_once()

        # Assertions for log messages (basic check)
        self.assertIn("Login realizado com sucesso!", out.getvalue())
        self.assertIn("Placa 'ABC1234' encontrada!", out.getvalue())
        self.assertIn("Certificado 'CERTIFICADO' (Vencido) encontrado.", out.getvalue())
        self.assertIn("Upload do arquivo concluído com sucesso.", out.getvalue())

    @patch('apps.automacao_ipiranga.management.commands.automacao_documentos_ipiranga.os.path.exists')
    def test_command_file_not_found(self, mock_exists):
        mock_exists.return_value = False
        with self.assertRaisesMessage(CommandError, 'O arquivo especificado não existe: /tmp/non_existent_file.pdf'):
            call_command('automacao_documentos_ipiranga', 'ABC1234', 'CERTIFICADO', '/tmp/non_existent_file.pdf')

    @patch('apps.automacao_ipiranga.management.commands.automacao_documentos_ipiranga.config')
    @patch('apps.automacao_ipiranga.management.commands.automacao_documentos_ipiranga.os.path.exists')
    def test_command_env_vars_not_set(self, mock_exists, mock_config):
        mock_exists.return_value = True
        mock_config.side_effect = lambda key: None # Simulate missing env vars
        with self.assertRaisesMessage(CommandError, 'As variáveis de ambiente PORTRAN_USER e PORTRAN_PASSWORD devem ser configuradas.'):
            call_command('automacao_documentos_ipiranga', 'ABC1234', 'CERTIFICADO', '/tmp/dummy_file.pdf')

    @patch('apps.automacao_ipiranga.management.commands.automacao_documentos_ipiranga.config')
    @patch('apps.automacao_ipiranga.management.commands.automacao_documentos_ipiranga.os.path.exists')
    @patch('apps.automacao_ipiranga.management.commands.automacao_documentos_ipiranga.async_playwright')
    def test_command_placa_not_found(self, mock_async_playwright, mock_exists, mock_config):
        mock_config.side_effect = lambda key: {
            'PORTRAN_USER': 'test_user',
            'PORTRAN_PASSWORD': 'test_password',
        }[key]
        mock_exists.return_value = True

        mock_page = AsyncMock()
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        mock_playwright_context = MagicMock()
        mock_playwright_context.chromium.launch.return_value = mock_browser
        mock_async_playwright.return_value.__aenter__.return_value = mock_playwright_context

        # Simulate no placa found
        mock_page.locator.return_value.count.return_value = 0 # No rows found

        with self.assertRaisesMessage(CommandError, "FALHA: Placa 'ABC1234' não encontrada em 'Vencidos', 'À vencer' ou 'Todos'."):
            call_command('automacao_documentos_ipiranga', 'ABC1234', 'CERTIFICADO', '/tmp/dummy_file.pdf')

    @patch('apps.automacao_ipiranga.management.commands.automacao_documentos_ipiranga.config')
    @patch('apps.automacao_ipiranga.management.commands.automacao_documentos_ipiranga.os.path.exists')
    @patch('apps.automacao_ipiranga.management.commands.automacao_documentos_ipiranga.async_playwright')
    def test_command_certificate_not_found(self, mock_async_playwright, mock_exists, mock_config):
        mock_config.side_effect = lambda key: {
            'PORTRAN_USER': 'test_user',
            'PORTRAN_PASSWORD': 'test_password',
        }[key]
        mock_exists.return_value = True

        mock_page = AsyncMock()
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        mock_playwright_context = MagicMock()
        mock_playwright_context.chromium.launch.return_value = mock_browser
        mock_async_playwright.return_value.__aenter__.return_value = mock_playwright_context

        # Simulate placa found, but no certificate
        mock_page.locator.return_value.count.side_effect = [1, 0] # One row for placa, zero for certificate
        mock_page.locator.return_value.nth.return_value.locator.return_value.inner_text.return_value = "ABC1234"
        mock_page.locator.return_value.nth.return_value.locator.return_value.is_visible.return_value = True

        with self.assertRaisesMessage(CommandError, "Certificado 'CERTIFICADO' (Vencido) não encontrado."):
            call_command('automacao_documentos_ipiranga', 'ABC1234', 'CERTIFICADO', '/tmp/dummy_file.pdf')

    @patch('apps.automacao_ipiranga.management.commands.automacao_documentos_ipiranga.config')
    @patch('apps.automacao_ipiranga.management.commands.automacao_documentos_ipiranga.os.path.exists')
    @patch('apps.automacao_ipiranga.management.commands.automacao_documentos_ipiranga.async_playwright')
    def test_command_timeout_error(self, mock_async_playwright, mock_exists, mock_config):
        mock_config.side_effect = lambda key: {
            'PORTRAN_USER': 'test_user',
            'PORTRAN_PASSWORD': 'test_password',
        }[key]
        mock_exists.return_value = True

        mock_page = AsyncMock()
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        mock_playwright_context = MagicMock()
        mock_playwright_context.chromium.launch.return_value = mock_browser
        mock_async_playwright.return_value.__aenter__.return_value = mock_playwright_context

        # Simulate TimeoutError during page.goto
        mock_page.goto.side_effect = TimeoutError("Navigation timeout")

        with self.assertRaisesMessage(CommandError, "Erro de Timeout na automação: Navigation timeout"):
            call_command('automacao_documentos_ipiranga', 'ABC1234', 'CERTIFICADO', '/tmp/dummy_file.pdf')

        mock_page.screenshot.assert_called_once_with(path='timeout_screenshot.png')

    @patch('apps.automacao_ipiranga.management.commands.automacao_documentos_ipiranga.config')
    @patch('apps.automacao_ipiranga.management.commands.automacao_documentos_ipiranga.os.path.exists')
    @patch('apps.automacao_ipiranga.management.commands.automacao_documentos_ipiranga.async_playwright')
    def test_command_unexpected_exception(self, mock_async_playwright, mock_exists, mock_config):
        mock_config.side_effect = lambda key: {
            'PORTRAN_USER': 'test_user',
            'PORTRAN_PASSWORD': 'test_password',
        }[key]
        mock_exists.return_value = True

        mock_page = AsyncMock()
        mock_browser = AsyncMock()
        mock_browser.new_page.return_value = mock_page
        mock_playwright_context = MagicMock()
        mock_playwright_context.chromium.launch.return_value = mock_browser
        mock_async_playwright.return_value.__aenter__.return_value = mock_playwright_context

        # Simulate a generic exception
        mock_page.goto.side_effect = Exception("Something went wrong")

        with self.assertRaisesMessage(CommandError, "Erro inesperado na automação: Something went wrong"):
            call_command('automacao_documentos_ipiranga', 'ABC1234', 'CERTIFICADO', '/tmp/dummy_file.pdf')

        mock_page.screenshot.assert_called_once_with(path='error_screenshot.png')