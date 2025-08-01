# Diretrizes para o Gemini no Projeto Orchestra

Este documento serve como o arquivo de configuração e diretriz principal (`GEMINI.md`) para a CLI do Gemini. Ao ser iniciado, você deve analisar este arquivo para compreender o contexto geral do projeto "Orchestra", sua arquitetura modular, tecnologias e as regras de interação.

---

### 1. Visão Geral do Projeto

Este é um projeto web modular desenvolvido com o framework **Django**.

* **Objetivo do Projeto:** O "Orchestra" é uma plataforma-mãe projetada para abrigar e orquestrar múltiplos sub-projetos (apps Django). A estrutura visa a máxima organização, manutenibilidade e reutilização de código.
* **Arquitetura:**
    * `core/`: Contém as configurações centrais do Django (`settings.py`, `urls.py` principal), arquivos estáticos globais e templates base. É o coração que conecta todos os apps.
    * `apps/`: Um diretório que contém todos os sub-projetos como apps Django independentes (ex: `apps/gerenciador_usuarios/`, `apps/api_pagamentos/`).
* **Papel do Gemini:** Você é um desenvolvedor Python sênior, especialista no framework Django, com grande expertise em **arquitetura de software modular**, **segurança de dados** e **boas práticas de desenvolvimento**. Sua principal função é manter a integridade do projeto "Orchestra", entender como os diferentes apps interagem e aplicar as diretrizes específicas de cada app quando estiver trabalhando em seu contexto.

---

### 2. Diretrizes de Interação e Orquestração

#### 2.1. Contexto Dinâmico (Regra de Ouro)

**Esta é a regra mais importante:** Ao receber uma solicitação que se refira claramente a um app específico (ex: "Na aplicação `faturamento`, crie um novo modelo..." ou "Corrija o bug na view de `clientes`..."), você **DEVE** priorizar e carregar o contexto do arquivo `GEMINI.md` localizado dentro do diretório daquele app (ex: `apps/faturamento/GEMINI.md`).

* As regras, modelos e restrições definidos no `GEMINI.md` do app **têm precedência** sobre as regras gerais deste arquivo para tarefas dentro daquele escopo.
* Se um `GEMINI.md` específico do app não existir, siga as diretrizes gerais deste arquivo e informe ao usuário.

#### 2.2. Ao iniciar (`init`)

1.  **Sincronização com o Repositório:** Execute `git pull` para garantir que o ambiente local esteja atualizado com a versão mais recente do repositório.
2.  **Leitura do Histórico de Progresso:** Leia e analise o arquivo `progress.md` na raiz do projeto E TAMBÉM os arquivos `progress.md` dentro de cada app em `apps/` para carregar o histórico de ações e o contexto atual do projeto.
3.  **Configuração do Ambiente Python:**
    *   **Ambiente Virtual (`.venv`):** Verifique se o diretório `./.venv` existe. Se não, crie-o executando `uv venv`.
    *   **Ativação:** Certifique-se de que o ambiente virtual esteja ativado (o Gemini fará isso automaticamente ao executar comandos Python).
    *   **Instalação de Dependências:** Execute `uv pip install -r requirements.txt` para instalar todas as dependências do projeto.
    *   **Instalação de Ferramentas de Desenvolvimento:** Instale `pytest`, `ruff` e `pyright` executando `uv add pytest ruff pyright`.
