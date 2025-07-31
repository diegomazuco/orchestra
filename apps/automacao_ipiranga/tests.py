from django.test import TransactionTestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from unittest.mock import patch, AsyncMock, MagicMock
import os
from io import StringIO

from apps.automacao_ipiranga.models import CertificadoVeiculo, VeiculoIpiranga

class AutomacaoDocumentosIpirangaCommandTest(TransactionTestCase):

    def setUp(self):
        self.veiculo = VeiculoIpiranga.objects.create(placa='ABC1234', renavam='12345678901') # type: ignore
        self.certificado = CertificadoVeiculo.objects.create( # type: ignore
            veiculo=self.veiculo,
            nome='CERTIFICADO',
            arquivo='certificados_veiculos/dummy_file.pdf',
            status='pendente'
        )
        # Ensure the dummy file exists for the test
        os.makedirs(os.path.dirname(self.certificado.arquivo.path), exist_ok=True)
        with open(self.certificado.arquivo.path, 'w') as f:
            f.write("dummy content")

    def tearDown(self):
        if os.path.exists(self.certificado.arquivo.path):
            os.remove(self.certificado.arquivo.path)
        self.certificado.delete()
        self.veiculo.delete()

    @patch('apps.automacao_ipiranga.management.commands.automacao_documentos_ipiranga.CertificadoVeiculo.objects.get')
    @patch('apps.automacao_ipiranga.management.commands.automacao_documentos_ipiranga.extract_text_from_pdf_image')
    def test_command_success_flow(self, mock_extract_text_from_pdf_image, mock_get_certificado):
        # Mock extract_text_from_pdf_image
        mock_extract_text_from_pdf_image.return_value = "dummy pdf text"

        # Mock CertificadoVeiculo.objects.get
        mock_get_certificado.return_value = self.certificado
        
        # Mock the save method of the certificado instance
        self.certificado.save = AsyncMock()

        # Capture stdout for logging messages
        out = StringIO()
        
        call_command('automacao_documentos_ipiranga', str(self.certificado.id), stdout=out)

        # Assertions for Playwright calls
        self.mock_async_playwright_context.__aenter__.assert_called_once()
        self.mock_playwright_context.chromium.launch.assert_called_once_with(headless=True)
        self.mock_browser.new_page.assert_called_once()
        self.mock_login_to_portran.assert_called_once_with(self.mock_page, MagicMock()) # Check if login_to_portran was called

        # Assertions for find_and_process_placa
        self.mock_page.goto.assert_any_call('https://sites.redeipiranga.com.br/WAPortranNew/veiculo/index?situacoesDocumentos=2&status=1,2,3,4,7', timeout=60000)
        self.mock_locator_result.nth.return_value.locator.return_value.click.assert_any_call('a.btn.btn--square.alterar-veiculo-js')
        self.mock_page.wait_for_load_state.assert_any_call('networkidle', timeout=60000)

        # Assertions for certificate logic
        self.mock_locator_result.click.assert_any_call('a#certificados-tab')
        self.mock_page.wait_for_load_state.assert_any_call('networkidle')
        self.mock_locator_result.set_input_files.assert_called_once_with('input[type="file"]:visible', self.certificado.arquivo.path)
        self.mock_browser.close.assert_called_once()

        # Assertions for log messages (basic check)
        self.assertIn(f"--- INÍCIO DA AUTOMAÇÃO PARA O CERTIFICADO ID: {self.certificado.id} ---", out.getvalue())
        self.assertIn(f"SUCESSO: Placa '{self.veiculo.placa}' encontrada!", out.getvalue())
        self.assertIn(f"Certificado '{self.certificado.nome}' (Vencido) encontrado.", out.getvalue())
        self.assertIn(f"SUCESSO: Status do certificado ID {self.certificado.id} atualizado para 'enviado'.", out.getvalue())

        # Verify database status update
        self.certificado.save.assert_called()
        self.assertEqual(self.certificado.status, 'enviado')

    @patch('apps.automacao_ipiranga.management.commands.automacao_documentos_ipiranga.extract_text_from_pdf_image')
    def test_command_placa_not_found(self, mock_extract_text_from_pdf_image, mock_get_certificado):
        mock_extract_text_from_pdf_image.return_value = "dummy pdf text"

        # Mock CertificadoVeiculo.objects.get
        mock_get_certificado.return_value = self.certificado
        
        # Mock the save method of the certificado instance
        self.certificado.save = AsyncMock()

        # Simulate no placa found
        self.mock_locator_result.count.return_value = 0 # No rows found

        with self.assertRaisesMessage(CommandError, f"FALHA: Placa '{self.veiculo.placa}' não encontrada."): # type: ignore
            call_command('automacao_documentos_ipiranga', str(self.certificado.id))

        self.certificado.save.assert_called()
        self.assertEqual(self.certificado.status, 'falha')

    @patch('apps.automacao_ipiranga.management.commands.automacao_documentos_ipiranga.extract_text_from_pdf_image')
    def test_command_certificate_not_found(self, mock_extract_text_from_pdf_image, mock_get_certificado):
        mock_extract_text_from_pdf_image.return_value = "dummy pdf text"

        # Mock CertificadoVeiculo.objects.get
        mock_get_certificado.return_value = self.certificado
        
        # Mock the save method of the certificado instance
        self.certificado.save = AsyncMock()

        # Simulate placa found, but no certificate
        self.mock_locator_result.count.side_effect = [1, 0] # One row for placa, zero for certificate
        self.mock_nth_locator_result.inner_text.return_value = self.veiculo.placa
        self.mock_nth_locator_result.is_visible.return_value = True

        with self.assertRaisesMessage(CommandError, f"Certificado '{self.certificado.nome}' (Vencido) não encontrado."): # type: ignore
            call_command('automacao_documentos_ipiranga', str(self.certificado.id))

        self.certificado.save.assert_called()
        self.assertEqual(self.certificado.status, 'falha')

    @patch('apps.automacao_ipiranga.management.commands.automacao_documentos_ipiranga.extract_text_from_pdf_image')
    def test_command_timeout_error(self, mock_extract_text_from_pdf_image, mock_get_certificado):
        mock_extract_text_from_pdf_image.return_value = "dummy pdf text"

        # Mock CertificadoVeiculo.objects.get
        mock_get_certificado.return_value = self.certificado
        
        # Mock the save method of the certificado instance
        self.certificado.save = AsyncMock()

        # Simulate TimeoutError during page.goto
        self.mock_page.goto.side_effect = TimeoutError("Navigation timeout")

        with self.assertRaisesMessage(CommandError, f"Erro na automação para o certificado ID {self.certificado.id}: Navigation timeout"): # type: ignore
            call_command('automacao_documentos_ipiranga', str(self.certificado.id))

        self.certificado.save.assert_called()
        self.assertEqual(self.certificado.status, 'falha')
        self.mock_page.screenshot.assert_called_once_with(path=f'error_screenshot_cert_{self.certificado.id}.png')

    @patch('apps.automacao_ipiranga.management.commands.automacao_documentos_ipiranga.extract_text_from_pdf_image')
    def test_command_unexpected_exception(self, mock_extract_text_from_pdf_image, mock_get_certificado):
        mock_extract_text_from_pdf_image.return_value = "dummy pdf text"

        # Mock CertificadoVeiculo.objects.get
        mock_get_certificado.return_value = self.certificado
        
        # Mock the save method of the certificado instance
        self.certificado.save = AsyncMock()

        # Simulate a generic exception
        self.mock_page.goto.side_effect = Exception("Something went wrong")

        with self.assertRaisesMessage(CommandError, f"Erro na automação para o certificado ID {self.certificado.id}: Something went wrong"): # type: ignore
            call_command('automacao_documentos_ipiranga', str(self.certificado.id))

        self.certificado.save.assert_called()
        self.assertEqual(self.certificado.status, 'falha')
        self.mock_page.screenshot.assert_called_once_with(path=f'error_screenshot_cert_{self.certificado.id}.png')

    @patch('apps.automacao_ipiranga.management.commands.automacao_documentos_ipiranga.CertificadoVeiculo.objects.get')
    def test_command_certificado_not_found_in_db(self, mock_get_certificado):
        mock_get_certificado.side_effect = CertificadoVeiculo.DoesNotExist # type: ignore
        with self.assertRaisesMessage(CommandError, 'CertificadoVeiculo com ID "999" não encontrado.'): # type: ignore
            call_command('automacao_documentos_ipiranga', '999')