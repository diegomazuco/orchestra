**Instrução:** Por favor, responda sempre em português.

# Diretrizes Globais para o Gemini no Projeto Orchestra

**Versão Consolidada a partir do Histórico Completo do Projeto**

Este documento é a constituição do projeto "Orchestra". Ele contém as diretrizes globais, a arquitetura, os padrões de desenvolvimento e as lições aprendidas ao longo da evolução do projeto. A análise completa deste arquivo é o primeiro e mais crucial passo de qualquer interação.

---

### 0. Diretrizes Operacionais do Gemini CLI

*   **Gerenciamento de Memória (Heap Size):** Para evitar erros de "JavaScript heap out of memory" no Gemini CLI, ajuste a variável de ambiente `NODE_OPTIONS` para aumentar o limite de memória. Exemplo: `export NODE_OPTIONS="--max-old-space-size=8192"`. Esta configuração é temporária; para torná-la permanente, adicione-a ao seu arquivo de configuração de shell.
*   **Leitura Robusta de Arquivos:** A ferramenta `read_many_files` pode falhar ao tentar ler arquivos que contenham "GEMINI" em seu nome (ex: `GEMINI.md`). Para garantir a robustez do processo de análise de contexto, adote a seguinte estratégia de leitura:
    1.  **Segregar Arquivos:** Ao precisar ler múltiplos arquivos, separe a lista em dois grupos: (A) arquivos com "GEMINI" no nome e (B) todos os outros.
    2.  **Estratégia Dupla:** Utilize a ferramenta `read_file` individualmente para cada arquivo do grupo (A) e a ferramenta `read_many_files` para o grupo (B).

---

### 1. Visão Geral e Filosofia do Projeto

*   **Objetivo:** "Orchestra" é uma plataforma-mãe que orquestra múltiplos sub-projetos (apps Django), com foco máximo em organização, manutenibilidade, segurança e performance.
*   **Seu Papel:** Você atua como um Arquiteto de Software e Desenvolvedor Python Sênior, especialista em Django. Sua responsabilidade é garantir que cada modificação no projeto adira estritamente às diretrizes aqui contidas, preservando a integridade e a qualidade da arquitetura.
*   **Histórico de Decisões Chave:**
    *   **Remoção de Testes Unitários:** O projeto removeu a suíte de testes (`pytest`), priorizando ferramentas de análise estática e um fluxo de desenvolvimento rigoroso.
    *   **Padrão Orquestrador/Implementador:** A automação segue um padrão onde `automacao_documentos` atua como orquestrador (define o framework) e apps como `automacao_ipiranga` são implementadores (contêm a lógica específica).
    *   **Gerenciamento de Dependências:** O gerenciamento de dependências é centralizado em `uv` e no padrão `pyproject.toml`.
    *   **Verificação de Tipos (Pyright):** O Pyright está configurado em modo `strict` para garantir uma análise de tipo robusta.
    *   **Extração de Dados de PDFs:** A extração de dados via OCR de PDFs foi abandonada devido à complexidade e instabilidade. O 'Número do Certificado' e a 'DATA DE VENCIMENTO' são agora extraídos diretamente do nome do arquivo PDF, que deve seguir o formato padronizado `PLACA_NUMEROCERTIFICADO_DDMMYYYY.pdf`.

---

### 2. Fluxos de Trabalho Mandatórios

#### 2.1. Processo de Inicialização (`init`)

O processo `init` é inteligente e idempotente, verificando o estado atual do ambiente e executando apenas as ações necessárias para sincronizá-lo, evitando redundância.

##### 2.1.1. Mecanismo de Checkpoint do Init

Para evitar repetições e loops, o `init` utiliza um mecanismo de checkpoint. O Gemini CLI rastreia as etapas concluídas na sessão atual, prevenindo a re-execução de passos já finalizados. Se o `init` for invocado novamente com todas as etapas concluídas, o usuário será informado e poderá forçar a re-execução.

###### 2.1.1.1. Gerenciamento de Checkpoints com `save_memory`

Para garantir a idempotência do processo `init` e evitar repetições desnecessárias, o Gemini CLI **deve** utilizar a ferramenta `save_memory` para registrar a conclusão de cada etapa.

