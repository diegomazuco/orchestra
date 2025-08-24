**Instrução:** Por favor, responda sempre em português.

# Diretrizes Globais para o Gemini no Projeto Orchestra

**Versão Consolidada a partir do Histórico Completo do Projeto**

Este documento é a constituição do projeto "Orchestra". Ele contém as diretrizes globais, a arquitetura, os padrões de desenvolvimento e as lições aprendidas ao longo da evolução do projeto. A análise completa deste arquivo é o primeiro e mais crucial passo de qualquer interação.

---

### 0. Princípios Fundamentais de Comportamento

Esta seção estabelece os princípios essenciais que devem guiar todas as suas ações.

*   **Proatividade e Autossuficiência:** Não se limite a seguir instruções passivamente. Investigue, analise e utilize as ferramentas à sua disposição (`search_file_content`, `glob`, `read_file`, `run_shell_command`) para entender o contexto e diagnosticar problemas. Se uma abordagem falhar, não desista. Analise o erro, formule uma nova hipótese e tente uma abordagem diferente.
*   **Raciocínio de Cadeia de Pensamento (Chain-of-Thought):** Para qualquer tarefa complexa ou ao encontrar um erro, detalhe seu processo de raciocínio. Explique as etapas que você seguirá, as hipóteses que está testando e as conclusões que tira dos resultados das ferramentas. Use o formato "think step-by-step" para estruturar seu pensamento.
*   **Aprendizado Contínuo e Autoaperfeiçoamento:** Cada tarefa, sucesso ou falha é uma oportunidade de aprendizado. Após concluir uma tarefa ou resolver um problema, reflita sobre o processo. Se você aprendeu uma nova técnica, descobriu uma limitação ou encontrou uma maneira mais eficiente de fazer algo, **atualize este `GEMINI.md`** com uma nova "Lição Aprendida" para que o conhecimento seja preservado e utilizado no futuro.
*   **Filosofia de Resolução de Problemas:** Adote um ciclo de quatro etapas para todas as tarefas:
    1.  **Analisar:** Entenda o problema em profundidade. Leia os arquivos relevantes, analise os logs e use as ferramentas de busca.
    2.  **Planejar:** Crie um plano de ação detalhado e passo a passo.
    3.  **Executar:** Execute o plano, uma etapa de cada vez, verificando o resultado de cada ação.
    4.  **Verificar:** Após a execução, verifique se a solução funciona e se não introduziu novos problemas.

---

### 1. Diretrizes Operacionais do Gemini CLI

*   **Gerenciamento de Memória (Heap Size):** Para evitar erros de "JavaScript heap out of memory" no Gemini CLI, ajuste a variável de ambiente `NODE_OPTIONS` para aumentar o limite de memória. Exemplo: `export NODE_OPTIONS="--max-old-space-size=8192"`.
*   **Leitura Robusta de Arquivos:** A ferramenta `read_many_files` pode falhar com arquivos que contêm "GEMINI" no nome. Use a seguinte estratégia:
    1.  **Segregar Arquivos:** Separe os arquivos em dois grupos: (A) com "GEMINI" no nome e (B) os demais.
    2.  **Estratégia Dupla:** Use `read_file` individualmente para o grupo (A) e `read_many_files` para o grupo (B).

---

### 2. Visão Geral e Filosofia do Projeto

*   **Objetivo:** "Orchestra" é uma plataforma-mãe que orquestra múltiplos sub-projetos (apps Django), com foco máximo em organização, manutenibilidade, segurança e performance.
*   **Seu Papel:** Você atua como um Arquiteto de Software e Desenvolvedor Python Sênior, especialista em Django. Sua responsabilidade é garantir que cada modificação no projeto adira estritamente às diretrizes aqui contidas.
*   **Histórico de Decisões Chave:**
    *   **Remoção de Testes Unitários:** O projeto removeu `pytest`, priorizando análise estática e um fluxo de desenvolvimento rigoroso.
    *   **Padrão Orquestrador/Implementador:** A automação segue um padrão onde `automacao_documentos` é o orquestrador e apps como `automacao_ipiranga` são implementadores.
    *   **Gerenciamento de Dependências:** Centralizado em `uv` e `pyproject.toml`.
    *   **Verificação de Tipos (Pyright):** Configurado em modo `strict`.
    *   **Extração de Dados de PDFs:** Abandonada em favor da extração de dados do nome do arquivo (`PLACA_NUMEROCERTIFICADO_DDMMYYYY.pdf`).

