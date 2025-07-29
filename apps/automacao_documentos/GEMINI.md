# Diretrizes Específicas para o App: automacao_documentos

**Contexto:** Este arquivo complementa o `GEMINI.md` principal da raiz do projeto "Orchestra". As regras e o contexto aqui definidos têm **precedência** para qualquer tarefa relacionada a este app.

---

### 0. Contexto do App

Ao iniciar qualquer tarefa relacionada a este app, leia e analise o arquivo `progress.md` localizado neste diretório (`apps/automacao_documentos/progress.md`) para carregar o histórico de ações e o contexto atual do app.

### 1. Visão Geral do App

* **Objetivo do App:** Este app é responsável por automatizar processos e interações com diversos sistemas externos para atualização e gestão de documentos. Ele serve como um contêiner para diferentes automações, cada uma focada em um portal ou tipo de documento específico.



### 2. Dependências e Restrições Específicas

* **Exceção Crítica de Pacotes:** Nenhuma definida até o momento. (Avaliar a necessidade de fixar versões de pacotes de web scraping como `selenium` ou `playwright` se forem utilizados, para evitar que atualizações do browser quebrem a automação).

* **Fontes de Dados Adicionais:**
    * **Principal:** Diversos portais externos (ex: Ipiranga, IBAMA, etc.).
    * **Secundária:** Possível consumo de APIs de dados abertos ou sistemas internos.

---

### 3. Contexto Técnico do App

* **Modelos Principais (Sugestões Iniciais):**
    * `Documento`: Para armazenar dados de documentos (tipo, número, status, data de validade, arquivo, portal de origem).
    * `Portal`: Para registrar os portais externos com os quais o sistema interage (nome, URL base, credenciais).
    * `Automacao`: Para agendar e registrar a execução de rotinas automáticas (ex: `automacao_documentos_ipiranga`).
    * `LogExecucaoAutomacao`: Para armazenar os logs detalhados de cada `Automacao` (sucesso, falha, dados coletados).

* **Lógica de Negócio Chave:** A lógica principal envolve a criação de "robôs" (web scrapers ou consumidores de API) para interagir com as fontes de dados dos portais. Esses robôs serão executados periodicamente através de `custom commands` do Django (gerenciados por um `cron` no servidor) para coletar e atualizar as informações nos modelos do banco de dados. O app também deve prover uma interface para visualização dos dados coletados e geração de relatórios.

* **Comandos de Teste Específicos:**
    * Para rodar os testes apenas deste app com relatório de cobertura:
        ```bash
        pytest apps/automacao_documentos/ --cov=apps.automacao_documentos --cov-report=html
        ```

---

### 4. Exemplos de Prompts para este App

> "Na aplicação `automacao_documentos`, crie o modelo `Portal` com campos para nome e URL. Gere a migração e registre o modelo no `admin.py`."

> "Crie um custom command do Django chamado `automacao_documentos_ibama`. O comando deve buscar documentos vencidos no portal do IBAMA e criar um registro de `LogExecucaoAutomacao` com o status 'ALERTA' para cada um deles."

---