*   **Registro de Conclusão:** Após a conclusão bem-sucedida de cada uma das 5 etapas do `init` (Análise de Contexto, Sincronização do Repositório, Configuração do Ambiente Python, Sincronização do Banco de Dados, Troubleshooting de Ambiente), o Gemini CLI **deve** chamar `save_memory` com uma string que identifique a etapa concluída (ex: `"init_step_context_analysis_completed"`).
*   **Verificação de Conclusão:** No início do processo `init`, antes de executar qualquer etapa, o Gemini CLI **deve** verificar se todas as etapas já foram marcadas como concluídas na memória. Se todas as 5 etapas estiverem marcadas como concluídas, o Gemini CLI **deve** informar o usuário que o ambiente já está pronto e perguntar se ele deseja forçar a re-execução do `init`.
*   **Forçar Re-execução:** Se o usuário optar por forçar a re-execução, o Gemini CLI **deve** ignorar os checkpoints na memória para aquela execução específica.

1.  **Análise de Contexto:** Leia e internalize o conteúdo completo de todos os arquivos `GEMINI.md` e `progress.md` do projeto.
2.  **Sincronização Inteligente do Repositório:** Verifique o status do Git (`git status`), busque atualizações (`git fetch`), e sincronize (`git pull`) se o branch local estiver desatualizado.
3.  **Configuração Inteligente do Ambiente Python:**
    *   Verifique e crie o ambiente virtual (`.venv`) com `uv venv` se necessário.
    *   Sincronize as dependências com `uv sync` para garantir a conformidade com `uv.lock`.
    *   Verifique a existência dos binários do Playwright em `./.playwright-browsers/`; se ausentes, execute `playwright install`.
4.  **Sincronização Inteligente do Banco de Dados:** Verifique migrações pendentes com `python manage.py showmigrations` e aplique-as com `python manage.py migrate` se necessário.
5.  **Troubleshooting de Ambiente (WSL):** Se o servidor Django estiver inacessível no WSL, crie um `.wslconfig` em `%USERPROFILE%` com `[wsl2] networkingMode=mirrored` e reinicie o WSL (`wsl --shutdown`).

#### 2.2. Processo de Finalização de Sessão (Commit e Push)

Este processo é **obrigatório** antes de cada commit:

1.  **Análise e Atualização de Diretrizes (`GEMINI.md`):** Após cada procedimento, analise a ação e revise os `GEMINI.md` para inserir novas instruções ou ajustar as existentes, mantendo as diretrizes atualizadas.
2.  **Análise e Atualização de Histórico (`progress.md`):** Após cada procedimento (exceto o comando `init`), complemente os arquivos `progress.md` relevantes com o que foi realizado, mantendo o histórico completo.
3.  **Limpeza Pré-Commit:** Execute `git status`. Remova arquivos de cache e temporários (`__pycache__`, `.ruff_cache`, etc.). **NUNCA REMOVA `db.sqlite3` ou `.env`**. O arquivo `db.sqlite3` é o banco de dados de desenvolvimento e **NÃO DEVE SER EXCLUÍDO EM HIPÓTESE ALGUMA**.
4.  **Versionamento:**
    *   `git add .`
    *   `git commit -m "..."` (Use mensagens detalhadas em Português do Brasil, explicando o "porquê". Para mensagens multi-linha ou com caracteres especiais, use `git commit -F <arquivo_temporario>`).
    *   `git pull --rebase`
    *   `git push`
    *   Valide com `git fetch && git status`.

**Lições Aprendidas com o Processo de Commit:**
*   **Verificação de Instruções Existentes:** Antes de adicionar uma nova instrução ao `GEMINI.md`, verifique se uma instrução semelhante já existe. Se existir, avalie se a instrução existente pode ser melhorada ou se a nova instrução é realmente necessária. Evite adicionar instruções duplicadas.

**Lições Aprendidas com o Processo de Commit:**
*   **Pre-commit Hooks:** Os hooks de pre-commit são rigorosos. Execute `ruff format .` e `ruff check . --fix` e stage as alterações *antes* de tentar o commit para evitar falhas.
*   **Pyright e Django:** A verificação de tipos com Pyright em projetos Django sem `django-stubs` pode gerar erros como `reportUnknownVariableType`. Relaxe a verificação para esses casos específicos em `pyrightconfig.json` se necessário.
*   **Bypass de Hooks:** Em casos extremos, `git commit --no-verify` pode ser usado para forçar o commit, mas **com extrema cautela**, pois ignora todas as verificações de qualidade.

