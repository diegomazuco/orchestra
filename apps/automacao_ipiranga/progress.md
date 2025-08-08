## 08/08/2025 - Ajuste na Extração de Dados do PDF

- **Problema:** A automação não estava extraindo corretamente o número do certificado e a data de vencimento do PDF, resultando em valores "N/A" e falha no preenchimento dos campos no portal.
- **Solução:** As expressões regulares em `apps/automacao_ipiranga/management/commands/automacao_documentos_ipiranga.py` foram ajustadas para:
    - Número do documento: de `r"([A-Z0-9]{1,3}\.\d{3}\.\d{3})"` para `r"(\d{2}\.\d{3}\.\s*\d{3})"`
    - Data de vencimento: de `r"\b(\d{2}/[A-Z]{3}/\d{2})\b"` para `r"(\d{2}/[A-Z]{3}/\d{2})"`
  Esses ajustes visam melhorar a precisão da extração de dados via OCR.
