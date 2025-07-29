from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from apps.automacao_documentos.models import LicencaAmbiental, Portal, Automacao, LogExecucaoAutomacao
from datetime import datetime

class LicencaAmbientalModelTest(TestCase):
    def test_create_licenca_ambiental(self):
        # Create a dummy file for testing FileField
        dummy_file = SimpleUploadedFile("test_licenca.pdf", b"file_content", content_type="application/pdf")
        licenca = LicencaAmbiental.objects.create(
            numero="LIC-2023-001",
            descricao="Licença de teste",
            arquivo=dummy_file,
            status='pendente'
        )
        self.assertEqual(licenca.numero, "LIC-2023-001")
        self.assertEqual(licenca.status, 'pendente')
        self.assertIsNotNone(licenca.data_criacao)
        self.assertIsNotNone(licenca.data_atualizacao)
        self.assertTrue(licenca.arquivo.name.startswith('licencas/'))
        self.assertTrue(licenca.arquivo.name.endswith('.pdf'))
        self.assertEqual(licenca.arquivo.read(), b"file_content")

    def test_licenca_ambiental_str(self):
        licenca = LicencaAmbiental.objects.create(numero="LIC-STR-001")
        self.assertEqual(str(licenca), "LIC-STR-001")

class PortalModelTest(TestCase):
    def test_create_portal(self):
        portal = Portal.objects.create(
            nome="Portal Teste",
            url_base="http://www.portalteste.com",
            usuario="user_teste",
            senha="password_teste"
        )
        self.assertEqual(portal.nome, "Portal Teste")
        self.assertEqual(portal.url_base, "http://www.portalteste.com")
        self.assertEqual(portal.usuario, "user_teste")
        self.assertEqual(portal.senha, "password_teste")

    def test_portal_str(self):
        portal = Portal.objects.create(nome="Portal STR")
        self.assertEqual(str(portal), "Portal STR")

class AutomacaoModelTest(TestCase):
    def setUp(self):
        self.portal = Portal.objects.create(nome="Portal Automacao", url_base="http://automacao.com")

    def test_create_automacao(self):
        automacao = Automacao.objects.create(
            nome="Automacao Teste",
            portal=self.portal,
            ultima_execucao=datetime.now(),
            proxima_execucao=datetime.now(),
            ativo=True
        )
        self.assertEqual(automacao.nome, "Automacao Teste")
        self.assertEqual(automacao.portal, self.portal)
        self.assertTrue(automacao.ativo)

    def test_automacao_str(self):
        automacao = Automacao.objects.create(nome="Automacao STR", portal=self.portal)
        self.assertEqual(str(automacao), "Automacao STR")

class LogExecucaoAutomacaoModelTest(TestCase):
    def setUp(self):
        self.portal = Portal.objects.create(nome="Portal Log", url_base="http://log.com")
        self.automacao = Automacao.objects.create(nome="Automacao Log", portal=self.portal)

    def test_create_log_execucao_automacao(self):
        log = LogExecucaoAutomacao.objects.create(
            automacao=self.automacao,
            status='sucesso',
            mensagem="Execução bem-sucedida",
            dados_coletados={"key": "value"}
        )
        self.assertEqual(log.automacao, self.automacao)
        self.assertEqual(log.status, 'sucesso')
        self.assertEqual(log.mensagem, "Execução bem-sucedida")
        self.assertEqual(log.dados_coletados, {"key": "value"})
        self.assertIsNotNone(log.data_execucao)

    def test_log_execucao_automacao_str(self):
        log = LogExecucaoAutomacao.objects.create(automacao=self.automacao, status='falha')
        self.assertIn("Log de Automacao Log", str(log))
