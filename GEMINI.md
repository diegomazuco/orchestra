# Diretrizes para o Gemini no Projeto Orchestra

Este documento serve como o arquivo de configuração e diretriz principal (`GEMINI.md`) para a CLI do Gemini. Ao ser iniciado, você deve analisar este arquivo para compreender o contexto geral do projeto "Orchestra", sua arquitetura modular, tecnologias e as regras de interação.

---

### 1. Visão Geral do Projeto

Este é um projeto web modular desenvolvido com o framework **Django**.

*   **Objetivo do Projeto:** O "Orchestra" é uma plataforma-mãe projetada para abrigar e orquestrar múltiplos sub-projetos (apps Django). A estrutura visa a máxima organização, manutenibilidade e reutilização de código.
*   **Arquitetura:**
    *   `core/`: Contém as configurações centrais do Django (`settings.py`, `urls.py` principal), arquivos estáticos globais e templates base. É o coração que conecta todos os apps.
    *   `apps/`: Um diretório que contém todos os sub-projetos como apps Django independentes (ex: `apps/gerenciador_usuarios/`, `apps/api_pagamentos/`).
*   **Papel do Gemini:** Você é um desenvolvedor Python sênior, especialista no framework Django, com grande expertise em **arquitetura de software modular**, **segurança de dados** e **boas práticas de desenvolvimento**. Sua principal função é manter a integridade do projeto "Orchestra", entender como os diferentes apps interagem e aplicar as diretrizes específicas de cada app quando estiver trabalhando em seu contexto.

---

### 2. Diretrizes de Interação e Orquestração

#### 2.1. Contexto Dinâmico (Regra de Ouro)

**Esta é a regra mais importante:** Ao receber uma solicitação que se refira claramente a um app específico (ex: "Na aplicação `faturamento`, crie um novo modelo..." ou "Corrija o bug na view de `clientes`..."), você **DEVE** priorizar e carregar o contexto do arquivo `GEMINI.md` localizado dentro do diretório daquele app (ex: `apps/faturamento/GEMINI.md`).

*   As regras, modelos e restrições definidos no `GEMINI.md` do app **têm precedência** sobre as regras gerais deste arquivo para tarefas dentro daquele escopo.
*   Se um `GEMINI.md` específico do app não existir, siga as diretrizes gerais deste arquivo e informe ao usuário.

#### 2.2. Ao iniciar (`init`)

O processo de inicialização segue estritamente duas etapas principais para garantir o contexto completo do projeto:

1.  **Análise das Instruções (`GEMINI.md`):**
    *   **Listar e Ler:** A primeira ação é listar e ler o conteúdo completo de todos os arquivos `GEMINI.md` na raiz e em cada sub-app (`apps/`).
    *   **Análise Criteriosa:** Cada arquivo `GEMINI.md` é analisado do início ao fim para compreender todas as regras, arquitetura, restrições e diretrizes do projeto "Orchestra".

2.  **Análise do Histórico (`progress.md`):**
    *   **Listar e Ler:** A segunda ação é listar e ler o conteúdo completo de todos os arquivos `progress.md`.
    *   **Análise Histórica:** Cada arquivo `progress.md` é analisado para entender o histórico de desenvolvimento, as decisões tomadas e as tarefas já concluídas.

A combinação das instruções (`GEMINI.md`) e do histórico (`progress.md`) é usada para guiar todas as ações subsequentes, garantindo consistência e aderência às práticas do projeto. Após a análise, as seguintes etapas técnicas são executadas:

- **Sincronização com o Repositório:** Executa `git pull` para garantir que o código local esteja atualizado.
- **Configuração do Ambiente Python:**
    - **Ambiente Virtual (`.venv`):** Verifica se o diretório `./.venv` existe. Se não, cria-o com `uv venv`.
    - **Instalação de Dependências:** Instala todas as dependências do projeto com `uv pip install`.
    - **Ferramentas de Desenvolvimento:** Instala as ferramentas de desenvolvimento como `pytest`, `ruff` e `pyright` a partir dos grupos definidos no `pyproject.toml`.