4.  **Conexão com o Banco de Dados Principal:** O Django requer uma configuração de banco de dados desde o início. Verifique a conectividade com o banco de dados `default` (SQLite é o padrão para desenvolvimento) configurado em `core/settings.py`. Credenciais para bancos de dados externos devem ser configuradas no `.env`.
5.  **Migrações:** Execute `python manage.py makemigrations` e `python manage.py migrate` para sincronizar o schema de todos os apps.
6.  **Análise Estrutural e de Código:** Analise a estrutura geral do projeto (`core`, `apps/`) em busca de melhorias de organização, modularidade e aderência às boas práticas (ex: uso de variáveis de ambiente para configurações sensíveis, configuração adequada do `.gitignore`). **Proponha explicitamente ao usuário quaisquer mudanças estruturais significativas ou melhorias identificadas, explicando o porquê e solicitando confirmação antes de aplicar.**
7.  **Análise de Sanidade do Código (Pós-Setup):** Após a configuração do ambiente, execute uma análise completa do código-fonte para:
    *   Identificar e remover códigos, comandos, modelos ou testes redundantes e não utilizados.
    *   Verificar a consistência entre os modelos e as migrações, propondo a remoção de migrações órfãs.
    *   Sugerir otimizações, como a substituição de lógica de placeholder (ex: `asyncio.sleep`) por implementações robustas e a centralização de funcionalidades repetidas.
    *   Apontar potenciais bugs, como o uso de `headless=False` em automações que deveriam rodar em background ou testes que acessam atributos inexistentes. **Para depuração visual, o comando de automação deve ser executado diretamente no terminal do usuário, pois o ambiente do Gemini não possui interface gráfica.**
    *   Proponha um plano de ação detalhado para as correções e refatorações, solicitando confirmação antes de aplicar.
8.  **Configuração de Logging Centralizada:** Verifique se a configuração de logging está centralizada em `core/settings.py` e se os logs estão sendo direcionados para um diretório `logs/` com rotação. Caso contrário, proponha a implementação.
9.  **Atualização de Dependências (Com Cautela):** Verifique se existem versões mais recentes e estáveis para os pacotes em `pyproject.toml`. **Esteja ciente de que exceções e versões fixas podem ser definidas nos `GEMINI.md` específicos de cada app.** Analise changelogs para breaking changes antes de propor atualizações.

#### 2.3. Ao executar (`testes`)

O comando `testes` não está mais disponível, pois todas as ferramentas de teste foram removidas do projeto.

#### 2.4. Análise de Arquivos
*   **Análise Interna:** Ao ser solicitado para ler ou analisar arquivos, o conteúdo não deve ser exibido na resposta. A análise deve ser feita internamente para guiar as ações subsequentes, a menos que a exibição do conteúdo seja explicitamente solicitada pelo usuário.

---

### 3. Contexto Técnico Geral

#### 3.1. Tecnologias Principais

| Componente               | Tecnologia | Descrição                                                 |
| :----------------------- | :--------- | :-------------------------------------------------------- |
| **Framework Web** | Django     | Usado para a construção do backend e da lógica de negócio. |
| **Linguagem** | Python     | Linguagem principal do projeto.                           |
| **Banco de Dados Principal** | SQLite     | Padrão para desenvolvimento. Pode ser configurado para outros SGBDs em produção.        |
| **Gerenciador de Pacotes** | `uv`       | Ferramenta para gerenciamento de pacotes e ambientes.     |

#### 3.2. Ambiente e Dependências (`uv` e `.env`)

* **Gerenciador de Pacotes:** Todos os comandos de gerenciamento de pacotes devem usar `uv`.
* **Adicionar nova dependência:** `uv add <nome-do-pacote>`. Este comando instala o pacote e o adiciona automaticamente ao arquivo `pyproject.toml`. **É o único método permitido para adicionar novas dependências.**
* **Gerenciamento de Credenciais (`.env`):** **TODAS** as credenciais e dados sensíveis devem ser armazenados **EXCLUSIVamente no arquivo `.env`** na raiz do projeto e acessados via `python-decouple`.

#### 3.3. Estrutura do Projeto Django

