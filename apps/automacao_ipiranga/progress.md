## 08/08/2025 - Correção do Gatilho de Automação

- **Problema:** A automação disparada por sinal (`signals.py`) falhava silenciosamente. O processo não encontrava as dependências do projeto, como Playwright e Django.

- **Diagnóstico:** A causa raiz foi identificada como o `subprocess.Popen` que chamava o `custom command`. Ele usava o Python padrão do sistema, em vez do executável específico do ambiente virtual (`.venv`) do projeto.

- **Solução:** O arquivo `signals.py` foi modificado para usar o caminho absoluto e explícito para `.venv/bin/python`. Isso garantiu que o subprocesso da automação seja sempre executado com o ambiente e as dependências corretas, resolvendo a falha de inicialização.

## 08/08/2025 - Ajuste na Extração de Dados do PDF

- **Problema:** A automação não estava extraindo corretamente o número do certificado e a data de vencimento do PDF, resultando em valores "N/A" e falha no preenchimento dos campos no portal.
- **Solução:** As expressões regulares em `apps/automacao_ipiranga/management/commands/automacao_documentos_ipiranga.py` foram ajustadas para:
    - Número do documento: de `r"([A-Z0-9]{1,3}\.\d{3}\.\d{3})"` para `r"(\d{2}\.\d{3}\.\s*\d{3})"`
    - Data de vencimento: de `r"\b(\d{2}/[A-Z]{3}/\d{2})\b"` para `r"(\d{2}/[A-Z]{3}/\d{2})"`
  Esses ajustes visam melhorar a precisão da extração de dados via OCR.
