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

---

### 2. Fluxos de Trabalho Mandatórios

#### 2.1. Processo de Inicialização (`init`)

Siga **rigorosamente** esta sequência para preparar o ambiente:

1.  **Análise de Contexto Total:** Leia e internalize o conteúdo completo de **todos** os arquivos `GEMINI.md` e `progress.md` do projeto. Isso é crucial para que o Gemini CLI compreenda todas as instruções, regras e o histórico de processos e procedimentos já realizados, garantindo que novos processos sejam efetuados em conformidade e evitando a repetição de erros.
2.  **Sincronização do Repositório:**
    *   **Verifique o Status:** Execute `git status` para identificar quaisquer alterações locais não comitadas. Se houver, comite-as ou descarte-as conforme necessário antes de prosseguir.
    *   **Atualize o Repositório:** Execute `git pull` para sincronizar com a versão mais recente.
3.  **Configuração do Ambiente Python:**
    * **Ambiente Virtual:** Confirme que `./.venv` existe. Se não, crie-o com `uv venv`.
    * **Instalação de Dependências:** Instale **todas** as dependências com `uv pip install --group all`.
    * **Verificação e Atualização de Dependências:** Verifique se há pacotes desatualizados com `uv pip list --outdated` e, se houver, atualize-os com `uv sync --upgrade`.
    * **Instalação de Navegadores Playwright:** Execute `playwright install`.
4.  **Configuração do Banco de Dados:** Execute `python manage.py migrate`.

6.  **Troubleshooting de Ambiente (WSL):** Se o servidor Django rodar mas estiver inacessível pelo navegador no Windows (sintoma: `SYN_SENT`), a solução permanente é criar um arquivo `.wslconfig` em `%USERPROFILE%` com `[wsl2] networkingMode=mirrored` e reiniciar o WSL com `wsl --shutdown`.

#### 2.2. Processo de Finalização de Sessão (Commit e Push)

Este processo é **obrigatório** antes de cada commit:

1.  **Análise e Atualização de Diretrizes em Tempo Real (`GEMINI.md`):** Após cada procedimento, analise a ação realizada. Revise todos os `GEMINI.D` e determine se uma nova instrução deve ser inserida ou se uma existente precisa ser ajustada, mantendo as diretrizes sempre atualizadas.
2.  **Análise e Atualização de Histórico em Tempo Real (`progress.md`):** Após cada procedimento, analise a ação e complemente os arquivos `progress.md` relevantes, adicionando o que foi realizado ao final de cada arquivo para manter o histórico completo.
3.  **Limpeza Pré-Commit:** Execute `git status`. Remova todos os arquivos de cache e temporários (`__pycache__`, `.ruff_cache`, etc.). **NUNCA REMOVA `db.sqlite3` ou `.env`**.
    *   **ATENÇÃO:** O arquivo `db.sqlite3` é o banco de dados de desenvolvimento e **NÃO DEVE SER EXCLUÍDO EM HIPÓTESE ALGUMA**, mesmo para fins de depuração ou para garantir um estado "limpo". Ajustes no banco de dados devem ser feitos via migrações ou comandos Django apropriados, não pela exclusão do arquivo. A exclusão acidental pode levar à perda de dados e à necessidade de recriação completa do ambiente de dados.
4.  **Versionamento:**
    * `git add .`
    * `git commit -m "..."` (Use mensagens detalhadas explicando o "porquê").
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
*   **Robustez na Extração de Dados (OCR):** A extração de dados via OCR é desafiadora. Utilize **expressões regulares flexíveis** e funções de normalização. A calibração deve ser iterativa, ajustando as regex para lidar com erros comuns de reconhecimento (ex: 'T' por '6', 'O' por '0').
*   **Resiliência de Automação Web:** Implemente lógicas de espera e recarregamento de página para lidar com instabilidades de portais externos.
*   **Segurança de Credenciais:** Utilize **exclusivamente o arquivo `.env`** com `python-decouple`.
*   **Segurança Web:** Sempre use a proteção CSRF do Django. O decorador `@csrf_exempt` foi removido e não deve ser reintroduzido.
*   **Comandos de Limpeza Eficientes:** Garanta que os comandos de limpeza de dados (ex: `cleanup_media`, `cleanup_test_data`, `cleanup_automation_data`) utilizem operações em massa para exclusão de registros de banco de dados (ex: `Model.objects.all().delete()`) e incluam tratamento de erros robusto para a exclusão de arquivos. Evite deleções linha a linha para grandes volumes de dados. Priorize abordagens agnósticas ao banco de dados sempre que possível.
*   **Externalização de Configurações:** URLs de portais, coordenadas de Regiões de Interesse (ROIs) para OCR, e outras configurações específicas de ambiente **devem** ser externalizadas para as configurações do Django (`settings.py`) ou para o arquivo `.env` (via `python-decouple`). Evite hardcoding de valores que possam mudar entre ambientes ou que representem dados sensíveis.
*   **Tipagem de Modelos Django com Pyright:** Sem `django-stubs`, a tipagem de modelos Django pode ser complexa. Pode ser necessário usar `type: ignore` para suprimir erros específicos do Pyright relacionados a atributos de modelo ou a argumentos de construtores de campo que não são inferidos corretamente.
*   **Resiliência da Automação Playwright:** Ao desenvolver automações web com Playwright, garanta a robustez utilizando seletores CSS/XPath explícitos e estáveis, implementando esperas condicionais (`page.wait_for_selector`, `page.wait_for_load_state`) e tratando exceções para elementos não encontrados ou interações falhas. Isso minimiza a quebra da automação devido a pequenas alterações na interface dos portais externos.
*   **Mecanismos de Bloqueio/Status para Automações:** Para automações críticas (ex: processamento de `CertificadoVeiculo`), considere a implementação de mecanismos de bloqueio ou status mais granulares no modelo (ex: `pendente`, `em_processamento`, `concluido`, `falha_web`, `falha_ocr`, `cancelado`). Isso evita que múltiplas automações tentem processar o mesmo registro simultaneamente ou que um registro falho seja retentado indefinidamente sem intervenção.
*   **Contadores de Tentativas no Modelo:** Para modelos que disparam automações (ex: `CertificadoVeiculo`), adicione campos como `tentativas_automacao` e `tentativas_ocr`. A automação deve parar de tentar após um número definido de falhas, marcando o registro com um status final de falha e evitando loops infinitos de retentativa.

---

### 4. Ferramentas, Procedimentos e Comandos

#### 4.1. Gerenciamento de Navegadores Playwright

*   **Instalação:** `playwright install` é mandatório no processo de `init`.
*   **Localização:** Os navegadores ficam em `./.playwright-browsers/`.
*   **CUIDADO com `git clean`:** O comando `git clean -fdx` **APAGARÁ** os navegadores. Use `git clean -fd` ou revise o que será apagado. Se removido, reinstale com `playwright install`.

#### 4.2. Procedimento de Gerenciamento do Servidor Django

Ao iniciar ou reiniciar o servidor, siga estas etapas para um ambiente limpo:
1.  **Liberar Porta:** Certifique-se de que a porta 8000 está livre (`lsof -i :8000` e `kill -9 <PID>`).
2.  **Limpar Banco de Dados:** Execute `python manage.py cleanup_automation_data`.
3.  **Limpar Arquivos Temporários:** Execute `python manage.py cleanup_media`.
4.  **Limpar Logs:** Remova arquivos de log antigos (`logs/`).
5.  **Iniciar Servidor:** Inicie o servidor (ex: `python manage.py runserver`).

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