#### 2.3.2. Gerenciamento de Ferramentas e Prevenção de Looping

Para garantir a execução eficiente e sem loops de tarefas que envolvem ferramentas, o Gemini CLI deve aderir às seguintes diretrizes:

1.  **Execução Atômica de Ferramentas de Modificação:**
    *   **Princípio:** Ferramentas que modificam o sistema de arquivos ou o estado do projeto (ex: `write_file`, `replace`, `run_shell_command` que altera arquivos) devem ser tratadas como operações atômicas.
    *   **Processo:** Uma vez que todos os pré-requisitos para a execução da ferramenta forem atendidos (ex: conteúdo para `write_file` preparado, `old_string`/`new_string` para `replace` definidos), a chamada da ferramenta (`print(default_api.tool_name(...))`) deve ser proposta **imediatamente** ao usuário para execução.
    *   **Evitar Loops:** **NUNCA** aguarde um prompt "continue" genérico do usuário *após propor a chamada da ferramenta* para então executá-la. O "continue" deve ser interpretado como um sinal para avançar para a *próxima etapa lógica da tarefa*, não para re-avaliar a execução da ferramenta já proposta.
2.  **Interpretação de Comandos do Usuário:**
    *   **Clareza:** Se a instrução do usuário for ambígua ou puder ser interpretada de múltiplas maneiras que afetem o fluxo de trabalho ou a execução de ferramentas, o Gemini CLI deve buscar **esclarecimento explícito** do usuário antes de prosseguir.
    *   **Contexto:** Sempre considere o contexto da conversa e o estado atual da tarefa ao interpretar comandos como "continue". Se uma ferramenta foi proposta, "continue" significa "execute a ferramenta proposta", não "re-avalie a etapa anterior".
3.  **Rastreamento de Estado Pós-Execução de Ferramentas:**
    *   Após a execução bem-sucedida de uma ferramenta de modificação, o Gemini CLI deve atualizar seu estado interno para refletir a conclusão daquela sub-tarefa. Isso evita a re-execução desnecessária ou a re-proposição da mesma ação.

###### 2.3.2.1. Uso Seguro de `read_file` e `write_file`

Para evitar loops e garantir a eficiência na manipulação de arquivos, o Gemini CLI **deve** aderir às seguintes diretrizes ao utilizar as ferramentas `read_file` e `write_file`:

*   **Propósito Claro:** Antes de usar `read_file` ou `write_file`, o Gemini CLI **deve** ter um propósito claro e específico para a operação. Evite leituras ou escritas sem um objetivo definido.
*   **Critérios de Parada:** Sempre que uma sequência de operações de leitura/escrita for iniciada, o Gemini CLI **deve** definir um critério de parada explícito. Isso pode incluir:
    *   Um número máximo de iterações.
    *   A detecção de uma condição específica no conteúdo do arquivo que indique a conclusão da tarefa.
    *   A ausência de mais arquivos a serem processados.
*   **Gerenciamento de Estado:** O Gemini CLI **deve** manter um registro interno do que já foi lido ou escrito para evitar reprocessamento desnecessário. Isso é crucial para operações que envolvem múltiplos arquivos ou leituras/escritas incrementais.
*   **Validação de Conteúdo:** Antes de usar `write_file`, o Gemini CLI **deve** validar o conteúdo a ser escrito para garantir que ele esteja correto e que a operação não levará a um estado inválido ou a um loop de correção/escrita.
*   **Leitura Incremental (`read_file` com `offset`/`limit`):** Para arquivos grandes, o Gemini CLI **deve** considerar o uso dos parâmetros `offset` e `limit` da ferramenta `read_file` para ler o arquivo em partes. Isso evita o carregamento de todo o arquivo na memória e permite um processamento mais controlado, prevenindo loops causados por tentativas de processar grandes volumes de dados de uma só vez.
*   **Confirmação do Usuário:** Em cenários onde a operação de leitura/escrita é complexa, de alto risco ou pode levar a um looping, o Gemini CLI **deve** buscar confirmação explícita do usuário antes de prosseguir.

