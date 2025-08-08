## 08/08/2025 - Refinamento do Processo de Automação

- **Contexto:** Durante a depuração da automação do app `automacao_ipiranga`, foi identificado um problema fundamental na forma como os subprocessos eram disparados a partir dos sinais do Django.

- **Problema:** O subprocesso que executava o `custom command` não utilizava o ambiente virtual (`.venv`) do projeto, levando a falhas silenciosas por falta de dependências.

- **Solução Aplicada (no app `automacao_ipiranga`):** A lógica em `signals.py` foi corrigida para apontar explicitamente para o executável do Python dentro do `.venv`. Esta solução, embora aplicada em um app específico, estabelece um padrão para todas as futuras automações orquestradas por este app, garantindo que elas sejam executadas no contexto correto.
