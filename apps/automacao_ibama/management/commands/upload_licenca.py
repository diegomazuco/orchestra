import os
from django.core.management.base import BaseCommand, CommandError
from decouple import config
from playwright.sync_api import sync_playwright

from apps.automacao_ibama.models import LicencaAmbiental

class Command(BaseCommand):
    help = 'Automatiza o upload de uma licença ambiental para o portal do IBAMA.'

    def add_arguments(self, parser):
        parser.add_argument('licenca_id', type=int, help='ID da Licença Ambiental a ser processada.')

    def handle(self, *args, **options):
        licenca_id = options['licenca_id']

        try:
            licenca = LicencaAmbiental.objects.get(pk=licenca_id)
        except LicencaAmbiental.DoesNotExist:
            raise CommandError(f'Licença Ambiental com ID "{licenca_id}" não encontrada.')

        self.stdout.write(self.style.SUCCESS(f'Iniciando automação para a licença: {licenca.numero}'))

        # Credenciais do .env
        ibama_login = config('IBAMA_LOGIN')
        ibama_senha = config('IBAMA_SENHA')

        if not ibama_login or not ibama_senha:
            raise CommandError('As variáveis de ambiente IBAMA_LOGIN e IBAMA_SENHA devem ser configuradas no arquivo .env.')

        # Lógica da automação com Playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True) # headless=True para rodar sem interface gráfica
            page = browser.new_page()

            try:
                # 1. Navegar até a página de login
                self.stdout.write('Navegando para a página de login...')
                page.goto('https://www.ibama.gov.br/login') # Substitua pela URL real do login do IBAMA

                # 2. Preencher campos de login e senha
                self.stdout.write('Preenchendo credenciais...')
                page.fill('input[name="username"]', ibama_login) # Substitua pelo seletor CSS real do campo de usuário
                page.fill('input[name="password"]', ibama_senha) # Substitua pelo seletor CSS real do campo de senha
                page.click('button[type="submit"]') # Substitua pelo seletor CSS real do botão de login

                # 3. Aguardar navegação pós-login (pode ser um redirecionamento ou carregamento de SPA)
                page.wait_for_url('https://www.ibama.gov.br/dashboard') # Substitua pela URL real pós-login

                self.stdout.write(self.style.SUCCESS('Login realizado com sucesso!'))

                # 4. Navegar até a página de upload
                self.stdout.write('Navegando para a página de upload...')
                page.goto('https://www.ibama.gov.br/upload-licenca') # Substitua pela URL real da página de upload

                # 5. Fazer upload do arquivo
                self.stdout.write(f'Fazendo upload do arquivo: {licenca.arquivo.path}')
                # Certifique-se de que o caminho do arquivo é absoluto
                file_path = os.path.abspath(licenca.arquivo.path)
                page.set_input_files('input[type="file"]', file_path) # Substitua pelo seletor CSS real do campo de upload

                # 6. Clicar no botão de envio (se houver um separado do input file)
                # page.click('button[type="submit-upload"]') # Exemplo: descomente e ajuste se necessário

                # 7. Aguardar confirmação de upload
                # page.wait_for_selector('.upload-success-message') # Exemplo: aguardar uma mensagem de sucesso
                self.stdout.write(self.style.SUCCESS('Arquivo enviado (simulado)!')) # Mensagem temporária

                # Atualizar status da licença
                licenca.status = 'enviado'
                licenca.save()
                self.stdout.write(self.style.SUCCESS(f'Status da licença {licenca.numero} atualizado para "enviado".'))

            except Exception as e:
                licenca.status = 'falha'
                licenca.save()
                self.stdout.write(self.style.ERROR(f'Erro durante a automação para a licença {licenca.numero}: {e}'))
                raise CommandError(f'Erro na automação: {e}')
            finally:
                browser.close()

        self.stdout.write(self.style.SUCCESS('Automação concluída.'))
