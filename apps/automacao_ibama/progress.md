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
- Criadas as migrações para o modelo `LicencaAmbiental` (`python manage.py makemigrations automacao_ibama`).
- Aplicadas as migrações ao banco de dados (`python manage.py migrate`).

### Lógica de Automação
- Criada a estrutura de diretórios para custom commands (`mkdir -p apps/automacao_ibama/management/commands`).
- Criado o custom command `upload_licenca.py` em `apps/automacao_ibama/management/commands/` com a lógica inicial para:
    - Receber o ID da licença.
    - Obter credenciais do `.env` (IBAMA_LOGIN, IBAMA_SENHA).
    - Utilizar Playwright para navegar, logar, e simular o upload de arquivo.
    - Atualizar o status da licença no banco de dados.