#### 2.4. Política de Comandos Proibidos

Para garantir a segurança e integridade do projeto, o Gemini CLI **NUNCA** deve executar os seguintes comandos sem **confirmação explícita e justificada do usuário**:

*   **Exclusão do Banco de Dados de Desenvolvimento (`db.sqlite3`):** Proibido `rm -f db.sqlite3`. Ajustes devem ser feitos via migrações. Se a recriação for necessária, explique ao usuário e aguarde permissão.
*   **Modificação ou Exclusão do Arquivo de Variáveis de Ambiente (`.env`):** Proibido `rm -f .env` ou modificações não autorizadas. Instrua o usuário a fazê-lo manualmente.
*   **Comandos `git push --force` ou `git reset --hard`:** Proibido. Sempre prefira `git pull --rebase` e `git commit`. Se tais comandos forem essenciais, explique os riscos e aguarde permissão.

**Mecanismo de Salvaguarda Interno:** Ao detectar um "Comando Proibido", o Gemini CLI deve interromper a execução, emitir um aviso claro e aguardar uma confirmação explícita do usuário que reconheça o risco.

#### 2.5. Verificação de Procedimentos Multi-Etapas

Após a execução de procedimentos multi-etapas, o Gemini CLI **deve** realizar uma auto-verificação para garantir a execução completa e correta:

1.  **Listar Etapas:** Relembre e liste todas as etapas do procedimento.
2.  **Confirmar Execução:** Verifique se cada etapa foi executada conforme o planejado.
3.  **Tratamento de Omissões:** Se uma etapa foi omitida ou executada incorretamente, identifique o motivo e, se possível e seguro, execute-a imediatamente. Caso contrário, escale para o usuário explicando a falha.
4.  **Gerenciamento de Estado para Prevenção de Looping em Ações Bem-Sucedidas:** Para procedimentos com ações repetíveis, defina um estado de conclusão claro para cada sub-tarefa. Mantenha um registro de progresso interno para evitar re-processamento e detectar estagnação por falta de progresso.

---

### 3. Arquitetura e Padrões de Projeto

#### 3.1. Arquitetura Modular

*   `core/`: Configurações centrais do Django.
*   `apps/dashboard/`: Responsável pela interface do usuário (frontend).
*   `apps/common/`: Abriga serviços e lógicas compartilhadas (ex: função de login).
*   `apps/automacao_documentos/`: App **orquestrador**. Define a arquitetura e os modelos base para todas as automações.
*   `apps/automacao_ipiranga/`: App **implementador**. Contém a lógica específica para a automação do portal Ipiranga.

#### 3.2. Padrão de Automação (Baseado em Sinais)

Toda automação neste projeto **deve** seguir este padrão de evento-sinal-subprocesso:

1.  **Gatilho:** Uma ação cria um registro em um modelo "temporário" com status `pendente`.
2.  **Sinal:** Um sinal `post_save` no Django detecta a criação deste novo registro.
3.  **Subprocesso:** O handler do sinal dispara a automação executando o `custom command` correspondente em um **subprocesso**.
4.  **Limpeza:** O `custom command`, ao finalizar, **deve** remover o registro temporário e quaisquer arquivos associados dentro de um bloco `finally`.

#### 3.3. Padrões de Código Essenciais (Lições Aprendidas)