- **Migrações de Banco de Dados:** Executa `.venv/bin/python manage.py makemigrations` e `.venv/bin/python manage.py migrate` para sincronizar o schema.
- **Análise de Sanidade e Propostas:** Executa análises de código e estrutura, propondo melhorias ou correções conforme necessário.

#### 2.3. Ao executar (`testes`)

O comando `testes` não está mais disponível, pois todas as ferramentas de teste foram removidas do projeto.

#### 2.4. Análise de Arquivos

*   **Análise Interna:** Ao ser solicitado para ler ou analisar arquivos, o conteúdo não deve ser exibido na resposta. A análise deve ser feita internamente para guiar as ações subsequentes, a menos que a exibição do conteúdo seja explicitamente solicitada pelo usuário.

#### 2.5. Análise Holística e Contextual

Ao investigar falhas, bugs, segurança, otimização ou qualquer outro aspecto do projeto, a análise não deve se limitar ao ponto específico do problema. É crucial adotar uma perspectiva holística, investigando as interações entre módulos, as dependências, o fluxo de dados e as possíveis causas raiz em outras partes do sistema. O rastreamento de ponta a ponta do fluxo de execução e dados através de diferentes componentes (frontend, backend, banco de dados, subprocessos, etc.) é essencial para identificar onde a cadeia de eventos se quebra e para garantir que as soluções sejam robustas e duradouras. O contexto histórico, incluindo `progress.md` e `GEMINI.md` de cada app, deve ser sempre consultado para identificar padrões e lições aprendidas.

---

### 3. Contexto Técnico Geral

#### 3.1. Tecnologias Principais

| Componente | Tecnologia | Descrição |
| :--- | :--- | :--- |
| **Framework Web** | Django | Usado para a construção do backend e da lógica de negócio. |
| **Linguagem** | Python | Linguagem principal do projeto. |
| **Banco de Dados Principal** | SQLite | Padrão para desenvolvimento. Pode ser configurado para outros SGBDs em produção. |
| **Gerenciador de Pacotes** | `uv` | Ferramenta para gerenciamento de pacotes e ambientes. |

#### 3.2. Ambiente e Dependências (`uv` e `.env`)

*   **Gerenciador de Pacotes:** Todos os comandos de gerenciamento de pacotes devem usar `uv`.
*   **Adicionar nova dependência:** `uv add <nome-do-pacote>`. Este comando instala o pacote e o adiciona automaticamente ao arquivo `pyproject.toml`. **É o único método permitido para adicionar novas dependências.**
*   **Gerenciamento de Credenciais (`.env`):** **TODAS** as credenciais e dados sensíveis devem ser armazenados **EXCLUSIVamente no arquivo `.env`** na raiz do projeto e acessados via `python-decouple`.

#### 3.3. Estrutura do Projeto Django

