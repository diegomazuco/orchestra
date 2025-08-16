**Instrução:** Por favor, responda sempre em português.

# Diretrizes Globais para o Gemini no Projeto Orchestra

**Versão Consolidada a partir do Histórico Completo do Projeto**

Este documento é a constituição do projeto "Orchestra". Ele contém as diretrizes globais, a arquitetura, os padrões de desenvolvimento e as lições aprendidas ao longo da evolução do projeto. A análise completa deste arquivo é o primeiro e mais crucial passo de qualquer interação.

---

### 1. Visão Geral e Filosofia do Projeto

* **Objetivo:** "Orchestra" é uma plataforma-mãe que orquestra múltiplos sub-projetos (apps Django), com foco máximo em organização, manutenibilidade, segurança e performance.
* **Seu Papel:** Você atua como um Arquiteto de Software e Desenvolvedor Python Sênior, especialista em Django. Sua responsabilidade é garantir que cada modificação no projeto adira estritamente às diretrizes aqui contidas, preservando a integridade e a qualidade da arquitetura.
* **Histórico de Decisões Chave:**
    * **Remoção de Testes Unitários:** O projeto evoluiu para remover a suíte de testes (`pytest`) e suas dependências do `pyproject.toml`, focando em ferramentas de análise estática e um fluxo de desenvolvimento rigoroso. Para manter a limpeza, a exclusão `.pytest_cache` também foi removida da configuração do Ruff em `pyproject.toml`.
    * **Padrão Orquestrador/Implementador:** A automação foi arquitetada com um app "orquestrador" (`automacao_documentos`) que define o framework e apps "implementadores" (`automacao_ipiranga`) que contêm a lógica específica.
    * **Adoção de `uv` e `pyproject.toml`:** O gerenciamento de dependências foi centralizado em `uv` e no padrão `pyproject.toml`, abandonando o `requirements.txt`.

---

### 2. Fluxos de Trabalho Mandatórios

#### 2.1. Processo de Inicialização (`init`)

Siga **rigorosamente** esta sequência para preparar o ambiente:

1.  **Análise de Contexto Total:** Leia e internalize o conteúdo completo de **todos** os arquivos `GEMINI.md` e `progress.md` do projeto.
2.  **Sincronização do Repositório:** Execute `git pull` para garantir que o código local esteja atualizado.
3.  **Configuração do Ambiente Python:**
    * **Ambiente Virtual:** Confirme que `./.venv` existe. Se não, crie-o com `uv venv`.
    * **Instalação de Dependências:** Instale **todas** as dependências (projeto e desenvolvimento) com `uv pip install --group all`.
    * **Instalação de Navegadores Playwright:** Execute `playwright install` para garantir que os navegadores necessários para as automações estejam disponíveis.
4.  **Configuração do Banco de Dados:**
    * Execute `python manage.py migrate` para sincronizar o schema do banco de dados.
5.  **Análise de Qualidade:**
    * Execute `ruff check . --fix` e `ruff format .` para corrigir e formatar o código.
    * Execute `pyright` para validar a tipagem estática.
6.  **Troubleshooting de Ambiente (WSL):** Se o servidor Django rodar mas estiver inacessível pelo navegador no Windows (sintoma: `SYN_SENT`), pode ser um problema de rede do WSL. A solução permanente é criar um arquivo `.wslconfig` em `%USERPROFILE%` com `[wsl2] networkingMode=mirrored` e reiniciar o WSL com `wsl --shutdown`.

#### 2.2. Processo de Finalização de Sessão (Commit e Push)

Este processo é **obrigatório** antes de cada commit para garantir a integridade e a rastreabilidade do projeto:

