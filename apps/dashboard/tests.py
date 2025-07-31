from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import CommandError
import os

class DashboardViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_orchestra_view(self):
        response = self.client.get(reverse('orchestra')) # Corrected URL name
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'dashboard/orchestra.html')

    @patch('django.core.management.call_command')
    @patch('apps.dashboard.views.default_storage.save')
    @patch('os.makedirs')
    def test_process_documents_view_success(self, mock_makedirs, mock_save, mock_call_command):
        mock_save.return_value = 'temp_uploads/TEST_FILE.pdf'
        
        # Create a dummy file for testing
        dummy_file = SimpleUploadedFile("ABC1234_CERTIFICADO.pdf", b"file_content", content_type="application/pdf")
        
        with self.settings(MEDIA_ROOT='/tmp/media/'): # Use a temporary MEDIA_ROOT for testing
            response = self.client.post(reverse('process_documents'), {'documents': [dummy_file]})

            self.assertEqual(response.status_code, 200) # type: ignore
            self.assertIn(b'Processamento de arquivos iniciado.', response.content) # type: ignore
            mock_makedirs.assert_called_once_with(os.path.join('/tmp/media/', 'temp_uploads'), exist_ok=True)
            mock_save.assert_called_once()
            mock_call_command.assert_called_once_with('automacao_documentos_ipiranga', 'ABC1234', 'CERTIFICADO', os.path.join('/tmp/media/', 'temp_uploads/TEST_FILE.pdf'))

    def test_process_documents_view_no_files(self):
        response = self.client.post(reverse('process_documents'), {})
        self.assertEqual(response.status_code, 400) # type: ignore
        self.assertIn(b'Nenhum arquivo enviado.', response.content) # type: ignore

    def test_process_documents_view_invalid_method(self):
        response = self.client.get(reverse('process_documents'))
        self.assertEqual(response.status_code, 405) # type: ignore

    @patch('django.core.management.call_command')
    @patch('apps.dashboard.views.default_storage.save')
    def test_process_documents_view_command_error(self, mock_save, mock_call_command):
        mock_save.return_value = 'temp_uploads/TEST_FILE.pdf'
        mock_call_command.side_effect = CommandError("Erro simulado")

        dummy_file = SimpleUploadedFile("ABC1234_CERTIFICADO.pdf", b"file_content", content_type="application/pdf")

        with self.settings(MEDIA_ROOT='/tmp/media/'):
            response = self.client.post(reverse('process_documents'), {'documents': [dummy_file]})

            self.assertEqual(response.status_code, 200) # Still 200, but status in details will show error # type: ignore
            self.assertIn(b'Erro na automa\xc3\xa7\xc3\xa3o: Erro simulado', response.content) # type: ignore

    @patch('django.core.management.call_command')
    @patch('apps.dashboard.views.default_storage.save')
    def test_process_documents_view_unexpected_error(self, mock_save, mock_call_command):
        mock_save.return_value = 'temp_uploads/TEST_FILE.pdf'
        mock_call_command.side_effect = Exception("Erro inesperado")

        dummy_file = SimpleUploadedFile("ABC1234_CERTIFICADO.pdf", b"file_content", content_type="application/pdf")

        with self.settings(MEDIA_ROOT='/tmp/media/'):
            response = self.client.post(reverse('process_documents'), {'documents': [dummy_file]})

            self.assertEqual(response.status_code, 200) # type: ignore
            self.assertIn(b'Erro inesperado: Erro inesperado', response.content) # type: ignore

    def test_process_documents_view_malformed_filename(self):
        dummy_file = SimpleUploadedFile("MALFORMED_FILE.pdf", b"file_content", content_type="application/pdf")
        response = self.client.post(reverse('process_documents'), {'documents': [dummy_file]})
        self.assertEqual(response.status_code, 400) # type: ignore
        self.assertIn(b'Nome de arquivo fora do padr\xc3\xa3o esperado (PLACA_NOME_CERTIFICADO.pdf).', response.content) # type: ignore