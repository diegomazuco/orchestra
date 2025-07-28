# Diretrizes Específicas para o App: automacao_ibama

**Contexto:** Este arquivo complementa o `GEMINI.md` principal da raiz do projeto "Orchestra". As regras e o contexto aqui definidos têm **precedência** para qualquer tarefa relacionada a este app.

---

### 0. Contexto do App

Ao iniciar qualquer tarefa relacionada a este app, leia e analise o arquivo `progress.md` localizado neste diretório (`apps/automacao_ibama/progress.md`) para carregar o histórico de ações e o contexto atual do app.

### 1. Visão Geral do App

* **Objetivo do App:** Este app é responsável por automatizar processos e interações com sistemas do IBAMA. As funcionalidades incluem o monitoramento de licenças ambientais, a extração de dados de sistemas públicos, o acompanhamento de processos e a geração de relatórios de conformidade.

---

### 2. Dependências e Restrições Específicas

* **Exceção Crítica de Pacotes:** Nenhuma definida até o momento. (Avaliar a necessidade de fixar versões de pacotes de web scraping como `selenium` ou `playwright` se forem utilizados, para evitar que atualizações do browser quebrem a automação).

* **Fontes de Dados Adicionais:**
    * **Principal:** Sistemas de consulta pública do IBAMA (ex: consulta de processos, licenciamento ambiental).
    * **Secundária:** Possível consumo de APIs do Portal de Dados Abertos do governo federal.

---

### 3. Contexto Técnico do App

* **Modelos Principais (Sugestões Iniciais):**
    * `ProcessoIBAMA`: Para armazenar dados de um processo específico (número, interessado, status, histórico).
    * `LicencaAmbiental`: Para rastrear licenças (número, tipo, data de emissão, data de validade, órgão emissor).
    * `TarefaAutomacao`: Para agendar e registrar a execução de rotinas automáticas (ex: verificação diária de processos).
    * `LogExecucao`: Para armazenar os logs detalhados de cada `TarefaAutomacao` (sucesso, falha, dados coletados).

* **Lógica de Negócio Chave:** A lógica principal envolve a criação de "robôs" (web scrapers ou consumidores de API) para interagir com as fontes de dados do IBAMA. Esses robôs serão executados periodicamente através de `custom commands` do Django (gerenciados por um `cron` no servidor) para coletar e atualizar as informações nos modelos do banco de dados. O app também deve prover uma interface para visualização dos dados coletados e geração de relatórios.

* **Comandos de Teste Específicos:**
    * Para rodar os testes apenas deste app com relatório de cobertura:
        ```bash
        pytest apps/automacao_ibama/ --cov=apps.automacao_ibama --cov-report=html
        ```

---

### 4. Exemplos de Prompts para este App

> "Na aplicação `automacao_ibama`, crie o modelo `Protocolo` com um relacionamento `ForeignKey` para `ProcessoIBAMA`, um campo `descricao` (TextField) e uma data de criação. Gere a migração e registre o modelo no `admin.py`."

> "Crie um custom command do Django chamado `verificar_prazos_licencas`. O comando deve buscar todas as `LicencasAmbientais` ativas com data de validade para os próximos 60 dias e criar um registro de `LogExecucao` com o status 'ALERTA' para cada uma delas."

---

### 5. Fluxo de Trabalho e Automação (Git)

* **Commits Detalhados:** Ao preparar um commit, a mensagem deve ser um resumo detalhado de **todo o processo realizado** desde o último commit. Ela deve explicar o "porquê" das mudanças, não apenas o "o quê".
* **Push Completo e Seguro:**
    1.  **Sincronizar:** Sempre execute `git pull --rebase` antes de fazer o push para integrar as mudanças remotas.
    2.  **Verificar Status:** Use `git status` para garantir que todos os arquivos relevantes (novos ou modificados) estão na área de stage.
    3.  **Executar Push:** Execute `git push`.
    4.  **Tratamento de Falhas:** **PARE** e avise o usuário imediatamente em caso de qualquer falha (ex: `merge conflict`, `push rejected`).
