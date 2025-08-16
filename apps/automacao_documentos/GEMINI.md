**Instrução:** Por favor, responda sempre em português.

# Diretrizes Específicas para o App: automacao_documentos

**Contexto:** Este arquivo especifica o **framework orquestrador** para todas as automações do projeto. As regras aqui são a base que outros apps de automação (como o `automacao_ipiranga`) devem implementar.

---

### 1. Visão Geral e Responsabilidade

* **Objetivo do App:** Servir como o **orquestrador central**. Ele define a arquitetura, os modelos de dados e o fluxo de negócio padrão para o registro, disparo e monitoramento de robôs de automação.
* **Responsabilidade:** Este app é responsável pelo **"O QUÊ"** (a estrutura da automação), enquanto os apps implementadores são responsáveis pelo **"COMO"** (a lógica específica de cada robô).

---

### 2. Dependências Críticas

* **`playwright`:** A versão deve ser fixada para garantir a estabilidade das automações. A versão testada e aprovada é `1.54.0`. Garanta que `playwright==1.54.0` esteja no `pyproject.toml`.

---

### 3. Arquitetura do Framework

Qualquer nova automação no projeto Orchestra deve se conformar a esta arquitetura:

* **Modelos Base (a serem definidos neste app):**
    * `Automacao(models.Model)`: Registra cada tipo de automação (Ex: "Ipiranga - Atualização de CIPP").
    * `ExecucaoAutomacao(models.Model)`: Registra cada disparo de uma automação, contendo status, `ForeignKey` para `Automacao`, e log.

* **Fluxo Padrão de Orquestração (a ser seguido pelos implementadores):**
    1.  Um evento externo cria um registro em um modelo "gatilho" no app implementador.
    2.  Um sinal `post_save` nesse modelo gatilho detecta a nova entrada.
    3.  O sinal dispara o `custom command` correspondente em um **subprocesso**, seguindo a regra de usar o caminho absoluto do python do `.venv`.
    4.  O `custom command` executa a lógica do robô, atualiza o status e garante a limpeza de recursos em um bloco `finally`.
    5.  **Limpeza de Recursos:** É mandatório que os apps implementadores garantam a limpeza de quaisquer arquivos ou registros temporários.
    6.  **Gerenciamento de Tempo Limite e Execução Assíncrona:** Para `custom commands` de longa duração (OCR, web scraping), é **mandatório** que sejam implementados de forma assíncrona (`asyncio`) e incluam mecanismos de tempo limite (ex: `asyncio.wait_for`) para evitar que fiquem presos indefinidamente.
