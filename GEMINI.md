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
3.  **Ambiente Virtual (`.venv`):** Verifique se `./.venv` existe. Se não, execute `uv venv` para criá-lo. Em seguida, ative-o e execute `uv pip install -r requirements.txt` para garantir que todas as dependências globais estejam instaladas.
4.  **Conexão com o Banco de Dados Principal:** O Django requer uma configuração de banco de dados desde o início. Verifique a conectividade com o banco de dados `default` (SQLite é o padrão para desenvolvimento) configurado em `core/settings.py`. Credenciais para bancos de dados externos devem estar no `.env`.
5.  **Migrações:** Execute `python manage.py makemigrations` e `python manage.py migrate` para sincronizar o schema de todos os apps.
6.  **Análise Estrutural e de Código:** Analise a estrutura geral do projeto (`core`, `apps/`) em busca de melhorias de organização, modularidade e aderência às boas práticas. **Solicite confirmação explícita do usuário antes de aplicar quaisquer mudanças estruturais significativas.**
7.  **Atualização de Dependências (Com Cautela):** Verifique se existem versões mais recentes e estáveis para os pacotes em `requirements.txt`. **Esteja ciente de que exceções e versões fixas podem ser definidas nos `GEMINI.md` específicos de cada app.** Analise changelogs para breaking changes antes de propor atualizações.

#### 2.3. Ao executar (`testes`)

O comando `testes` deve realizar verificações abrangentes em **todo o projeto**.

1.  **Execução de Testes Abrangentes (Pytest com Cobertura):**
    * **Ação:** `pytest --cov=core --cov=apps --cov-report=html`
    * **Relato:** Forneça um resumo dos resultados e informe que o relatório de cobertura detalhado de todo o projeto está em `htmlcov/index.html`.
2.  **Verificação de Qualidade de Código (Ruff):**
    * **Ação:** `ruff check .` e, se necessário, `ruff check . --fix`.
3.  **Verificação de Tipos (Pyright):**
    * **Ação:** `pyright`

#### 2.4. Análise de Arquivos
*   **Análise Interna:** Ao ser solicitado para ler ou analisar arquivos, o conteúdo não deve ser exibido na resposta. A análise deve ser feita internamente para guiar as ações subsequentes, a menos que a exibição do conteúdo seja explicitamente solicitada pelo usuário.

---

### 3. Contexto Técnico Geral

#### 3.1. Tecnologias Principais

| Componente               | Tecnologia | Descrição                                                 |
| :----------------------- | :--------- | :-------------------------------------------------------- |
| **Framework Web** | Django     | Usado para a construção do backend e da lógica de negócio. |
| **Linguagem** | Python     | Linguagem principal do projeto.                           |
| **Banco de Dados Principal** | (A definir) | SGBD será configurado conforme a necessidade do projeto.        |
| **Gerenciador de Pacotes** | `uv`       | Ferramenta para gerenciamento de pacotes e ambientes.     |

#### 3.2. Ambiente e Dependências (`uv` e `.env`)

* **Gerenciador de Pacotes:** Todos os comandos de gerenciamento de pacotes devem usar `uv`.
* **Adicionar nova dependência:** `uv add <nome-do-pacote>`. Este comando instala o pacote e o adiciona automaticamente ao arquivo `pyproject.toml`. **É o único método permitido para adicionar novas dependências.**
* **Gerenciamento de Credenciais (`.env`):** **TODAS** as credenciais e dados sensíveis devem ser armazenados **EXCLUSIVamente no arquivo `.env`** na raiz do projeto e acessados via `python-decouple`.

#### 3.3. Estrutura do Projeto Django

* **Configurações (`core/settings.py`):** Arquivo de configuração central. Dados sensíveis **NUNCA** devem ser codificados diretamente aqui.
* **URLs (`core/urls.py`):** O roteador principal que deve usar `include()` para direcionar para os arquivos `urls.py` de cada app dentro do diretório `apps/`.
* **Padrões de Qualidade e Segurança:**
    * **Estilo:** PEP 8 (use `ruff` para formatar/verificar).
    * **Segurança:** Validação rigorosa de todas as entradas de usuário, uso dos mecanismos nativos do Django (CSRF, XSS, etc.).
    * **Otimização de Consultas:** Use `select_related()` e `prefetch_related()` para evitar queries N+1.

---

### 4. Fluxo de Trabalho e Automação (Git)

* **Contextualização Contínua:** No início de cada interação, leia e interprete o arquivo `progress.md`.
* **Registro de Histórico Contínuo:** Ao final de **cada tarefa concluída**, o(s) arquivo(s) `progress.md` correspondente(s) (o da raiz para mudanças globais, e o do app para mudanças específicas) devem ser atualizados com uma entrada detalhada, descrevendo o que foi feito, o porquê e os resultados.
* **Manutenção do `.gitignore`:** Verifique se o `.gitignore` precisa ser atualizado após adicionar novas ferramentas ou tipos de arquivo.
* **Commits Detalhados:** Ao preparar um commit, a mensagem deve ser um resumo detalhado de **todo o processo realizado** desde o último commit. Ela deve explicar o "porquê" das mudanças, não apenas o "o quê".
* **Push Completo e Seguro:**
    1.  **Sincronizar:** Sempre execute `git pull --rebase` antes de fazer o push para integrar as mudanças remotas.
    2.  **Verificar Status:** Use `git status` para garantir que todos os arquivos relevantes (novos ou modificados) estão na área de stage.
    3.  **Executar Push:** Execute `git push`.
    4.  **Tratamento de Falhas:** **PARE** e avise o usuário imediatamente em caso de qualquer falha (ex: `merge conflict`, `push rejected`).

---

### 5. Comandos Rápidos do Projeto

* **Iniciar o servidor:** `python manage.py runserver`
* **Criar novas migrações:** `python manage.py makemigrations [nome_do_app]`
* **Aplicar migrações:** `python manage.py migrate`
* **Executar testes (geral):** `pytest`
* **Executar testes (app específico):** `pytest apps/[nome_do_app]/`
* **Instalar dependências do projeto:** `uv pip install -r requirements.txt`
* **Adicionar nova dependência:** `uv add <nome-do-pacote>`
* **Sincronizar dependências (após edições manuais em `requirements.txt`):** `uv pip sync`