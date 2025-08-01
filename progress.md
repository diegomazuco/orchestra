## 2025-07-31 - Inicialização, Refatoração e Configuração da Automação

- **Inicialização do Projeto:**
    - Sincronização do repositório.
    - Leitura dos arquivos `progress.md` para contexto.
    - Configuração do ambiente Python: `.venv` verificado, dependências instaladas (`requirements.txt`), e ferramentas de desenvolvimento (`pytest`, `ruff`, `pyright`) instaladas.
    - Migrações do Django executadas.
    - Análise da estrutura do projeto (`core/settings.py`, `core/urls.py`, `pyproject.toml`) para entender a arquitetura modular e configurações.
    - Verificação de sanidade do código: Limpeza de arquivos temporários e de cache.

- **Refatoração do Comando `automacao_documentos_ipiranga`:**
    - Implementada a extração de `numero_documento_valor` e `vencimento_valor_pdf` do texto do PDF usando expressões regulares.
    - Substituído o `asyncio.sleep(5)` por um `TODO` para o usuário implementar a lógica de espera por um elemento de sucesso na página.
    - Removidos comentários `TODO` e corrigido o comentário sobre `headless`.

- **Configuração da Automação Web:**
    - Alterado o modo `headless` do Playwright para `False` em `apps/automacao_ipiranga/management/commands/automacao_documentos_ipiranga.py` para permitir a visualização da automação.
    - Adicionada uma URL (`iniciar_automacao/`) e uma view (`iniciar_automacao`) em `apps/automacao_ipiranga/` para disparar a automação via requisição POST.

## 2025-08-01 - Otimizações, Segurança e Processamento de Múltiplos Certificados

- **Refatoração do Comando `automacao_documentos_ipiranga`:**
    - **Suporte a Múltiplos IDs:** O comando agora aceita múltiplos `certificado_ids` como argumento, permitindo o processamento em lote.
    - **Inicialização Única do Navegador e Login:** O navegador e o login no portal são realizados apenas uma vez por execução do comando, otimizando o desempenho.
    - **Extração de Dados do PDF Aprimorada:**
        - O número do documento é extraído e formatado para conter apenas dígitos (removendo pontos e letras como 'A').
        - A data de vencimento é extraída de forma mais robusta, buscando a última data no formato `DD/MON/YY` no primeiro bloco do certificado, garantindo a precisão.
    - **Lógica de Confirmação de Sucesso:** A confirmação final de salvamento é feita aguardando o redirecionamento para a página de listagem de veículos, tornando a automação mais confiável.
    - **Limpeza Automática:**
        - Em caso de sucesso, o registro `CertificadoVeiculo` e o arquivo PDF associado são removidos do banco de dados e do sistema de arquivos, respectivamente.
        - Arquivos temporários de log (`temp_automation.log`) e de depuração (`debug_*.png`, `debug_*.html`) são removidos incondicionalmente ao final da execução.
        - Screenshots de erro (`error_screenshot_*.png`, `login_error_screenshot.png`) são agora removidos, conforme solicitação do usuário.
    - **Tratamento de Erros por Certificado:** Se um certificado individual falhar, a automação registra o erro, atualiza o status do certificado para 'falha' e tenta continuar com o próximo, sem interromper todo o processo.

- **Aprimoramentos no `apps/common/services.py`:**
    - Adicionada a importação do módulo `asyncio`.
    - Implementada lógica de resiliência para instabilidade de login no portal Ipiranga: o script aguarda alguns segundos e recarrega a página se detectar a mensagem "Erro Inesperado. Favor tente novamente.", aumentando a robustez da automação.

- **Atualizações de Configuração (`core/settings.py`):**
    - O app `apps.automacao_documentos` foi adicionado à lista `INSTALLED_APPS`.
    - Implementada uma configuração de logging centralizada, direcionando os logs para um diretório `logs/` com rotação, melhorando a organização e o gerenciamento de logs.

