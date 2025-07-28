# Histórico de Progresso do App: Automação Ibama

Este arquivo registra as principais ações e configurações realizadas especificamente no app "Automação Ibama".

## 25 de Julho de 2025

### Criação e Configuração do App
- Criado o diretório `apps/automacao_ibama` (`mkdir -p apps/automacao_ibama`).
- Criado o app Django `automacao_ibama` dentro do diretório `apps/` (`python manage.py startapp automacao_ibama apps/automacao_ibama`).
- Registrado o app `automacao_ibama` em `INSTALLED_APPS` no `core/settings.py`.
- Corrigido o `name` em `apps/automacao_ibama/apps.py` para `'apps.automacao_ibama'` para garantir a importação correta.

### Modelagem de Dados
- Criado o modelo `LicencaAmbiental` em `apps/automacao_ibama/models.py` com campos para número, descrição, arquivo PDF, status, data de criação e atualização.
- Criadas as migrações para o modelo `LicencaAutomacao` (`python manage.py makemigrations automacao_ibama`).
- Aplicadas as migrações ao banco de dados (`python manage.py migrate`).

### Lógica de Automação
- Criada a estrutura de diretórios para custom commands (`mkdir -p apps/automacao_ibama/management/commands`).
- Criado o custom command `upload_licenca.py` em `apps/automacao_ibama/management/commands/` com a lógica inicial para:
    - Receber o ID da licença.
    - Obter credenciais do `.env` (IBAMA_LOGIN, IBAMA_SENHA).
    - Utilizar Playwright para navegar, logar, e simular o upload de arquivo.
    - Atualizar o status da licença no banco de dados.

## 28 de Julho de 2025

### Alinhamento com as Diretrizes Globais do Projeto
- **Atualização do `GEMINI.md` do App:** O arquivo de diretrizes do app (`apps/automacao_ibama/GEMINI.md`) foi atualizado para refletir as novas regras de fluxo de trabalho com o Git, garantindo consistência com as diretrizes do projeto principal `Orchestra`. As novas regras incluem commits detalhados e um procedimento de push seguro e sincronizado.

### Automação de Login no Portran
- **Criação do Comando `login_portran`:** Criado o custom command `login_portran.py` em `apps/automacao_ibama/management/commands/`. Este comando utiliza Playwright para automatizar o processo de login no portal Portran, preenchendo os campos de usuário e senha e clicando no botão de autenticar, utilizando credenciais lidas do arquivo `.env`.
- **Teste do Comando `login_portran`:** O comando `login_portran` foi executado com sucesso, abrindo o navegador e simulando o login no portal Portran. As dependências de sistema do Playwright foram instaladas para permitir a execução do navegador.
- **Integração de Login no `upload_licenca`:** A lógica de login no portal Portran foi integrada ao comando `upload_licenca.py`. O comando agora utiliza `async_playwright` e as credenciais `PORTRAN_USER` e `PORTRAN_PASSWORD` do `.env` para autenticar antes de prosseguir com a lógica de upload.
- **Criação do Comando `process_portran_vehicles`:** Criado o custom command `process_portran_vehicles.py` em `apps/automacao_ibama/management/commands/`. Este comando automatiza o login no portal Portran, navega até o dashboard, clica nos cards "Vencidos" e "À vencer" e extrai as placas de veículos de cada página.