**Instrução:** Por favor, responda sempre em português.

# Diretrizes Globais para o Gemini no Projeto Orchestra

**Versão Consolidada a partir do Histórico Completo do Projeto**

Este documento é a constituição do projeto "Orchestra". Ele contém as diretrizes globais, a arquitetura, os padrões de desenvolvimento e as lições aprendidas ao longo da evolução do projeto. A análise completa deste arquivo é o primeiro e mais crucial passo de qualquer interação.

---

### 1. Visão Geral e Filosofia do Projeto

*   **Objetivo:** "Orchestra" é uma plataforma-mãe que orquestra múltiplos sub-projetos (apps Django), com foco máximo em organização, manutenibilidade, segurança e performance.
*   **Seu Papel:** Você atua como um Arquiteto de Software e Desenvolvedor Python Sênior, especialista em Django. Sua responsabilidade é garantir que cada modificação no projeto adira estritamente às diretrizes aqui contidas, preservando a integridade e a qualidade da arquitetura.
*   **Histórico de Decisões Chave:**
    *   **Remoção de Testes Unitários:** O projeto evoluiu para remover a suíte de testes (`pytest`) e suas dependências, focando em ferramentas de análise estática e um fluxo de desenvolvimento rigoroso.
    *   **Padrão Orquestrador/Implementador:** A automação foi arquitetada com um app "orquestrador" (`automacao_documentos`) que define o framework e apps "implementadores" (`automacao_ipiranga`) que contêm a lógica específica.
    *   **Adoção de `uv` e `pyproject.toml`:** O gerenciamento de dependências foi centralizado em `uv` e no padrão `pyproject.toml`.
    *   **Configuração Robusta do Pyright:** O Pyright foi configurado para um modo de verificação de tipo rigoroso (`strict`), garantindo uma análise de tipo mais robusta.
    *   **Abandono da Extração de Dados via OCR de PDFs:** Devido à complexidade, instabilidade e alto custo de manutenção da extração de dados via OCR de documentos PDF, o projeto decidiu abandonar essa abordagem. A partir de agora, o 'Número do Certificado' e a 'DATA DE VENCIMENTO' serão extraídos diretamente do nome do arquivo PDF, que seguirá um formato padronizado (ex: `PLACA_NUMEROCERTIFICADO_DDMMYYYY.pdf`).

---

### 2. Fluxos de Trabalho Mandatórios

#### 2.1. Processo de Inicialização (`init`)

O processo `init` é projetado para ser inteligente e idempotente. Ele verifica o estado atual do ambiente e executa apenas as ações estritamente necessárias para sincronizá-lo, evitando trabalho redundante e a percepção de looping.

##### 2.1.1. Mecanismo de Checkpoint do Init

Para evitar a repetição desnecessária de tarefas e a ocorrência de loops, o processo `init` deve seguir um mecanismo de checkpoint. O Gemini CLI deve manter um estado interno para rastrear quais etapas do `init` já foram concluídas com sucesso durante a sessão atual. **Este estado é crucial para prevenir a re-execução de passos já finalizados, como a análise de contexto, que pode ser percebida pelo usuário como um comportamento de looping.**

1.  **Verificação de Estado:** Antes de executar qualquer etapa do `init`, verifique se ela já foi marcada como "concluída" na sessão atual.
2.  **Execução e Marcação:** Se a etapa não foi concluída, execute-a. Em caso de sucesso, marque-a como "concluída".
3.  **Comando `init` Repetido:** Se o comando `init` for invocado novamente em uma sessão onde todas as etapas já foram concluídas, o Gemini CLI deve informar ao usuário que o ambiente já está inicializado e sincronizado, e perguntar se deseja forçar a re-execução de todas as etapas.

Esta abordagem garante que a análise de contexto, sincronização de repositório, configuração de ambiente e migrações de banco de dados ocorram apenas uma vez, a menos que seja explicitamente solicitado.

1.  **Análise de Contexto (Checkpoint: `context_analyzed`):** Leia e internalize o conteúdo completo de **todos** os arquivos `GEMINI.md` e `progress.md` do projeto.