- **Atualizações de Rotas (`core/urls.py`):**
    - A inclusão das URLs para o app `apps.automacao_documentos` foi adicionada.

- **Documentação de Armazenamento (`apps/common/storage.py`):**
    - Adicionado um comentário explícito na classe `OriginalFilenameStorage` para documentar o comportamento intencional de sobrescrita de arquivos com o mesmo nome.

- **Organização de Scripts (`create_test_data.py`):**
    - Adicionado um comentário no topo do arquivo `create_test_data.py` recomendando sua realocação para um diretório de scripts utilitários para melhor organização do projeto.

- **Análise de Estrutura e Boas Práticas:**
    - A estrutura geral do projeto "Orchestra" foi confirmada como modular e bem organizada, seguindo as convenções do Django.
    - Reforçada a importância de executar comandos de automação diretamente no terminal do usuário para depuração visual, devido às limitações do ambiente do Gemini sem interface gráfica.

## 2025-08-01 - Configuração e Execução de Ferramentas de Qualidade e Performance

- **Configuração e Execução do Ruff (Linter e Formatador):**
    - **Instalação:** `ruff` e `ruff-django` instalados como dependências de desenvolvimento.
    - **Configuração:** `pyproject.toml` atualizado com regras abrangentes (incluindo `DJ` para Django), exclusões de diretórios e configurações de formatação (`ruff format`).
    - **Execução:** `ruff check .` e `ruff format .` executados para garantir a conformidade com o estilo e a identificação de problemas. Todos os erros de linting foram resolvidos.

- **Configuração e Execução do Pyright (Verificador de Tipos Estático):**
    - **Instalação:** `pyright` e `django-stubs` instalados como dependências de desenvolvimento.
    - **Configuração:** `pyrightconfig.json` criado com configurações recomendadas para projetos Django, incluindo `include`, `exclude`, `extraPaths`, `pythonVersion`, `pythonPlatform`, `typeCheckingMode`, e `reportMissingTypeStubs`.
    - **Correções:** Erros de `reportAttributeAccessIssue` e `reportMissingTypeStubs` foram resolvidos através da adição de `type: ignore` em linhas específicas e instalação de `decouple-types`.
    - **Execução:** `pyright` executado, resultando em "0 errors, 0 warnings, 0 informations".

- **Configuração e Execução de Profiling (`cProfile` e `line_profiler`):**
    - **Instalação:** `line-profiler` instalado como dependência de desenvolvimento.
    - **Preparação do Script:** `create_test_data.py` modificado para permitir profiling com `cProfile` (via `--profile-cprofile`) e `line_profiler` (via `@profile` e `kernprof`).
    - **Execução `cProfile`:** `python create_test_data.py --profile-cprofile` executado com sucesso.
    - **Execução `line_profiler`:** `kernprof -l create_test_data.py` executado com sucesso, gerando o arquivo `.lprof`.
    - **Análise:** Resultados de profiling obtidos, identificando as operações de criação do ORM do Django como as mais custosas em `create_test_data.py`.
    - **Reversão:** Decorador `@profile` removido de `create_test_data.py` após o profiling.

- **Configuração do `pre-commit`:**
    - **Instalação:** `pre-commit` instalado como dependência de desenvolvimento.
    - **Configuração:** `.pre-commit-config.yaml` criado com hooks para `pre-commit-hooks`, `ruff-pre-commit` e `pyright-python`.
    - **Execução:** `pre-commit install` e `pre-commit run --all-files` executados com sucesso após a resolução de problemas de versão e configuração.

- **Instalação do `safety`:**
    - **Instalação:** `safety` instalado como dependência de desenvolvimento.

- **Configuração do `django-debug-toolbar`:**
    - **Instalação:** `django-debug-toolbar` instalado como dependência de desenvolvimento.
    - **Configuração:** `core/settings.py` e `core/urls.py` atualizados para integrar o `django-debug-toolbar` em ambiente de desenvolvimento.
