**Instrução:** Por favor, responda sempre em português.

# Diretrizes Globais para o Gemini no Projeto Orchestra

**Versão Consolidada a partir do Histórico Completo do Projeto**

Este documento é a constituição do projeto "Orchestra". Ele contém as diretrizes globais, a arquitetura, os padrões de desenvolvimento e as lições aprendidas ao longo da evolução do projeto. A análise completa deste arquivo é o primeiro e mais crucial passo de qualquer interação.

---

### 0. Diretrizes Operacionais do Gemini CLI

*   **Gerenciamento de Memória (Heap Size):** Para evitar erros de "JavaScript heap out of memory" no Gemini CLI, ajuste a variável de ambiente `NODE_OPTIONS` para aumentar o limite de memória. Exemplo: `export NODE_OPTIONS="--max-old-space-size=8192"`. Esta configuração é temporária; para torná-la permanente, adicione-a ao seu arquivo de configuração de shell.

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
2.  **Análise e Atualização de Histórico (`progress.md`):** Após cada procedimento, complemente os arquivos `progress.md` relevantes com o que foi realizado, mantendo o histórico completo.
3.  **Limpeza Pré-Commit:** Execute `git status`. Remova arquivos de cache e temporários (`__pycache__`, `.ruff_cache`, etc.). **NUNCA REMOVA `db.sqlite3` ou `.env`**. O arquivo `db.sqlite3` é o banco de dados de desenvolvimento e **NÃO DEVE SER EXCLUÍDO EM HIPÓTESE ALGUMA**.
4.  **Versionamento:**
    *   `git add .`
    *   `git commit -m "..."` (Use mensagens detalhadas em Português do Brasil, explicando o "porquê". Para mensagens multi-linha ou com caracteres especiais, use `git commit -F <arquivo_temporario>`).
    *   `git pull --rebase`
    *   `git push`
    *   Valide com `git fetch && git status`.

**Lições Aprendidas com o Processo de Commit:**
*   **Pre-commit Hooks:** Os hooks de pre-commit são rigorosos. Execute `ruff format .` e `ruff check . --fix` e stage as alterações *antes* de tentar o commit para evitar falhas.
*   **Pyright e Django:** A verificação de tipos com Pyright em projetos Django sem `django-stubs` pode gerar erros como `reportUnknownVariableType`. Relaxe a verificação para esses casos específicos em `pyrightconfig.json` se necessário.
*   **Bypass de Hooks:** Em casos extremos, `git commit --no-verify` pode ser usado para forçar o commit, mas **com extrema cautela**, pois ignora todas as verificações de qualidade.

#### 2.3. Gerenciamento de Falhas e Prevenção de Looping Aprimorado

Para garantir robustez e evitar loops, o Gemini CLI deve seguir estas diretrizes:

1.  **Detecção de Looping e Estagnação:** Mantenha um registro interno das últimas ações e resultados, com um contador de tentativas consecutivas. Se uma ação falhar repetidamente (ex: 3 vezes) ou o progresso estagnar, considere um looping.
2.  **Ciclo de Ação-Reflexão-Resolução:** Após cada falha, siga um ciclo rigoroso:
    *   **Análise Imediata da Falha:** Examine o `output` e `stderr` para identificar a causa raiz e classificar o erro.
    *   **Estratégias de Retentativa Inteligente (Nível 1 - Táticas):** Para falhas transitórias, tente retentativas com backoff exponencial e jitter. Limite as retentativas (ex: 3 vezes).
    *   **Diversificação de Abordagem (Nível 2 - Estratégias):** Se as retentativas falharem, mude a estratégia: reavalie a ferramenta, mude o fluxo, ou use táticas de depuração. Implemente um "circuit breaker" para ferramentas que falham repetidamente.
    *   **Escalonamento Proativo para o Usuário (Nível 3 - Intervenção Humana):** Se o looping for detectado ou a falha persistir, comunique o problema ao usuário de forma clara, explicando a falha, as tentativas e estratégias usadas, e a necessidade de intervenção.
3.  **Considerações Adicionais:** Mantenha um estado interno que reflita o progresso da tarefa. Priorize a segurança, escalando imediatamente erros de segurança ou permissão.

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
5.  **Limpar Arquivos Temporários:** Execute `python manage.py cleanup_media`.
6.  **Limpar Logs:** Remova arquivos de log antigos (`logs/`).
7.  **Iniciar Servidor:** Inicie o servidor (ex: `python manage.py runserver`).

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