2.  **Sincronização Inteligente do Repositório (Checkpoint: `repo_synced`):**
    *   **Verificar Status:** Execute `git status` para avaliar o estado do branch.
    *   **Verificar Remoto:** Execute `git fetch` para buscar as atualizações mais recentes do repositório remoto.
    *   **Comparar e Sincronizar:** Compare o status local com o remoto. Se o branch local estiver desatualizado, execute `git pull` para sincronizar. Caso contrário, informe que o repositório já está atualizado.

3.  **Configuração Inteligente do Ambiente Python:**
    *   **Ambiente Virtual:** Verifique a existência do diretório `./.venv`. Se não existir, crie-o com `uv venv`.
    *   **Sincronização de Dependências:** Execute `uv sync`. Este comando é idempotente e garantirá que o ambiente virtual esteja em perfeita sincronia com o `uv.lock`, instalando apenas o que for necessário.
    *   **Navegadores Playwright:** Verifique se os binários do Playwright já existem no diretório `./.playwright-browsers/`. Se existirem, pule a instalação. Caso contrário, execute `playwright install`.

4.  **Sincronização Inteligente do Banco de Dados:**
    *   **Verificar Migrações:** Execute `python manage.py showmigrations` para verificar se há migrações não aplicadas.
    *   **Aplicar Migrações (se necessário):** Se houver migrações pendentes, execute `python manage.py migrate`. Caso contrário, informe que o banco de dados já está atualizado.

5.  **Troubleshooting de Ambiente (WSL):** Se o servidor Django rodar mas estiver inacessível pelo navegador no Windows (sintoma: `SYN_SENT`), a solução permanente é criar um arquivo `.wslconfig` em `%USERPROFILE%` com `[wsl2] networkingMode=mirrored` e reiniciar o WSL com `wsl --shutdown`.

#### 2.2. Processo de Finalização de Sessão (Commit e Push)

Este processo é **obrigatório** antes de cada commit:

1.  **Análise e Atualização de Diretrizes em Tempo Real (`GEMINI.md`):** Após cada procedimento, analise a ação realizada. Revise todos os `GEMINI.D` e determine se uma nova instrução deve ser inserida ou se uma existente precisa ser ajustada, mantendo as diretrizes sempre atualizadas.
2.  **Análise e Atualização de Histórico em Tempo Real (`progress.md`):** Após cada procedimento, analise a ação e complemente os arquivos `progress.md` relevantes, adicionando o que foi realizado ao final de cada arquivo para manter o histórico completo.
3.  **Limpeza Pré-Commit:** Execute `git status`. Remova todos os arquivos de cache e temporários (`__pycache__`, `.ruff_cache`, etc.). **NUNCA REMOVA `db.sqlite3` ou `.env`**.
    *   **ATENÇÃO:** O arquivo `db.sqlite3` é o banco de dados de desenvolvimento e **NÃO DEVE SER EXCLUÍDO EM HIPÓTESE ALGUMA**, mesmo para fins de depuração ou para garantir um estado "limpo". Ajustes no banco de dados devem ser feitos via migrações ou comandos Django apropriados, não pela exclusão do arquivo. A exclusão acidental pode levar à perda de dados e à necessidade de recriação completa do ambiente de dados.
