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
    * `Automacao(models.Model)`: Modelo para registrar cada tipo de automação (Ex: "Ipiranga - Atualização de CIPP"). Deve conter campos como `nome` e `comando_django`.
    * `ExecucaoAutomacao(models.Model)`: Registra cada disparo de uma automação, contendo status (`pendente`, `processando`, `sucesso`, `falha`), `ForeignKey` para `Automacao`, e um campo de log.

* **Fluxo Padrão de Orquestração (a ser seguido pelos implementadores):**
    1.  Um evento externo (ex: upload) cria um registro em um modelo "gatilho" no app implementador.
    2.  Um sinal `post_save` nesse modelo gatilho detecta a nova entrada.
    3.  O sinal dispara o `custom command` correspondente em um **subprocesso**, seguindo a regra de usar o caminho absoluto do python do `.venv`.
    4.  O `custom command` executa a lógica do robô, atualiza o status (seja no modelo gatilho ou em um `ExecucaoAutomacao`) e garante a limpeza de recursos em um bloco `finally`.
    5.  **Limpeza de Recursos Temporários:** É mandatório que os apps implementadores garantam a limpeza de quaisquer arquivos ou registros temporários gerados durante a automação, tanto ao final da execução do robô quanto no ciclo de vida do servidor (início, reinício, término).
    6.  **Gerenciamento de Tempo Limite:** O `custom command` deve implementar um mecanismo de tempo limite para evitar que a automação fique presa indefinidamente, garantindo o fechamento do navegador e a liberação de recursos.