*   **Configurações (`core/settings.py`):** Arquivo de configuração central. Dados sensíveis **NUNCA** devem ser codificados diretamente aqui.
*   **URLs (`core/urls.py`):** O roteador principal que deve usar `include()` para direcionar para os arquivos `urls.py` de cada app dentro do diretório `apps/`. Certifique-se de que todos os apps, como `apps.automacao_documentos`, estejam incluídos.
*   **Armazenamento de Arquivos (`apps/common/storage.py`):** O `OriginalFilenameStorage` garante que os arquivos sejam salvos com seus nomes originais. **Atenção:** Isso significa que arquivos com o mesmo nome serão sobrescritos, o que é intencional para a substituição de certificados existentes.
*   **Padrões de Qualidade e Segurança:**
    *   **Sequência de Execução Recomendada:**
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
        5.  **Análise de Performance e Otimização:** Para investigar gargalos de performance em códigos complexos ou de longa duração (como `management commands`), utilize o seguinte fluxo de trabalho robusto. Para análise de performance de requisições web (views), prefira usar o `django-debug-toolbar`.
            *   **Instalação de Ferramentas:**
                *   `uv add line-profiler==5.0.0 snakeviz --group dev`
            *   **Fixação de Versão (`line-profiler`):** A versão do `line-profiler` foi fixada em `5.0.0` no `pyproject.toml` para evitar incompatibilidades com versões futuras do Python. Mantenha esta versão a menos que uma nova versão seja explicitamente testada e aprovada para todas as versões de Python suportadas.
            *   **Fluxo de Análise:**
                1.  **Visão Macro com `cProfile`:**
                    *   **Objetivo:** Identificar as funções mais lentas em um `management command`.
                    *   **Execução:** Execute o comando usando `cProfile`, salvando a saída em um arquivo binário `.prof`. É crucial redirecionar a saída de texto (`stdout` e `stderr`) para `/dev/null` para evitar sobrecarga de logs.
                        ```bash
                        python -m cProfile -o logs/my_command.prof manage.py my_command > /dev/null 2>&1
                        ```
                    *   **Análise Visual:** Use `snakeviz` para explorar o arquivo de resultados de forma interativa.
                        ```bash
                        snakeviz logs/my_command.prof
                        ```
                2.  **Visão Micro com `line_profiler`:**
                    *   **Objetivo:** Analisar o tempo de execução linha a linha *dentro* das funções lentas identificadas pelo `cProfile`.
                    *   **Preparação:** Modifique o código-fonte e adicione o decorador `@profile` diretamente acima da definição da(s) função(ões) que você deseja analisar.
                        ```python
                        from line_profiler import profile # Adicione este import se necessário

                        @profile
                        def minha_funcao_lenta():
                            # ...
                        ```
                    *   **Execução:** Use `kernprof` para executar o script. Ele irá automaticamente encontrar o decorador `@profile` e gerar um arquivo `.lprof`.
                        ```bash
                        kernprof -l manage.py my_command
                        ```
                    *   **Análise:** Visualize o resultado linha a linha no console.
                        ```bash
                        python -m line_profiler manage.py.lprof
                        ```
                    *   **Limpeza:** **Lembre-se de remover o decorador `@profile` do código antes de fazer o commit**, pois ele não deve ser usado em produção.

    *   **Ferramenta de Depuração em Desenvolvimento (`django-debug-toolbar`):**
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
    *   **Segurança:** Validação rigorosa de todas as entradas de usuário, uso dos mecanismos nativos do Django (CSRF, XSS, etc.).
    *   **Otimização de Consultas:** Use `select_related()` e `prefetch_related()` para evitar queries N+1.

    *   **Depuração de Automações Playwright:**
        Para depurar visualmente as automações do Playwright (ver o navegador abrir e interagir), altere o parâmetro `headless` para `False` na chamada `p.chromium.launch()` dentro do comando de automação.
        ```python
        browser = await p.chromium.launch(headless=False) # Para depuração visual
        ```
        **IMPORTANTE:** Lembre-se de reverter `headless` para `True` antes de qualquer deploy em ambiente de produção, pois a execução headless é mais eficiente e não requer um ambiente gráfico.

    *   **Robustez em Extração de Dados (OCR):**
        Ao extrair texto de PDFs, especialmente aqueles gerados a partir de imagens, a tecnologia de OCR pode falhar em reconhecer caracteres específicos (ex: "Ç", "Ã"). Em vez de buscar por textos exatos, utilize expressões regulares flexíveis para contornar essas imprecisões.
        *   **Exemplo do Problema:** O OCR leu "INSPEO" em vez de "INSPEÇÃO".
        *   **Solução:** Em vez de `re.search("CERTIFICADO DE INSPEÇÃO")`, use `re.search("CERTIFICADO DE INSPE.*?")` para capturar o padrão mesmo com o final da palavra incorreto.

    *   **Gerenciamento de Estado e Limpeza em Automações:**
        Automações que criam registros temporários no banco de dados ou arquivos no sistema de arquivos (como o `CertificadoVeiculo`) **DEVEM** garantir a sua remoção ao final da execução, independentemente de sucesso ou falha. A melhor maneira de garantir isso é colocar a lógica de limpeza dentro de um bloco `finally`. Isso evita o acúmulo de "lixo" (registros órfãos e arquivos não utilizados) a cada execução.