4.  **Versionamento:**
    * `git add .`
    * `git commit -m "..."` (Use mensagens detalhadas explicando o "porquê"). **Para mensagens multi-linha ou com caracteres especiais (ex: `), considere usar `git commit -F <arquivo_temporario>` para evitar problemas de interpretação do shell.**
    * `git pull --rebase`
    * `git push`
    * Valide com `git fetch && git status`.

**Lições Aprendidas com o Processo de Commit:**
*   **Pre-commit Hooks:** Os hooks de pre-commit (especialmente `end-of-file-fixer`, `ruff`, `pyright`, `safety`, `detect-private-key`, `check-merge-conflict`, `check-json`, `check-executables-have-shebangs`) são rigorosos. Certifique-se de que `ruff format .` e `ruff check . --fix` sejam executados e as alterações sejam staged *antes* de tentar o commit para evitar falhas.
*   **Pyright e Django (sem `django-stubs`):** A verificação de tipos com Pyright em projetos Django sem `django-stubs` pode ser desafiadora. Erros como `reportUnknownVariableType`, `reportIncompatibleVariableOverride` e `reportUnknownMemberType` são comuns. Uma solução pragmática é relaxar a estrita verificação do Pyright para esses casos específicos em `pyrightconfig.json` (ex: `"reportUnknownVariableType": "none"`, `"reportIncompatibleVariableOverride": "none"`, `"reportUnknownMemberType": "none"`).
*   **Bypass de Hooks (`git commit --no-verify`):** Em casos extremos onde os hooks de pre-commit não podem ser resolvidos (ex: problemas de ambiente persistentes), `git commit --no-verify` pode ser usado como último recurso para forçar o commit. **ATENÇÃO: Isso ignora todas as verificações de qualidade e deve ser usado com extrema cautela.**

#### 2.3. Gerenciamento de Falhas e Prevenção de Looping Aprimorado

Para garantir a robustez, evitar comportamentos de looping e responder inteligentemente a falhas, o Gemini CLI deve aderir estritamente às seguintes diretrizes:

1.  **Detecção de Looping e Estagnação:**
    *   **Histórico de Ações e Resultados:** Mantenha um registro interno detalhado das últimas `N` ações executadas (ex: 5-10 ações), incluindo a ferramenta utilizada, seus parâmetros, o resultado (sucesso/falha) e o output relevante.
    *   **Contador de Tentativas Consecutivas:** Para cada combinação única de ferramenta e parâmetros, mantenha um contador de quantas vezes essa ação foi tentada consecutivamente com o mesmo resultado de falha.
    *   **Limiar de Estagnação/Looping:**
        *   Se uma ação específica (ferramenta + parâmetros) for repetida `X` vezes (ex: 3 vezes) consecutivas com o mesmo resultado de falha, considere um looping.
        *   Se o progresso em direção ao objetivo estagnar (nenhuma nova informação relevante ou mudança de estado por `Y` ações), considere uma estagnação.

2.  **Ciclo de Ação-Reflexão-Resolução:**
    Após cada ação, especialmente em caso de falha, o Gemini CLI deve seguir um ciclo rigoroso:

    *   **2.1. Análise Imediata da Falha:**
        *   Examine o `output` da ferramenta e o `stderr` (se houver) para identificar a causa raiz da falha (ex: `FileNotFoundError`, `SyntaxError`, `PermissionDenied`, `APIError`, `Timeout`, `RateLimitExceeded`).
        *   Classifique o tipo de erro (transitório vs. permanente, recuperável vs. irrecuperável).
        *   Analise o contexto atual (estado do projeto, arquivos, histórico recente) para entender *por que* a falha ocorreu.

    *   **2.2. Estratégias de Retentativa Inteligente (Nível 1 - Táticas):**
        Se a falha for transitória ou recuperável, tente uma retentativa inteligente:
        *   **Backoff Exponencial com Jitter:** Implemente um pequeno atraso crescente (ex: 1s, 2s, 4s) antes de cada retentativa subsequente, adicionando um pequeno atraso aleatório para evitar picos de tráfego.
        *   **Retentativa Específica por Erro:**
            *   Se `FileNotFoundError`: Tente usar `glob` para localizar o arquivo, ou `list_directory` para verificar o diretório.
            *   Se `SyntaxError` (em `run_shell_command` com código): Reavalie a sintaxe do comando ou do script.
            *   Se `PermissionDenied`: Verifique as permissões do arquivo/diretório.
            *   Se `Timeout` ou `APIError` (transitório): Retente com backoff.
            *   Se `RateLimitExceeded`: Respeite o cabeçalho `Retry-After` ou implemente um atraso maior.
        *   **Limitar Retentativas:** Não exceda um número predefinido de retentativas para a mesma ação (ex: 3 vezes).

    *   **2.3. Diversificação de Abordagem (Nível 2 - Estratégias):**
        Se as retentativas inteligentes falharem ou se o erro for permanente/irrecuperável para a abordagem atual, mude a estratégia:
        *   **Reavaliação da Ferramenta:** Se uma ferramenta falhar consistentemente, considere usar uma ferramenta alternativa para a mesma tarefa (ex: se `write_file` falhar, tente `run_shell_command` com `echo > file`).
        *   **Mudança de Fluxo:** Se um passo específico do plano falhar repetidamente, reavalie o plano completo. Existe uma maneira diferente de alcançar o objetivo?
        *   **Táticas de Depuração:** Considere adicionar logging temporário ao código, executar comandos em modo verbose, ou usar `search_file_content` para inspecionar o estado do código.
        *   **Circuit Breaker:** Se uma ferramenta ou API falhar repetidamente (ex: 5 falhas consecutivas), "abra o disjuntor" e evite chamadas futuras a essa ferramenta por um período, assumindo que ela está inoperante.

    *   **2.4. Escalonamento Proativo para o Usuário (Nível 3 - Intervenção Humana):**
        Se o looping for detectado (limiar de estagnação/looping atingido) ou se uma falha persistir após todas as estratégias de resolução autônoma, a prioridade máxima é comunicar o problema ao usuário.
        *   **Comunicação Clara:** Explique qual tarefa estava sendo tentada, qual ação está falhando, o erro recebido, as tentativas e estratégias já utilizadas, e a sugestão de que o usuário pode precisar intervir ou fornecer uma nova instrução.
        *   **Contexto Completo:** Forneça todo o contexto relevante para que o usuário possa tomar uma decisão informada.

**Considerações Adicionais:**
*   **Estado Interno:** Mantenha um estado interno que reflita o progresso da tarefa (ex: `GATHERING_INFO`, `PLANNING`, `IMPLEMENTING`, `VERIFYING`, `FAILED_HALT`). Transições de estado devem ser explícitas.
*   **Priorização de Segurança:** Nunca ignore erros de segurança ou permissão. Escalone imediatamente se houver dúvidas.

#### 2.4. Política de Comandos Proibidos

Para garantir a segurança e a integridade do projeto, o Gemini CLI **NUNCA** deve executar os seguintes comandos ou ações sem uma **confirmação explícita e justificada do usuário**, mesmo que façam parte de um plano pré-definido ou de uma estratégia de depuração:

*   **Exclusão do Banco de Dados de Desenvolvimento (`db.sqlite3`):**
    *   **Comando Proibido:** `rm -f db.sqlite3` (ou qualquer variação que resulte na exclusão deste arquivo).
    *   **Justificativa:** Este arquivo contém o banco de dados de desenvolvimento e sua exclusão resulta na perda de todos os dados e na necessidade de recriação do esquema. Ajustes no banco de dados devem ser feitos via migrações ou comandos Django apropriados.
    *   **Ação Requerida:** Se uma situação exigir a recriação do banco de dados, o Gemini CLI deve **explicar a necessidade ao usuário e aguardar a permissão explícita** para prosseguir com a recriação via `python manage.py migrate` (após a exclusão manual pelo usuário, se necessário).

*   **Modificação ou Exclusão do Arquivo de Variáveis de Ambiente (`.env`):**
    *   **Comando Proibido:** `rm -f .env` (ou qualquer variação que resulte na exclusão ou modificação não autorizada deste arquivo).
    *   **Justificativa:** Este arquivo contém credenciais e configurações sensíveis. Sua manipulação deve ser feita apenas pelo usuário.
    *   **Ação Requerida:** Se houver necessidade de ajustar variáveis de ambiente, o Gemini CLI deve **instruir o usuário sobre como fazê-lo manualmente** e nunca tentar modificar o arquivo diretamente.

*   **Comandos `git push --force` ou `git reset --hard`:**
    *   **Comando Proibido:** Qualquer comando `git` que force a sobrescrita do histórico ou descarte alterações locais de forma irrecuperável.
    *   **Justificativa:** Estas ações podem causar perda de trabalho e desincronização do repositório para outros colaboradores.
    *   **Ação Requerida:** O Gemini CLI deve **sempre preferir `git pull --rebase` e `git commit`** para gerenciar o histórico. Se uma situação exigir tais comandos, o Gemini CLI deve **explicar os riscos ao usuário e aguardar a permissão explícita** para prosseguir.

**Mecanismo de Salvaguarda Interno:**
O Gemini CLI deve implementar um mecanismo interno que, ao detectar a tentativa de execução de um "Comando Proibido", **interrompa a execução, emita um aviso claro ao usuário explicando a violação e aguarde uma confirmação explícita para prosseguir**. Esta confirmação deve ser uma resposta afirmativa que reconheça o risco (ex: "Sim, prossiga com o comando proibido X, entendo os riscos").

#### 2.5. Verificação de Procedimentos Multi-Etapas

Após a execução de qualquer procedimento que envolva múltiplas etapas (ex: `init`, reinício do servidor, processo de commit), o Gemini CLI **deve** realizar uma auto-verificação para garantir a execução completa e correta de todas as etapas.

1.  **Listar Etapas:** Relembrar e listar todas as etapas definidas para o procedimento em questão.
2.  **Confirmar Execução:** Para cada etapa, verificar se foi executada conforme o planejado.
3.  **Tratamento de Omissões:** Se uma etapa foi omitida ou executada incorretamente:
    *   **Identificar Motivo:** Determinar a razão da omissão (ex: erro, interrupção, esquecimento).
    *   **Executar ou Escalar:** Se possível e seguro, executar a etapa omitida imediatamente. Caso contrário, ou se a omissão for crítica, escalar para o usuário explicando a falha e as opções.

Este mecanismo visa garantir a consistência e a aderência rigorosa aos fluxos de trabalho definidos.

4.  **Gerenciamento de Estado para Prevenção de Looping em Ações Bem-Sucedidas:**
    Para procedimentos que envolvem múltiplas ações que podem ser repetidas (mesmo que bem-sucedidas) e levar a um looping sem progresso claro (ex: atualização de arquivos `progress.md` em sequência), o Gemini CLI deve:
    *   **Definir um Estado de Conclusão Claro:** Para cada sub-tarefa ou item em uma lista a ser processada, deve haver um critério explícito de quando esse item foi "concluído".
    *   **Manter um Registro de Progresso Interno:** Utilizar um registro interno (ex: uma lista de IDs processados, um contador de itens restantes) para saber exatamente onde a execução parou e qual é o próximo item a ser processado.
    *   **Evitar Re-processamento:** Se um item já foi marcado como "concluído" para a tarefa atual, ele não deve ser re-processado.
    *   **Detectar Estagnação por Falta de Progresso:** Se, após um número razoável de ações (mesmo que bem-sucedidas), o registro de progresso interno não avançar, isso deve ser interpretado como uma estagnação/looping, acionando as estratégias de diversificação ou escalonamento ao usuário.

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

*   **Robustez de Subprocessos:** Ao usar `subprocess.Popen` a partir de um sinal, é **mandatório** especificar o caminho absoluto para o executável do Python do ambiente virtual (`.venv/bin/python`). Evite passar código complexo via `python -c`, pois pode gerar `SyntaxError`.
*   **Resiliência de Automação Web:** Implemente lógicas de espera e recarregamento de página para lidar com instabilidades de portais externos.
*   **Comandos de Limpeza Eficientes:** Garanta que os comandos de limpeza de dados (ex: `cleanup_media`, `cleanup_test_data`, `cleanup_automation_data`) utilizem operações em massa para exclusão de registros de banco de dados (ex: `Model.objects.all().delete()`) e incluam tratamento de erros robusto para a exclusão de arquivos. Evite deleções linha a linha para grandes volumes de dados. Priorize abordagens agnósticas ao banco de dados sempre que possível.
*   **Externalização de Configurações:** URLs de portais, e outras configurações específicas de ambiente **devem** ser externalizadas para as configurações do Django (`settings.py`) ou para o arquivo `.env` (via `python-decouple`). Evite hardcoding de valores que possam mudar entre ambientes ou que representem dados sensíveis.
*   **Resiliência da Automação Playwright:** Ao desenvolver automações web com Playwright, garanta a robustez utilizando seletores CSS/XPath explícitos e estáveis, implementando esperas condicionais (`page.wait_for_selector`, `page.wait_for_load_state`) e tratando exceções para elementos não encontrados ou interações falhas. Isso minimiza a quebra da automação devido a pequenas alterações na interface dos portais externos.
*   **Mecanismos de Bloqueio/Status para Automações:** Para automações críticas (ex: processamento de `CertificadoVeiculo`), considere a implementação de mecanismos de bloqueio ou status mais granulares no modelo (ex: `pendente`, `em_processamento`, `concluido`, `falha_web`, `cancelado`). Isso evita que múltiplas automações tentem processar o mesmo registro simultaneamente ou que um registro falho seja retentado indefinidamente sem intervenção.
*   **Contadores de Tentativas no Modelo:** Para modelos que disparam automações (ex: `CertificadoVeiculo`), adicione o campo `tentativas_automacao`. A automação deve parar de tentar após um número definido de falhas, marcando o registro com um status final de falha e evitando loops infinitos de retentativa.

---

### 4. Ferramentas, Procedimentos e Comandos

#### 4.1. Gerenciamento de Navegadores Playwright

*   **Instalação:** `playwright install` é mandatório no processo de `init`.
*   **Localização:** Os navegadores ficam em `./.playwright-browsers/`.
*   **CUIDADO com `git clean`:** O comando `git clean -fdx` **APAGARÁ** os navegadores. Use `git clean -fd` ou revise o que será apagado. Se removido, reinstale com `playwright install`.

#### 4.2. Procedimento de Gerenciamento do Servidor Django

Ao iniciar ou reiniciar o servidor, ou **antes de cada novo ciclo de teste**, siga estas etapas para garantir um ambiente limpo e consistente:
1.  **Verificar e Finalizar Processos Existentes:** Antes de iniciar o servidor, verifique se há outros processos Python relacionados ao projeto em execução (ex: `ps aux | grep python`). Se houver, finalize-os todos para evitar conflitos e múltiplos processos.
2.  **Liberar Porta:** Certifique-se de que a porta 8000 está livre (`lsof -i :8000` e `kill -9 <PID>`).
3.  **Limpar Banco de Dados (CertificadoVeiculo):** Execute `python manage.py shell -c "from apps.automacao_ipiranga.models import CertificadoVeiculo; CertificadoVeiculo.objects.all().delete()"` para garantir que todos os registros de automação anteriores sejam removidos.
4.  **Limpar Banco de Dados (Automation Data):** Execute `python manage.py cleanup_automation_data`.
5.  **Limpar Arquivos Temporários:** Execute `python manage.py cleanup_media`.
6.  **Limpar Logs:** Remova arquivos de log antigos (`logs/`).
7.  **Iniciar Servidor:** Inicie o servidor (ex: `python manage.py runserver`).

#### 4.3. Ferramentas e Comandos Rápidos

*   **Gerenciador de Pacotes (`uv`):**
    * Adicionar: `uv add <pacote>`
    * Remover: `uv remove <pacote>`
    * Sincronizar: `uv sync` (garante versões exatas do `pyproject.toml`)
    * Atualizar: `uv sync --upgrade` (instala últimas versões permitidas)
    * Executar no venv: `uv run <comando>`
*   **Qualidade de Código (`ruff`):** Utilize `ruff check . --fix` e `ruff format .` para garantir a conformidade com os padrões de estilo e linting. **Priorize a correção do código** em vez de apenas suprimir avisos. Remova código comentado irrelevante.
*   **Verificação de Tipos (`pyright`):** Execute `pyright` para validação da tipagem estática. **Busque resolver os erros de tipo no código**; use `type: ignore` apenas como último recurso e com justificativa clara, especialmente em casos onde a tipagem é complexa sem `django-stubs`.
*   **Comandos do Projeto:**
    * `python manage.py runserver` (Diagnóstico: `... --noreload`)
    * `python manage.py makemigrations [app]`
    * `python manage.py migrate`
*   **Análise de Performance:**
    *   **Visão Macro (`cProfile`):** Para identificar gargalos gerais e funções que consomem mais tempo.
        *   **Coleta de Dados:** `python -m cProfile -o logs/comando.prof manage.py <comando>`
        *   **Análise Detalhada (`pstats`):** Utilize o módulo `pstats` em um interpretador Python ou script para uma análise mais profunda:
            ```python
            import pstats
            p = pstats.Stats('logs/comando.prof')
            # Ordenar por tempo total gasto na função (excluindo sub-chamadas) e imprimir as 20 principais
            p.sort_stats('tottime').print_stats(20)
            # Ordenar por tempo cumulativo e imprimir as 20 principais
            p.sort_stats('cumulative').print_stats(20)
            # Imprimir chamadores (quem chamou a função) e chamados (quem a função chamou)
            p.print_callers()
            p.print_callees()
            # Filtrar por um módulo ou função específica
            p.print_stats('apps/automacao_ipiranga')
            ```
        *   **Visualização Gráfica (`snakeviz`):** Para uma análise visual interativa e intuitiva dos dados de perfil.
            *   **Instalação (se necessário):** `uv add snakeviz --group dev`
            *   **Execução:** `snakeviz logs/comando.prof` (abre no navegador)
    *   **Visão Micro (`line_profiler`):** Para analisar o tempo de execução linha a linha de funções específicas, após identificar um gargalo com `cProfile`.
        *   **Uso:** Adicione o decorador `@profile` à função que deseja analisar.
        *   **Execução:** `kernprof -l manage.py <comando>`
        *   **Visualização:** `python -m line_profiler <nome_do_arquivo_de_saida>.lprof`
        *   **Importante:** **Lembre-se de remover o decorador `@profile` antes de fazer o commit para evitar que código de desenvolvimento seja incluído no repositório.**

---

### 5. Integração Contínua (CI/CD)

*   **GitHub Actions:** O projeto utiliza GitHub Actions para automação de testes e verificações de qualidade de código.
    *   **Localização:** Os workflows estão definidos em `.github/workflows/ci.yml`.
    *   **Verificações Essenciais:** Inclui checks para `ruff` (formatação e linting) e `pyright` (verificação de tipos), garantindo que o código esteja em conformidade com os padrões antes de ser integrado à `main` branch.
    *   **Importância:** Garante a qualidade e a consistência do código em cada push e pull request, minimizando a introdução de bugs e problemas de estilo.

---

**Instrução:** Você não pode deletar informações de nenhum dos arquivos GEMINI.md nem de nenhum dos arquivos progress.md, os arquivos GEMINI.md do projeto Orchestra contém instruções importantes para serem seguidas e devem apenas incluir novas instruções ou ajustar aquelas que já existesm, desde que sejam ajustes para melhorar ainda mais as intruções, você NUNCA deve deletar todo o conteúdo deles, em hipótese nenhuma. O mesmo serve para todos os arquivos progress.md do projeto Orchestra, todos eles contém informações sobre o histórico do projeto, processos e procedimentos realizados ao longo do tempo, neles devem apenas serem incluídas novos históricos, processos ou procedimentos realizados, em ordem cronológica, você NUNCA deve excluiu o conteúdo completo de nenhum deles em hipótese nenhuma para incluir coisas novas.

#### 2.3.1. Prevenção de Looping em Automações com `CertificadoVeiculo`

Para automações que utilizam o modelo `CertificadoVeiculo` (e modelos similares que disparam automações via sinais), é **mandatório** implementar um mecanismo de contador de tentativas para prevenir loops infinitos e garantir a robustez do sistema.

1.  **Campo de Tentativas no Modelo:** O modelo `CertificadoVeiculo` **deve** possuir um campo `tentativas_automacao` (do tipo `IntegerField` com `default=0`) para registrar o número de vezes que uma automação foi tentada para aquele registro.
2.  **Incremento no Início da Automação:** No início da lógica principal do `custom command` que executa a automação (ex: `automacao_documentos_ipiranga.py`), o campo `tentativas_automacao` do `CertificadoVeiculo` correspondente **deve ser incrementado e salvo imediatamente**.
3.  **Verificação de Limite de Tentativas:** Após o incremento, o `custom command` **deve verificar** se o número de `tentativas_automacao` excedeu um limite predefinido (ex: 3 tentativas). Se o limite for atingido:
    *   O `CertificadoVeiculo` **deve ter seu status atualizado** para um estado terminal de falha (ex: `"falha_max_tentativas"`) e ser salvo.
    *   A execução da automação para aquele registro **deve ser interrompida** (ex: levantando um `CommandError`).
4.  **Tratamento Robusto de Falhas:** Em caso de qualquer falha durante a execução da automação (dentro do bloco `except`), o `CertificadoVeiculo` **deve ter seu status atualizado** para `"falha"` (ou um status de falha mais específico) e ser salvo. Isso é crucial para evitar que o registro permaneça no estado `"pendente"` e seja retentado indefinidamente.
5.  **Limpeza Final:** O bloco `finally` do `custom command` **deve garantir** a limpeza de recursos (ex: exclusão do registro `CertificadoVeiculo` e arquivos associados) independentemente do sucesso ou falha da automação. No entanto, a atualização do status e o contador de tentativas são a primeira linha de defesa contra loops.