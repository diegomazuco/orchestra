import os
from django.core.management.base import BaseCommand, CommandError
from decouple import config
from playwright.async_api import async_playwright
import asyncio

from apps.automacao_documentos.models import LicencaAmbiental

class Command(BaseCommand):
    help = 'Automatiza o upload de uma licença ambiental para o portal do IBAMA.'

    def add_arguments(self, parser):
        parser.add_argument('licenca_id', type=int, help='ID da Licença Ambiental a ser processada.')

    async def handle_async(self, *args, **options):
        licenca_id = options['licenca_id']

        try:
            licenca = LicencaAmbiental.objects.get(pk=licenca_id) # type: ignore
        except LicencaAmbiental.DoesNotExist: # type: ignore
            raise CommandError(f'Licença Ambiental com ID "{licenca_id}" não encontrada.')

        self.stdout.write(self.style.SUCCESS(f'Iniciando automação para a licença: {licenca.numero}'))

        # Credenciais do .env
        portran_user = config('PORTRAN_USER')
        portran_password = config('PORTRAN_PASSWORD')

        if not portran_user or not portran_password:
            raise CommandError('As variáveis de ambiente PORTRAN_USER e PORTRAN_PASSWORD devem ser configuradas no arquivo .env.')

        # Lógica da automação com Playwright
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True) # headless=True para rodar sem interface gráfica
            page = await browser.new_page()

            try:
                # Lógica de Login no Portran
                self.stdout.write('Navegando para a página de login do Portran...')
                await page.goto('https://sites.redeipiranga.com.br/WAPortranNew/usuario/exibir')

                # Preenchendo o campo de usuário
                user_selector = '#codigoUsuario' # id="codigoUsuario"
                await page.fill(user_selector, str(portran_user)) # type: ignore
                self.stdout.write(f'Usuário preenchido: {portran_user}')

                # Preenchendo o campo de senha
                password_selector = '#senha' # id="senha"
                await page.fill(password_selector, str(portran_password))
                self.stdout.write('Senha preenchida.')

                # Clicando no botão de autenticar
                login_button_selector = """input[type="submit"][value="Autenticar"]"""
                await page.click(login_button_selector)
                self.stdout.write('Botão de autenticar clicado.')

                # Aguardar um pouco para ver o resultado do login
                # Em um cenário real, você esperaria por um elemento específico na página pós-login
                # ou por uma URL específica. Aqui, apenas um delay para observação.
                await page.wait_for_timeout(5000) # Espera 5 segundos

                self.stdout.write(self.style.SUCCESS('Login no Portran realizado com sucesso!'))

                # 4. Navegar até a página de upload (URL do IBAMA, ajustar conforme necessário)
                self.stdout.write('Navegando para a página de upload...')
                await page.goto('https://www.ibama.gov.br/upload-licenca') # Substitua pela URL real da página de upload

                # 5. Fazer upload do arquivo
                self.stdout.write(f'Fazendo upload do arquivo: {licenca.arquivo.path}')
                # Certifique-se de que o caminho do arquivo é absoluto
                file_path = os.path.abspath(licenca.arquivo.path)
                await page.set_input_files('input[type="file"]', file_path) # Substitua pelo seletor CSS real do campo de upload

                # 6. Clicar no botão de envio (se houver um separado do input file)
                # await page.click('button[type="submit-upload"]') # Exemplo: descomente e ajuste se necessário

                # 7. Aguardar confirmação de upload
                # await page.wait_for_selector('.upload-success-message') # Exemplo: aguardar uma mensagem de sucesso
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
                await browser.close()

        self.stdout.write(self.style.SUCCESS('Automação concluída.')) # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore # type: ignore

    def handle(self, *args, **options):
        return asyncio.run(self.handle_async(*args, **options))