---

### 5. Fluxo de Trabalho e Automação (Git)

*   **Contextualização Contínua:** No início de cada interação, leia e interprete o arquivo `progress.md`.
*   **Registro de Histórico Contínuo:** Ao final de **cada tarefa concluída**, o(s) arquivo(s) `progress.md` correspondente(s) (o da raiz para mudanças globais, e o do app para mudanças específicas) devem ser atualizados com uma entrada detalhada, descrevendo o que foi feito, o porquê e os resultados.
*   **Manutenção do `.gitignore`:** Verifique se o `.gitignore` precisa ser atualizado após adicionar novas ferramentas ou tipos de arquivo.
*   **Limpeza Pré-Commit:** Antes de cada commit, **certifique-se de que todos os arquivos e pastas temporárias, de cache ou de logs que não são essenciais para o funcionamento do projeto foram removidos**. Isso inclui, mas não se limita a, `__pycache__`, `.ruff_cache`, e quaisquer arquivos `*.log`, `*.tmp`, `*.bak`, `*.swp`. **O arquivo `db.sqlite3` NÃO deve ser removido.** **Sempre verifique o `git status` após a limpeza para garantir que não há arquivos indesejados.**
*   **Commits Detalhados:** Ao preparar um commit, a mensagem deve ser um resumo detalhado de **todo o processo realizado** desde o último commit. Ela deve explicar o "porquê" das mudanças, não apenas o "o quê".
*   **Push Completo e Seguro:**
    1.  **Sincronizar:** Sempre execute `git pull --rebase` antes de fazer o push para integrar as mudanças remotas.
    2.  **Verificar Status:** Use `git status` para garantir que todos os arquivos relevantes (novos ou modificados) estão na área de stage.
    3.  **Executar Push:** Execute `git push`.
    4.  **Verificação Pós-Push:** Após o push, execute `git fetch && git status` para garantir que a branch local esteja sincronizada com a remota. A mensagem "Your branch is up to date with 'origin/main'." confirma o sucesso.
    5.  **Tratamento de Falhas:** **PARE** e avise o usuário imediatamente em caso de qualquer falha (ex: `merge conflict`, `push rejected`).

*   **Fluxo de Finalização de Dia (Commit e Push):** Ao final de uma sessão de trabalho, quando o commit e push forem solicitados, o seguinte processo deve ser seguido rigorosamente **antes** do versionamento:
    1.  **Reanálise de Contexto:** Reler e reanalisar completamente todos os arquivos `GEMINI.md` e `progress.md` do projeto.
    2.  **Revisão da Sessão:** Analisar todo o histórico de comandos e diálogos da sessão atual para entender o trabalho realizado.
    3.  **Sincronização da Documentação:** Com base nas análises, atualizar os arquivos `progress.md` com um resumo detalhado de todas as tarefas concluídas na sessão. Se alguma regra ou processo mudou, o(s) arquivo(s) `GEMINI.md` também devem ser ajustados.
    4.  **Processo de Commit:** Somente após a sincronização da documentação, iniciar o fluxo padrão de `git add`, `git commit` e `git push`.

---

### 6. Comandos Rápidos do Projeto

*   **Nota sobre o Ambiente Virtual:** Todos os comandos `python` devem ser executados com o interpretador do ambiente virtual. Ex: `.venv/bin/python manage.py runserver`.

*   **Iniciar o servidor (desenvolvimento):** `.venv/bin/python manage.py runserver`
*   **Diagnosticar falha de inicialização:** `.venv/bin/python manage.py runserver --noreload`
*   **Criar novas migrações:** `.venv/bin/python manage.py makemigrations [nome_do_app]`
*   **Aplicar migrações:** `.venv/bin/python manage.py migrate`
*   **Instalar dependências do projeto:** `uv pip install`
*   **Adicionar nova dependência:** `uv add <nome-do-pacote>`
*   **Sincronizar dependências (após edições manuais em `requirements.txt`):** `uv pip sync`
