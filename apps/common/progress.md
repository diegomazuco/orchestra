# Histórico de Progresso do App: Common

Este arquivo registra as principais ações e configurações realizadas especificamente no app "Common".

## 30 de Julho de 2025

### Criação e Configuração do App
- Criado o diretório `apps/common` (`mkdir -p apps/common`).
- Criado o app Django `common` dentro do diretório `apps/` (`python manage.py startapp common apps/common`).
- Registrado o app `common` em `INSTALLED_APPS` no `core/settings.py`.
- Corrigido o `name` em `apps/common/apps.py` para `'apps.common'` para garantir a importação correta.

### Centralização de Serviços
- Criado o arquivo `apps/common/services.py`.
- Implementada a função assíncrona `login_to_portran(page, logger)` em `apps/common/services.py`. Esta função encapsula a lógica de login no portal Portran/Ipiranga, utilizando `playwright` e credenciais do `.env`. Inclui esperas explícitas e logging detalhado.

### Refatoração de Comandos Existentes
- **`login_portran.py`:** Modificado para remover a lógica de login duplicada e chamar a função `login_to_portran` do serviço `common`.
- **`upload_licenca.py`:** Modificado para remover a lógica de login duplicada e chamar a função `login_to_portran` do serviço `common`.
- **`automacao_documentos_ipiranga.py`:** Modificado para remover a lógica de login duplicada e chamar a função `login_to_portran` do serviço `common`.