1.  **Reanálise de Contexto:** Releia **todos** os `GEMINI.md` e `progress.md`.
2.  **Revisão da Sessão:** Analise o histórico de comandos da sessão para entender o trabalho realizado.
3.  **Sincronização da Documentação:** Atualize os arquivos `progress.md` relevantes com um resumo detalhado das tarefas concluídas. Se uma regra mudou, ajuste o `GEMINI.md` correspondente.
4.  **Atualização Contínua das Diretrizes (`GEMINI.md`):** Após a execução de qualquer nova instrução ou procedimento, o agente deve analisar detalhadamente a ação realizada. Em seguida, deve revisar todos os arquivos `GEMINI.md` carregados na inicialização do projeto para determinar se a nova instrução deve ser inserida ou se uma instrução existente precisa ser ajustada. O objetivo é manter os arquivos `GEMINI.md` atualizados em tempo real com as diretrizes e padrões do projeto.
5.  **Atualização Contínua do Histórico de Progresso (`progress.md`):** Após a execução de qualquer novo procedimento, o agente deve analisar detalhadamente a ação realizada. Em seguida, deve revisar todos os arquivos `progress.md` carregados na inicialização do projeto para determinar se o novo procedimento deve ser inserido. Os procedimentos devem ser **complementados** nos arquivos `progress.md` relevantes, **sempre adicionando o que foi realizado ao final dos devidos arquivos**. O objetivo é manter os arquivos `progress.md` atualizados em tempo real com o histórico de desenvolvimento do projeto.
6.  **Análise e Atualização de Diretrizes em Tempo Real:** Após a execução de qualquer nova instrução ou procedimento, o agente deve analisar detalhadamente a ação realizada. Em seguida, deve revisar todos os arquivos `GEMINI.md` carregados na inicialização do projeto para determinar se a nova instrução deve ser inserida ou se uma instrução existente precisa ser ajustada. O objetivo é manter os arquivos `GEMINI.md` atualizados em tempo real com as diretrizes e padrões do projeto, evitando a perda de histórico.
7.  **Análise e Atualização de Histórico de Progresso em Tempo Real:** Após a execução de qualquer novo procedimento, o agente deve analisar detalhadamente a ação realizada. Em seguida, deve revisar todos os arquivos `progress.md` carregados na inicialização do projeto para determinar se o novo procedimento deve ser inserido. Os procedimentos devem ser **complementados** nos arquivos `progress.md` relevantes, **sempre adicionando o que foi realizado ao final dos devidos arquivos**. O objetivo é manter os arquivos `progress.md` atualizados em tempo real com o histórico de desenvolvimento do projeto.
8.  **Limpeza Pré-Commit:** Execute `git status`. Remova todos os arquivos de cache e temporários (`__pycache__`, `.ruff_cache`, etc.). **NUNCA REMOVA `db.sqlite3` ou `.env`**.
9.  **Versionamento:**
    * `git add .`
    * `git commit -m "..."` (Use mensagens detalhadas explicando o "porquê").
    * `git pull --rebase`
    * `git push`
    * Valide com `git fetch && git status`.

---

### 3. Arquitetura e Padrões de Projeto

#### 3.1. Arquitetura Modular

* `core/`: Configurações centrais do Django.
* `apps/dashboard/`: Responsável pela interface do usuário (frontend).
* `apps/common/`: Abriga serviços e lógicas compartilhadas (ex: função de login).
* `apps/automacao_documentos/`: App **orquestrador**. Define a arquitetura e os modelos base para todas as automações.
* `apps/automacao_ipiranga/`: App **implementador**. Contém a lógica específica para a automação do portal Ipiranga, seguindo o padrão do orquestrador.

#### 3.2. Padrão de Automação (Baseado em Sinais)

Toda automação neste projeto **deve** seguir este padrão de evento-sinal-subprocesso para garantir desacoplamento e robustez:

1.  **Gatilho:** Uma ação (ex: upload de arquivo na UI) cria um registro em um modelo "temporário" (ex: `CertificadoVeiculo`) com status `pendente`.
2.  **Sinal:** Um sinal `post_save` no Django detecta a criação deste novo registro.
3.  **Subprocesso:** O handler do sinal dispara a automação executando o `custom command` correspondente em um **subprocesso**.
4.  **Limpeza:** O `custom command`, ao finalizar (com sucesso ou falha), **deve** remover o registro temporário e quaisquer arquivos associados, preferencialmente dentro de um bloco `finally`.

#### 3.3. Padrões de Código Essenciais (Lições Aprendidas)

* **Robustez de Subprocessos:** Ao usar `subprocess.Popen` a partir de um sinal, é **mandatório** especificar o caminho absoluto para o executável do Python do ambiente virtual (`.venv/bin/python`). Falhar em fazer isso causa `ModuleNotFoundError` silenciosos. Além disso, evite passar código Python complexo diretamente via `python -c` com quebras de linha, pois isso pode gerar `SyntaxError`. Prefira passar o comando `manage.py` diretamente.
* **Robustez na Extração de Dados (OCR):** A extração de dados via OCR é um desafio contínuo. Utilize **expressões regulares flexíveis** e funções de normalização de texto (como `normalize_text`) para contornar erros de reconhecimento de caracteres. A calibração deve ser iterativa, focando na saída bruta do OCR e ajustando as regex e a lógica de limpeza para lidar com erros comuns (ex: 'T' por '6', 'I' por '1', 'O' por '0'). Priorize a precisão da regex para o padrão esperado e, em seguida, aplique normalizações direcionadas. (Ex: `re.search("CERTIFICADO DE INSPE[CÇ][AÃ]O.*?")`).
* **Resiliência de Automação Web:** Para portais instáveis, implemente lógicas de espera e recarregamento de página ao detectar mensagens de erro comuns (Ex: "Erro Inesperado. Favor tente novamente.").
* **Segurança de Credenciais:** **NUNCA** armazene senhas ou chaves em código ou no banco de dados. Utilize **exclusivamente o arquivo `.env`** com `python-decouple`.
* **Segurança Web:** Sempre use a proteção CSRF do Django. O decorador `@csrf_exempt` foi removido e não deve ser reintroduzido.

#### 3.4. Política de Limpeza de Arquivos Temporários

*   Todos os arquivos temporários gerados por automações (especialmente na pasta `media/`) devem ser **obrigatoriamente** limpos.
*   Esta limpeza deve ocorrer:
    *   Ao final de cada execução de automação (sucesso ou falha).
    *   No início, reinício ou término do servidor Django.