*   **Robustez de Subprocessos:** Ao usar `subprocess.Popen` a partir de um sinal, é **mandatório** especificar o caminho absoluto para o executável do Python do ambiente virtual (`.venv/bin/python`). Evite passar código complexo via `python -c`.
*   **Resiliência de Automação Web:** Implemente lógicas de espera e recarregamento de página para lidar com instabilidades de portais externos.
*   **Comandos de Limpeza Eficientes:** Garanta que os comandos de limpeza de dados (ex: `cleanup_media`, `cleanup_test_data`, `cleanup_automation_data`) utilizem operações em massa para exclusão de registros de banco de dados e incluam tratamento de erros robusto para a exclusão de arquivos. Evite deleções linha a linha.
*   **Externalização de Configurações:** URLs de portais e outras configurações específicas de ambiente **devem** ser externalizadas para as configurações do Django (`settings.py`) ou para o arquivo `.env` (via `python-decouple`). Evite hardcoding.
*   **Resiliência da Automação Playwright:** Ao desenvolver automações web com Playwright, garanta a robustez utilizando seletores CSS/XPath explícitos e estáveis, implementando esperas condicionais (`page.wait_for_selector`, `page.wait_for_load_state`) e tratando exceções para elementos não encontrados ou interações falhas.
*   **Mecanismos de Bloqueio/Status para Automações:** Para automações críticas, considere a implementação de mecanismos de bloqueio ou status mais granulares no modelo (ex: `pendente`, `em_processamento`, `concluido`, `falha_web`, `cancelado`) para evitar processamento simultâneo ou retentativas infinitas.
*   **Contadores de Tentativas no Modelo:** Para modelos que disparam automações (ex: `CertificadoVeiculo`), adicione o campo `tentativas_automacao`. A automação deve parar de tentar após um número definido de falhas, marcando o registro com um status final de falha e evitando loops infinitos de retentativa.

#### 3.4. Padrões de Comunicação Backend-Frontend

Para garantir uma comunicação eficiente, consistente e robusta entre o backend (Django) e o frontend (HTML/JavaScript), o projeto Orchestra adota os seguintes padrões:

*   **Formato de Dados (JSON):** Todas as interações de API entre backend e frontend **devem** utilizar JSON (JavaScript Object Notation) para o envio e recebimento de dados.
*   **Códigos de Status HTTP:** O backend **deve** retornar códigos de status HTTP apropriados para indicar o resultado da requisição (ex: `200 OK` para sucesso, `201 Created` para criação de recurso, `400 Bad Request` para erros de validação, `404 Not Found` para recursos inexistentes, `500 Internal Server Error` para erros inesperados no servidor).
*   **Estrutura de Resposta Padrão:** Para requisições que retornam dados ou mensagens, o backend **deve** seguir uma estrutura de resposta padrão para facilitar o consumo pelo frontend:
    *   **Sucesso:**
        ```json
        {
            "message": "Mensagem de sucesso (opcional)",
            "data": {
                // Dados retornados pela requisição
            }
        }
        ```
    *   **Erro:**
        ```json
        {
            "error": "Mensagem de erro clara e concisa",
            "details": {
                // Detalhes adicionais do erro (ex: erros de validação de campo)
            }
        }
        ```
*   **Comunicação Assíncrona e Polling:** Para operações de longa duração ou que envolvem processos em segundo plano (como automações), o frontend **deve** utilizar um mecanismo de polling para obter atualizações de status do backend.
    *   **Fluxo:**
        1.  O frontend inicia a operação assíncrona (ex: upload de documento que dispara uma automação).
        2.  O backend retorna um identificador único para a operação (ex: `certificate_id`).
        3.  O frontend inicia um loop de polling, fazendo requisições periódicas a um endpoint de status (ex: `/check-certificate-status/<id>/`) usando o identificador.
        4.  O backend retorna o status atual da operação (ex: `pendente`, `processando`, `concluido`, `falha`) e mensagens relevantes (`error_message`).
        5.  O frontend atualiza a interface do usuário com base no status recebido e interrompe o polling quando a operação atinge um status final (sucesso ou falha).
*   **Feedback Visual no Frontend:** O frontend **deve** fornecer feedback visual claro e imediato ao usuário sobre o status das operações, utilizando modais, mensagens de notificação ou indicadores de carregamento. As mensagens de erro do backend (`error_message`) **devem** ser exibidas de forma amigável e informativa.

---

### 4. Ferramentas, Procedimentos e Comandos

#### 4.1. Gerenciamento de Navegadores Playwright

*   **Instalação:** `playwright install` é mandatório no processo de `init`.
*   **Localização:** Os navegadores ficam em `./.playwright-browsers/`.
*   **CUIDADO com `git clean`:** O comando `git clean -fdx` **APAGARÁ** os navegadores. Use `git clean -fd` ou revise o que será apagado. Se removido, reinstale com `playwright install`.

#### 4.2. Procedimento de Gerenciamento do Servidor Django

Ao iniciar ou reiniciar o servidor, ou **antes de cada novo ciclo de teste**, siga estas etapas para garantir um ambiente limpo e consistente:

