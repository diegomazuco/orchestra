## 08/08/2025 - Correção do Gatilho de Automação

- **Problema:** A automação disparada por sinal (`signals.py`) falhava silenciosamente. O processo não encontrava as dependências do projeto, como Playwright e Django.

- **Diagnóstico:** A causa raiz foi identificada como o `subprocess.Popen` que chamava o `custom command`. Ele usava o Python padrão do sistema, em vez do executável específico do ambiente virtual (`.venv`) do projeto.

- **Solução:** O arquivo `signals.py` foi modificado para usar o caminho absoluto e explícito para `.venv/bin/python`. Isso garantiu que o subprocesso da automação seja sempre executado com o ambiente e as dependências corretas, resolvendo a falha de inicialização.