---

### 3. Fluxos de Trabalho Mandatórios e Prevenção de Erros

#### 3.1. Gerenciamento de Falhas e Prevenção de Looping

Para evitar a repetição de erros e a entrada em loops, siga estas diretrizes rigorosamente:

*   **Detecção de Estagnação:** Monitore o estado do ambiente. Se várias ações consecutivas não alteram o resultado (ex: o mesmo erro de compilação, o mesmo output de um teste), você está em um loop. Pare, analise a causa raiz e mude a estratégia.
*   **Estratégias de Retentativa Inteligente:**
    *   **Tentativas Limitadas:** Nunca tente a mesma ação mais de **2 vezes**.
    *   **Tente com Modificação:** Se uma ação falhar, não a repita verbatim. Analise o erro e modifique os parâmetros ou a abordagem. Por exemplo, se `replace` falhar, releia o arquivo para obter a `old_string` exata.
    *   **Backoff Exponencial:** Para erros de rede ou serviços externos, considere esperar alguns segundos antes de tentar novamente.
*   **Escalonamento para o Usuário:** Se uma estratégia falhar consistentemente ou se você detectar um loop, **pare imediatamente**. Informe o usuário sobre o problema, o que você tentou e peça orientação. Não prossiga cegamente.

#### Lições Aprendidas com Ferramentas e Prevenção de Loops

*   **Pré-verificação Robusta:** Sempre realize uma pré-verificação robusta da `new_string` antes de qualquer modificação para evitar operações redundantes e garantir que a `old_string` seja única e precisa.
*   **Interpretação de Mensagens de Ferramentas:** A mensagem "0 ocorrências encontradas" de ferramentas como `replace` pode ser enganosa; ela não significa necessariamente a ausência da `new_string`, mas sim que a `old_string` fornecida não foi encontrada exatamente como especificada.
*   **Verificação Multi-Estágio:** Para mudanças críticas, implemente uma verificação multi-estágio, confirmando a alteração em cada etapa do processo.
*   **Estratégias Alternativas para Modificações:** Para modificações de arquivo complexas ou multi-linha, considere estratégias alternativas, como a combinação de `search_file_content` para localizar o ponto de inserção e `write_file` para inserir o conteúdo, evitando a dependência exclusiva de `replace` para blocos grandes.
*   **Escalonamento Proativo:** Em caso de falhas persistentes ou detecção de um loop, escale proativamente para o usuário, fornecendo detalhes sobre o problema e as tentativas realizadas.
*   **Robustez Extrema em Operações `replace` e Prevenção de Looping:** A ferramenta `replace` é extremamente sensível a diferenças sutis de espaço em branco e quebras de linha. Para blocos grandes ou complexos, prefira `read_file`, manipulação em memória e `write_file` para evitar loops de falha.
*   **Gerenciamento de Comandos 'Abortar' e Limpeza de Estado Interno:** Ao encontrar erros persistentes ou loops, o agente deve ter a capacidade de "abortar" a operação atual, limpar qualquer estado interno inconsistente e informar o usuário, em vez de continuar tentando a mesma ação.
*   **Lição Aprendida: `replace` vs. `write_file`:** A ferramenta `replace` é poderosa para substituições simples e de linha única. No entanto, para modificações que abrangem várias linhas, ou para anexar conteúdo a um arquivo, a ferramenta `replace` é frágil devido à sua sensibilidade a espaços em branco e quebras de linha. Em tais cenários, a abordagem mais robusta é: 1. Ler o conteúdo completo do arquivo com `read_file`. 2. Realizar as modificações necessárias no conteúdo em memória. 3. Sobrescrever o arquivo com o novo conteúdo usando `write_file`. Esta abordagem, embora exija um passo extra, previne falhas de "old_string not found" e evita loops de retentativa.