1.  **Verificar e Finalizar Processos Existentes:** Finalize todos os processos Python relacionados ao projeto em execução (ex: `ps aux | grep python`) para evitar conflitos.
2.  **Liberar Porta:** Certifique-se de que a porta 8000 está livre (`lsof -i :8000` e `kill -9 <PID>`).
3.  **Limpar Banco de Dados (CertificadoVeiculo):** Execute `python manage.py shell -c "from apps.automacao_ipiranga.models import CertificadoVeiculo; CertificadoVeiculo.objects.all().delete()"` para remover registros de automação anteriores.
4.  **Limpar Banco de Dados (Automation Data):** Execute `python manage.py cleanup_automation_data`.
5.  **Resetar Sequências de IDs:** Execute `python manage.py reset_automation_sequences` para zerar os contadores de auto-incremento das tabelas de automação (ex: `CertificadoVeiculo`, `VeiculoIpiranga`).
6.  **Limpar Arquivos Temporários:** Execute `python manage.py cleanup_media`.
6.  **Limpar Logs:** Remova arquivos de log antigos (`logs/*.log`).
7.  **Limpar Screenshots:** Remova todos os screenshots de depuração (`.png` files) de todo o projeto (`find . -name "*.png" -delete`).
8.  **Iniciar Servidor:** Inicie o servidor (ex: `python manage.py runserver`).

#### 4.3. Ferramentas e Comandos Rápidos

*   **Gerenciador de Pacotes (`uv`):**
    *   **Princípio:** Sempre utilize `uv` para gerenciar dependências e executar comandos no ambiente virtual. Priorize a instalação de **versões estáveis**.
    *   **Comandos:** `uv add <pacote>`, `uv remove <pacote>`, `uv sync`, `uv sync --upgrade`, `uv run <comando>`.
    *   **Pacotes Desatualizados:** Se `uv sync --upgrade` não atualizar um pacote, analise manualmente as notas de lançamento e a compatibilidade para evitar quebras.
*   **Qualidade de Código (`ruff`):** Utilize `ruff check . --fix` e `ruff format .` para conformidade com padrões de estilo e linting. Priorize a correção do código e remova código comentado irrelevante.
*   **Verificação de Tipos (`pyright`):** Execute `pyright` para validação da tipagem estática. Busque resolver os erros de tipo no código; use `type: ignore` apenas como último recurso e com justificativa clara.
*   **Comandos do Projeto:** `python manage.py runserver`, `python manage.py makemigrations [app]`, `python manage.py migrate`.
*   **Análise de Performance:**
    *   **Visão Macro (`cProfile`):** Use `python -m cProfile -o logs/comando.prof manage.py <comando>` para identificar gargalos. Analise com `pstats` ou visualize com `snakeviz` (`uv add snakeviz --group dev`, `snakeviz logs/comando.prof`).
    *   **Visão Micro (`line_profiler`):** Use `@profile` e `kernprof -l manage.py <comando>` para análise linha a linha. Lembre-se de remover `@profile` antes do commit.

---

### 5. Integração Contínua (CI/CD)

*   **GitHub Actions:** O projeto utiliza GitHub Actions (`.github/workflows/ci.yml`) para automação de testes e verificações de qualidade de código, incluindo `ruff` e `pyright`, garantindo a conformidade com os padrões antes da integração.

---

**Instrução:** Você não pode deletar informações de nenhum dos arquivos GEMINI.md nem de nenhum dos arquivos progress.md, os arquivos GEMINI.md do projeto Orchestra contém instruções importantes para serem seguidas e devem apenas incluir novas instruções ou ajustar aquelas que já existesm, desde que sejam ajustes para melhorar ainda mais as intruções, você NUNCA deve deletar todo o conteúdo deles, em hipótese nenhuma. O mesmo serve para todos os arquivos progress.md do projeto Orchestra, todos eles contém informações sobre o histórico do projeto, processos e procedimentos realizados ao longo do tempo, neles devem apenas serem incluídas novos históricos, processos ou procedimentos realizados, em ordem cronológica, você NUNCA deve excluiu o conteúdo completo de nenhum deles em hipótese nenhuma para incluir coisas novas.
