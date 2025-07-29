# Diretrizes Específicas para o App: automacao_ipiranga

**Contexto:** Este arquivo complementa o `GEMINI.md` principal da raiz do projeto "Orchestra" e o `GEMINI.md` do app `automacao_documentos`. As regras e o contexto aqui definidos têm **precedência** para qualquer tarefa relacionada a este app.

---

### 0. Contexto do App

Ao iniciar qualquer tarefa relacionada a este app, leia e analise o arquivo `progress.md` localizado neste diretório (`apps/automacao_ipiranga/progress.md`) para carregar o histórico de ações e o contexto atual do app.

### 1. Visão Geral do App

*   **Objetivo do App:** Este app é responsável por automatizar processos e interações especificamente com o portal Ipiranga para gestão de documentos e informações relacionadas a veículos.



### 2. Dependências e Restrições Específicas

*   **Exceção Crítica de Pacotes:** Nenhuma definida até o momento. (Avaliar a necessidade de fixar versões de pacotes de web scraping como `selenium` ou `playwright` se forem utilizados, para evitar que atualizações do browser quebrem a automação).

*   **Fontes de Dados Adicionais:**
    *   **Principal:** Portal Ipiranga.

---

### 3. Contexto Técnico do App

*   **Modelos Principais (Sugestões Iniciais):**
    *   `VeiculoIpiranga`: Para armazenar dados de veículos específicos do portal Ipiranga (placa, renavam, status de documentos, etc.).

*   **Lógica de Negócio Chave:** A lógica principal envolve a criação de "robôs" (web scrapers) para interagir com o portal Ipiranga. Esses robôs serão executados periodicamente através de `custom commands` do Django (gerenciados por um `cron` no servidor) para coletar e atualizar as informações nos modelos do banco de dados. O app também deve prover uma interface para visualização dos dados coletados e geração de relatórios.

*   **Comandos de Teste Específicos:**
    *   Para rodar os testes apenas deste app com relatório de cobertura:
        ```bash
        pytest apps/automacao_ipiranga/ --cov=apps.automacao_ipiranga --cov-report=html
        ```

---

### 4. Exemplos de Prompts para este App

> "Na aplicação `automacao_ipiranga`, crie o modelo `VeiculoIpiranga` com campos para placa e renavam. Gere a migração e registre o modelo no `admin.py`."

> "Crie um custom command do Django chamado `sincronizar_veiculos_ipiranga`. O comando deve buscar veículos no portal Ipiranga e atualizar o status no modelo `VeiculoIpiranga`."

---