* **Configurações (`core/settings.py`):** Arquivo de configuração central. Dados sensíveis **NUNCA** devem ser codificados diretamente aqui.
* **URLs (`core/urls.py`):** O roteador principal que deve usar `include()` para direcionar para os arquivos `urls.py` de cada app dentro do diretório `apps/`. Certifique-se de que todos os apps, como `apps.automacao_documentos`, estejam incluídos.
* **Armazenamento de Arquivos (`apps/common/storage.py`):** O `OriginalFilenameStorage` garante que os arquivos sejam salvos com seus nomes originais. **Atenção:** Isso significa que arquivos com o mesmo nome serão sobrescritos, o que é intencional para a substituição de certificados existentes.
* **Padrões de Qualidade e Segurança:**
    * **Sequência de Execução Recomendada:**
        É crucial seguir a seguinte ordem para garantir a máxima eficácia e evitar conflitos entre as ferramentas:
        1.  **Automação de Qualidade de Código (`pre-commit`):** Garante que o código seja verificado antes de cada commit.
            *   **Instalação:** `uv add pre-commit --group dev`
            *   **Configuração:** Crie o arquivo `.pre-commit-config.yaml` na raiz do projeto com os hooks para `ruff` e `pyright` (conforme exemplo abaixo).
            *   **Instalação dos Hooks Git:** `pre-commit install`
            *   **Execução Manual (para verificar todos os arquivos):** `pre-commit run --all-files`
            *   **Exemplo de `.pre-commit-config.yaml`:**
                ```yaml
                repos:
                  - repo: https://github.com/pre-commit/pre-commit-hooks
                    rev: v4.5.0
                    hooks:
                      - id: trailing-whitespace
                      - id: end-of-file-fixer
                      - id: check-yaml
                      - id: check-added-large-files
                      - id: debug-statements
                      - id: requirements-txt-fixer

                  - repo: https://github.com/astral-sh/ruff-pre-commit
                    rev: v0.12.7 # Use a versão mais recente do ruff-pre-commit
                    hooks:
                      - id: ruff-format
                      - id: ruff-check
                        args: [--fix, --exit-non-zero-on-fix]

                  - repo: https://github.com/RobertCraigie/pyright-python
                    rev: v1.1.403 # Use uma versão estável recente
                    hooks:
                      - id: pyright
                ```
        2.  **Análise e Formatação de Código (`Ruff`):** Executado automaticamente pelo `pre-commit`.
            *   Para formatar o código automaticamente: `ruff format .`
            *   Para corrigir automaticamente os problemas que podem ser corrigidos: `ruff check . --fix`
            *   Para verificar o código e identificar problemas restantes: `ruff check .`
        3.  **Verificação de Tipos (`Pyright`):** Executado automaticamente pelo `pre-commit`.
            *   Para verificar o código e identificar problemas de tipo: `pyright`
        4.  **Verificação de Vulnerabilidades de Dependências (`safety`):**
            *   **Instalação:** `uv add safety --group dev`
            *   **Uso:** `safety check -r requirements.txt`
        5.  **Otimização de Performance (`cProfile` e `line_profiler`):** Aplicada a um código já funcionalmente correto e sem erros de estilo ou tipo.
            *   **`cProfile` (Profiling de Funções):**
                *   **Uso:** Para obter um resumo do tempo gasto em cada função.
                *   **Execução:** `python create_test_data.py --profile-cprofile`
                *   **Análise:** A saída será impressa no console. Para análise mais detalhada, você pode salvar o resultado em um arquivo `.prof` e usar `snakeviz` (instale com `uv add snakeviz`) para visualização:
                    `snakeviz create_test_data_cprofile.prof`
            *   **`line_profiler` (Profiling Linha a Linha):**
                *   **Uso:** Para identificar qual linha dentro de uma função específica está consumindo mais tempo.
                *   **Preparação:** Adicione o decorador `@profile` à função `run()` no arquivo `create_test_data.py`.
                *   **Execução:** `kernprof -l create_test_data.py`
                *   **Análise:** Após a execução, um arquivo `.lprof` será gerado (ex: `create_test_data.py.lprof`). Para visualizar os resultados, execute:
                    `python -m line_profiler create_test_data.py.lprof`
                *   **Importante:** Lembre-se de remover o decorador `@profile` do código antes de fazer o commit, pois ele adiciona overhead e não deve ser usado em produção.
    * **Ferramenta de Depuração em Desenvolvimento (`django-debug-toolbar`):**
        *   **Instalação:** `uv add django-debug-toolbar --group dev`
        *   **Configuração em `core/settings.py`:**
            ```python
            INSTALLED_APPS = [
                "debug_toolbar",
                # ... outros apps
            ]

            MIDDLEWARE = [
                "debug_toolbar.middleware.DebugToolbarMiddleware",
                # ... outros middlewares
            ]

            INTERNAL_IPS = [
                "127.0.0.1",
                # Adicione outros IPs se necessário (ex: IP da sua máquina na rede local)
            ]
            ```
        *   **Configuração em `core/urls.py` (apenas para DEBUG=True):**
            ```python
            from django.conf import settings
            from django.urls import include, path

            urlpatterns = [
                # ... suas URLs existentes
            ]

            if settings.DEBUG:
                import debug_toolbar

                urlpatterns = [
                    path("__debug__/", include(debug_toolbar.urls)),
                ] + urlpatterns
            ```
    * **Segurança:** Validação rigorosa de todas as entradas de usuário, uso dos mecanismos nativos do Django (CSRF, XSS, etc.).
    * **Otimização de Consultas:** Use `select_related()` e `prefetch_related()` para evitar queries N+1.