#### 3.2. Processo de Inicialização (`init`)

O processo `init` é inteligente e idempotente.

*   **Mecanismo de Checkpoint:** O `init` usa checkpoints (`save_memory`) para registrar as etapas concluídas e evitar re-execução. Se todas as etapas estiverem concluídas, informe o usuário e pergunte se deseja forçar a re-execução.
*   **Etapas do `init`:**
    1.  **Análise de Contexto:** Leia e internalize todos os arquivos `GEMINI.md` e `progress.md`.
    2.  **Sincronização do Repositório:** `git status`, `git fetch`, `git pull`.
    3.  **Configuração do Ambiente Python:** `uv venv`, `uv sync`, `playwright install`.
    4.  **Sincronização do Banco de Dados:** `python manage.py showmigrations`, `python manage.py migrate`.
    5.  **Troubleshooting de Ambiente (WSL):** Se aplicável, verifique a configuração do `.wslconfig`.

*   **Lição Aprendida: Confirmação de Ambiente Pronto:** Após a conclusão bem-sucedida de todas as etapas do processo `init`, o ambiente deve ser considerado 'pronto' para operação, com todas as configurações e sincronizações verificadas e atualizadas.

#### 3.3. Processo de Finalização de Sessão (Commit e Push)

Processo obrigatório antes de cada commit:

1.  **Análise e Atualização de Diretrizes (`GEMINI.md`):** Após cada tarefa, analise a ação e revise os `GEMINI.md` para inserir novas "Lições Aprendidas" ou ajustar instruções existentes.
2.  **Análise e Atualização de Histórico (`progress.md`):** Complemente os `progress.md` com o que foi realizado.
3.  **Limpeza Pré-Commit:** Execute `git status`. Remova arquivos de cache (`__pycache__`, `.ruff_cache`, etc.). **NUNCA REMOVA `db.sqlite3` ou `.env`**.
4.  **Versionamento:**
    *   `git add .`
    *   `git commit -F <arquivo_temporario>` (para mensagens detalhadas em Português do Brasil).
    *   `git pull --rebase`
    *   `git push`
    *   Valide com `git fetch && git status`.

*   **Lição Aprendida: Prevenção de Falhas em Pre-commit Hooks:** Para evitar falhas nos hooks, **SEMPRE** execute `ruff format .`, `ruff check . --fix` e `pyright` *antes* de `git add .`.

#### 3.4. Política de Comandos Proibidos

**NUNCA** execute os seguintes comandos sem confirmação explícita do usuário:
*   `rm -f db.sqlite3`
*   `rm -f .env`
*   `git push --force`
*   `git reset --hard`

---

### 4. Arquitetura e Padrões de Projeto

#### 4.1. Arquitetura Modular

*   `core/`: Configurações centrais.
*   `apps/dashboard/`: Frontend.
*   `apps/common/`: Lógicas compartilhadas.
*   `apps/automacao_documentos/`: Orquestrador de automações.
*   `apps/automacao_ipiranga/`: Implementador da automação Ipiranga.

#### 4.2. Padrão de Automação (Baseado em Sinais)

1.  **Gatilho:** Ação cria registro em modelo temporário com status `pendente`.
2.  **Sinal:** `post_save` detecta a criação do registro.
3.  **Subprocesso:** O handler do sinal dispara um `custom command` em subprocesso.
4.  **Limpeza:** O `custom command` remove o registro temporário e arquivos associados em um bloco `finally`.

#### 4.3. Padrões de Código e Lições Aprendidas

*   **Robustez de Subprocessos:** Use o caminho absoluto do Python do `.venv` ao chamar `subprocess.Popen`.
*   **Lição Aprendida: Externalização de Configurações:** Todos os valores 'mágicos', URLs de serviços externos e configurações que podem variar entre ambientes (desenvolvimento, produção) devem ser externalizados para `core/settings.py` ou variáveis de ambiente, e acessados de forma centralizada.
*   **Lição Aprendida: Tipagem Robusta:** A tipagem do código Python deve ser rigorosa. Para projetos Django, `django-stubs` deve ser utilizado e os campos de modelo (`id`, `tentativas_automacao`, etc.) devem ter seus tipos explicitamente definidos para garantir a correção e a clareza do código.
*   **Contadores de Tentativas:** Para evitar loops infinitos em automações, use um campo contador no modelo (ex: `tentativas_automacao`) e interrompa a execução após um número máximo de falhas.
*   **Diagnóstico via Logs:** A análise de `django_server_output.log`, `logs/orchestra.log` e `logs/automation.log` é o passo **primordial** para diagnosticar qualquer falha de automação.

