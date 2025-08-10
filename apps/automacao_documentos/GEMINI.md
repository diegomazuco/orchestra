# Diretrizes Específicas para o App: automacao_documentos

**Contexto:** Este arquivo complementa o `GEMINI.md` principal da raiz do projeto "Orchestra". As regras e o contexto aqui definidos têm **precedência** para qualquer tarefa relacionada a este app.

---

### 0. Contexto do App

Ao iniciar qualquer tarefa relacionada a este app, leia e analise o arquivo `progress.md` localizado neste diretório (`apps/automacao_documentos/progress.md`) para carregar o histórico de ações e o contexto atual do app.

### 1. Visão Geral do App

*   **Objetivo do App:** Este app serve como o **orquestrador central** para os processos de automação. Ele define os modelos de dados e a lógica de negócio **base** para o registro, disparo e monitoramento de robôs de automação. As implementações específicas de cada robô (ex: a interação com o portal Ipiranga) residem em seus próprios apps dedicados (ex: `apps/automacao_ipiranga`), que por sua vez utilizam a estrutura fornecida por este app.

### 2. Dependências e Restrições Específicas

*   **Exceção Crítica de Pacotes:** A versão do pacote `playwright` deve ser fixada para garantir a estabilidade das automações. A versão atualmente em uso e testada é `1.54.0`. Garanta que o `pyproject.toml` contenha a linha `playwright==1.54.0`.

*   **Fontes de Dados Adicionais:**
    *   **Principal:** Diversos portais externos (ex: Ipiranga, IBAMA, etc.).
    *   **Secundária:** Possível consumo de APIs de dados abertos ou sistemas internos.

---

### 3. Contexto Técnico do App

*   **Modelos Principais (Arquitetura Base):**
    *   `Automacao(models.Model)`: Um modelo central para registrar cada tipo de automação disponível no sistema. Ex: "Ipiranga - Atualização de CIPP", "IBAMA - Consulta de Licenças".
    *   `ExecucaoAutomacao(models.Model)`: Um registro para **cada vez** que uma automação é disparada. Contém o status (`pendente`, `processando`, `sucesso`, `falha`), um `ForeignKey` para o modelo `Automacao`, e um campo para armazenar o log detalhado da execução ou o caminho para o arquivo de log.

*   **Lógica de Negócio Chave (Fluxo Padrão):**
    1.  Um evento externo (como um upload de arquivo, um agendamento `cron`, ou uma ação manual do usuário) cria um registro de `ExecucaoAutomacao` com o status `pendente`.
    2.  Um sinal `post_save` no modelo `ExecucaoAutomacao` detecta a nova entrada.
    3.  O sinal dispara o `custom command` do Django correspondente à automação (ex: `automacao_documentos_ipiranga`), passando o ID da `ExecucaoAutomacao`.
    4.  O `custom command` executa a lógica do robô, atualizando o status da `ExecucaoAutomacao` para `processando`, e depois para `sucesso` ou `falha`, preenchendo os logs ao final.

*   **Comandos de Teste Específicos:**
    *   Para rodar os testes apenas deste app com relatório de cobertura:
        ```bash
        pytest apps/automacao_documentos/ --cov=apps.automacao_documentos --cov-report=html
        ```

---

### 4. Exemplos de Prompts para este App

> "Na aplicação `automacao_documentos`, crie o modelo `Automacao` com um campo `nome` e um campo `comando_django` para armazenar o nome do custom command a ser executado."

> "Crie o modelo `ExecucaoAutomacao` com os campos `automacao` (ForeignKey para `Automacao`), `status` (CharField com choices), `log` (TextField) e `data_inicio` / `data_fim` (DateTimeField)."