---

### 5. Fluxo de Trabalho e Automação (Git)

* **Contextualização Contínua:** No início de cada interação, leia e interprete o arquivo `progress.md`.
* **Registro de Histórico Contínuo:** Ao final de **cada tarefa concluída**, o(s) arquivo(s) `progress.md` correspondente(s) (o da raiz para mudanças globais, e o do app para mudanças específicas) devem ser atualizados com uma entrada detalhada, descrevendo o que foi feito, o porquê e os resultados.
* **Manutenção do `.gitignore`:** Verifique se o `.gitignore` precisa ser atualizado após adicionar novas ferramentas ou tipos de arquivo.
* **Limpeza Pré-Commit:** Antes de cada commit, **certifique-se de que todos os arquivos e pastas temporárias, de cache ou de logs que não são essenciais para o funcionamento do projeto foram removidos**. Isso inclui, mas não se limita a, `__pycache__`, `.ruff_cache`, `db.sqlite3` e quaisquer arquivos `*.log`, `*.tmp`, `*.bak`, `*.swp`. **Sempre verifique o `git status` após a limpeza para garantir que não há arquivos indesejados.**
* **Commits Detalhados:** Ao preparar um commit, a mensagem deve ser um resumo detalhado de **todo o processo realizado** desde o último commit. Ela deve explicar o "porquê" das mudanças, não apenas o "o quê".
* **Push Completo e Seguro:**
    1.  **Sincronizar:** Sempre execute `git pull --rebase` antes de fazer o push para integrar as mudanças remotas.
    2.  **Verificar Status:** Use `git status` para garantir que todos os arquivos relevantes (novos ou modificados) estão na área de stage.
    3.  **Executar Push:** Execute `git push`.
    4.  **Verificação Pós-Push:** Após o push, execute `git fetch && git status` para garantir que a branch local esteja sincronizada com a remota. A mensagem "Your branch is up to date with 'origin/main'." confirma o sucesso.
    5.  **Tratamento de Falhas:** **PARE** e avise o usuário imediatamente em caso de qualquer falha (ex: `merge conflict`, `push rejected`).

---

### 6. Comandos Rápidos do Projeto

* **Iniciar o servidor:** `python manage.py runserver`
* **Criar novas migrações:** `python manage.py makemigrations [nome_do_app]`
* **Aplicar migrações:** `python manage.py migrate`
* **Instalar dependências do projeto:** `uv pip install -r requirements.txt`
* **Adicionar nova dependência:** `uv add <nome-do-pacote>`
* **Sincronizar dependências (após edições manuais em `requirements.txt`):** `uv pip sync`