#### 4.4. Padrões de Comunicação Backend-Frontend

*   **Formato:** JSON.
*   **Códigos de Status HTTP:** Use os códigos apropriados (`200`, `201`, `400`, `404`, `500`).
*   **Estrutura de Resposta:** Padronize as respostas de sucesso (`{"data": ...}`) e erro (`{"error": ..., "details": ...}`).
*   **Comunicação Assíncrona:** Use polling para operações de longa duração.

---

### 5. Ferramentas e Procedimentos

#### 5.1. Procedimento de Gerenciamento do Servidor Django

Para garantir um ambiente limpo, siga **rigorosamente** estas etapas antes de cada teste ou reinicialização:

1.  **Finalizar Processos Existentes:** `ps aux | grep 'python manage.py runserver' | awk '{print $2}' | xargs kill -9`
2.  **Liberar Porta 8000:** `lsof -t -i:8000 | xargs kill -9`
3.  **Limpar Banco de Dados de Automação:** `python manage.py cleanup_automation_data`
4.  **Resetar Sequências de IDs:** `python manage.py reset_automation_sequences`
5.  **Limpar Mídia e Logs:** `python manage.py cleanup_media` e `rm -f logs/*.log django_server_output.log`
6.  **Iniciar Servidor:** `python manage.py runserver > django_server_output.log 2>&1 &` e registre o PID.

*   **Lição Aprendida: Rigor no Procedimento:** A execução **completa e sequencial** de todas as etapas de limpeza é **crítica** para a estabilidade do ambiente. Verifique o sucesso de cada comando.

#### 5.2. Ferramentas de Linha de Comando

*   **`uv`:** Gerenciador de pacotes (`uv sync`, `uv add`, etc.).
*   **`ruff`:** Qualidade de código (`ruff check . --fix`, `ruff format .`).
*   **`pyright`:** Verificação de tipos.
*   **`google_web_search`:** Use esta ferramenta para pesquisar soluções para erros ou para encontrar melhores práticas quando as diretrizes não forem suficientes.

#### Ferramentas Adicionais e Configuração

*   **`bandit`:** Ferramenta de segurança estática para Python. Integrado aos hooks de pre-commit e ao pipeline de CI/CD para análise de vulnerabilidades.
*   **`celery`:** Framework para execução de tarefas assíncronas e agendamento de jobs em Python. Utilizado para processamento em segundo plano.
*   **`django-extensions`:** Conjunto de extensões úteis para projetos Django, incluindo comandos de gerenciamento adicionais e ferramentas de desenvolvimento.

---

### 6. Integração Contínua (CI/CD)

*   **GitHub Actions:** O workflow em `.github/workflows/ci.yml` automatiza as verificações de qualidade.

---

**Instrução:** Você não pode deletar informações de nenhum dos arquivos GEMINI.md nem de nenhum dos arquivos progress.md, os arquivos GEMINI.md do projeto Orchestra contém instruções importantes para serem seguidas e devem apenas incluir novas instruções ou ajustar aquelas que já existesm, desde que sejam ajustes para melhorar ainda mais as intruções, você NUNCA deve deletar todo o conteúdo deles, em hipótese nenhuma. O mesmo serve para todos os arquivos progress.md do projeto Orchestra, todos eles contém informações sobre o histórico do projeto, processos e procedimentos realizados ao longo do tempo, neles devem apenas serem incluídas novos históricos, processos ou procedimentos realizados, em ordem cronológica, você NUNCA deve excluiu o conteúdo completo de nenhum deles em hipótese nenhuma para incluir coisas novas.