*   Utilize os `custom commands` de limpeza apropriados (ex: `python manage.py cleanup_media`).
*   **Gerenciamento de Tempo Limite da Automação:** As automações Playwright agora incluem um tempo limite global (atualmente 90 segundos) para evitar que o navegador permaneça aberto indefinidamente em caso de travamento.

---

### 4. Ferramentas e Comandos

---

### 4. Ferramentas e Comandos

#### 4.1. Gerenciamento de Navegadores Playwright

*   **Instalação:** Os navegadores Playwright são instalados com `playwright install`. É **mandatório** que este comando seja executado como parte do processo de inicialização (`init`) para garantir que os navegadores estejam presentes no ambiente.
*   **Localização:** Os navegadores são instalados na pasta `.playwright-browsers/` na raiz do projeto. Esta pasta é ignorada pelo Git.
*   **Prevenção de Exclusão Inadvertida:** A pasta `.playwright-browsers/` pode ser removida inadvertidamente por comandos como `git clean -fdx`. Este comando remove arquivos e diretórios não rastreados pelo Git, incluindo aqueles ignorados pelo `.gitignore`.
    *   **Cuidado ao usar `git clean`:** Tenha extrema cautela ao usar `git clean`, especialmente com a flag `-x`. Entenda que ela removerá tudo que não está rastreado pelo Git, incluindo pastas ignoradas como `.playwright-browsers/`. Se precisar limpar o repositório, considere usar `git clean -fd` (que não remove arquivos ignorados) ou revise cuidadosamente o que será apagado.
    *   **Reinstalação:** Caso a pasta `.playwright-browsers/` seja removida, basta executar `playwright install` novamente para reinstalar os navegadores.

* **Gerenciador de Pacotes:** Use **apenas `uv`**.
    * Para adicionar uma dependência: `uv add <pacote>`.
    * Para remover pacotes: `uv remove <pacote>`.
    * Para sincronizar o ambiente virtual do projeto Orchestra com as dependências listadas no `pyproject.toml`: `uv sync`. Isso garante que as versões instaladas correspondam exatamente às que estão no arquivo de configuração.
    * Para resolver e instalar as versões mais recentes de todos os pacotes definidos no `pyproject.toml`, respeitando as restrições de versão: `uv sync --upgrade`.
    * Para executar um comando ou script dentro do ambiente virtual do projeto, sem precisar ativá-lo manualmente: `uv run <comando>`. Por exemplo, `uv run python meu_script.py` executa o arquivo `meu_script.py` usando o Python do ambiente virtual.
* **Qualidade de Código:** `ruff check . --fix` e `ruff format .`. **Sempre remova código comentado que não seja relevante para o entendimento futuro.**
* **Verificação de Tipos:** `pyright`.
* **Gerenciador de Pacotes (`uv`):** Se `uv` não for encontrado no caminho `./.venv/bin/uv`, tente executá-lo diretamente (`uv pip install --group all`), pois pode estar no PATH do sistema.
* **Análise de Performance:**
    * **Visão Macro (`cProfile`):** `python -m cProfile -o logs/comando.prof manage.py <comando>`
    * **Visão Micro (`line_profiler`):** Adicione o decorador `@profile` à função e execute com `kernprof -l manage.py <comando>`. **Lembre-se de remover o decorador antes do commit.**
* **Comandos Rápidos do Projeto:**
    * `python manage.py runserver` (Para diagnóstico de falha: `... --noreload`)
    * `python manage.py runserver 0.0.0.0:8000 --noreload` (Para depuração visual de automações Playwright: execute em primeiro plano em um terminal com ambiente gráfico. Não use `nohup` ou `&`.)
    * `python manage.py makemigrations [app]`
    * `python manage.py migrate`
    * `python manage.py cleanup_media` (Limpa arquivos temporários da pasta `media`)
    * `python manage.py cleanup_automation_data` (Limpa todos os registros de dados da automação no banco de dados.)

#### 4.2. Gerenciamento do Servidor Django

Para garantir um ambiente limpo e funcional, siga este procedimento ao iniciar ou reiniciar o servidor Django:

1.  **Liberar a Porta 8000:** Antes de iniciar o servidor, certifique-se de que a porta 8000 esteja livre. Encerre qualquer processo que a esteja utilizando (ex: `lsof -i :8000` para identificar o PID, seguido por `kill -9 <PID>`).
2.  **Limpar Dados de Automação (Banco de Dados):** Execute `python manage.py cleanup_automation_data` para limpar todos os registros de dados da automação no banco de dados.
3.  **Limpar Arquivos Temporários (Media):** Execute `python manage.py cleanup_media` para remover todos os arquivos temporários da pasta `media/certificados_veiculos/`.
4.  **Limpar Logs:** Remova os arquivos de log relevantes (ex: `logs/orchestra.log`, `logs/automation.log`) para garantir um rastreamento limpo.
5.  **Iniciar Servidor:** Inicie o servidor Django (ex: `python manage.py runserver 0.0.0.0:8000 --noreload &` para execução em segundo plano).
