**Instrução:** Por favor, responda sempre em português.

# Diretrizes Específicas para o App: automacao_documentos

**Contexto:** Este arquivo especifica o **framework orquestrador** para todas as automações do projeto. As regras aqui são a base que outros apps de automação (como o `automacao_ipiranga`) devem implementar.

---

### 1. Visão Geral e Responsabilidade

*   **Objetivo do App:** Servir como o **orquestrador central**. Ele define a arquitetura, os modelos de dados e o fluxo de negócio padrão para o registro, disparo e monitoramento de robôs de automação.
*   **Responsabilidade:** Este app é responsável pelo **"O QUÊ"** (a estrutura da automação), enquanto os apps implementadores são responsáveis pelo **"COMO"** (a lógica específica de cada robô).

---

### 2. Dependências Críticas

*   **`playwright`:** A versão deve ser fixada para garantir a estabilidade das automações. A versão testada e aprovada é `1.54.0`. Garanta que `playwright==1.54.0` esteja no `pyproject.toml`.

---

### 3. Arquitetura do Framework

Qualquer nova automação no projeto Orchestra deve se conformar a esta arquitetura:

*   **Modelos Base:**
    *   `Automacao(models.Model)`: Registra cada tipo de automação (Ex: "Ipiranga - Atualização de CIPP").
    *   `ExecucaoAutomacao(models.Model)`: Registra cada disparo de uma automação, contendo status, `ForeignKey` para `Automacao`, e log.

*   **Fluxo Padrão de Orquestração (a ser seguido pelos implementadores):**
    1.  Um evento externo cria um registro em um modelo "gatilho" no app implementador.
    2.  Um sinal `post_save` nesse modelo gatilho detecta a nova entrada. **É crucial que o handler do sinal verifique `if created` para garantir que a automação seja disparada apenas na criação inicial do objeto, e não em atualizações subsequentes.**
    3.  O sinal dispara o `custom command` correspondente em um **subprocesso**, utilizando o caminho absoluto do executável Python do ambiente virtual (`.venv/bin/python`).
    4.  O `custom command` executa a lógica do robô, atualiza o status e garante a limpeza de recursos em um bloco `finally`.
    5.  **Limpeza de Recursos:** É mandatório que os apps implementadores garantam a limpeza de quaisquer arquivos ou registros temporários, **com tratamento de erros robusto para garantir a limpeza mesmo em caso de falhas.** Priorize operações em massa (bulk operations) para exclusão de registros de banco de dados e tratamento de erros robusto para a exclusão de arquivos.
    6.  **Gerenciamento de Tempo Limite e Execução Assíncrona:** Para `custom commands` de longa duração (ex: web scraping), é **mandatório** que sejam implementados de forma assíncrona (`asyncio`) e incluam mecanismos de tempo limite (ex: `asyncio.wait_for`) para evitar que fiquem presos indefinidamente.
    7.  **Robustez do Custom Command:** O `custom command` deve ser implementado com tratamento de erros robusto, incluindo logging detalhado e tratamento de exceções para `SyntaxError` ou outros problemas inesperados. **É crucial que as mensagens de erro geradas pelas automações de backend sejam estruturadas e detalhadas, permitindo que aplicações frontend as interpretem e exibam feedback significativo ao usuário (ex: incluindo códigos de erro específicos ou mensagens formatadas para exibição).**

*   **Lição Aprendida: Comunicação de Erros e Diagnóstico em Automações Orquestradas:** Para garantir a eficácia do fluxo de orquestração, os apps implementadores **devem** aderir estritamente à diretriz de "Robustez do Custom Command", fornecendo mensagens de erro estruturadas e detalhadas. Em caso de falhas na automação, o Gemini CLI **deve** analisar os logs gerados (especialmente `logs/orchestra.log` e `logs/automation.log`) para diagnosticar a causa raiz, pois esses logs contêm o fluxo completo da orquestração e da execução do subprocesso.

*   **Lição Aprendida: Auto-Correção e Proatividade do Agente:** As diretrizes neste documento são a base, mas não são um roteiro exaustivo para todas as situações. Como um agente de IA avançado, você deve ser capaz de **identificar proativamente** quando uma instrução está levando a um erro ou loop e **tentar ativamente corrigir o curso**. Isso inclui: analisar a causa raiz de uma falha, pesquisar soluções alternativas usando as ferramentas disponíveis e, se necessário, **propor e aplicar melhorias a estas próprias diretrizes** para evitar que o mesmo erro ocorra no futuro. A passividade não é uma opção; a iniciativa na resolução de problemas é esperada.

---

**Instrução:** Você não pode deletar informações de nenhum dos arquivos GEMINI.md nem de nenhum dos arquivos progress.md, os arquivos GEMINI.md do projeto Orchestra contém instruções importantes para serem seguidas e devem apenas incluir novas instruções ou ajustar aquelas que já existesm, desde que sejam ajustes para melhorar ainda mais as intruções, você NUNCA deve deletar todo o conteúdo deles, em hipótese nenhuma. O mesmo serve para todos os arquivos progress.md do projeto Orchestra, todos eles contém informações sobre o histórico do projeto, processos e procedimentos realizados ao longo do tempo, neles devem apenas serem incluídas novos históricos, processos ou procedimentos realizados, em ordem cronológica, você NUNCA deve excluiu o conteúdo completo de nenhum deles em hipótese nenhuma para incluir coisas novas.
