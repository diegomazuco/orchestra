## 08/08/2025 - Diagnóstico e Correção Definitiva da Automação Playwright

- **Problema:** A automação Playwright falhava de forma intermitente e com múltiplos sintomas, incluindo: o servidor não iniciar, a automação não prosseguir após o login, e erros na extração de dados de PDFs. Além disso, arquivos e registros de banco de dados órfãos eram deixados para trás a cada falha.

- **Diagnóstico Abrangente:** Uma análise detalhada revelou uma cadeia de problemas interligados:
    1.  **Erro de Execução do Subprocesso (Causa Raiz):** O `signals.py` chamava `python` diretamente, usando o Python do sistema em vez do Python do ambiente virtual (`.venv`). Isso causava um `ModuleNotFoundError` silencioso no subprocesso, que não conseguia encontrar as dependências do projeto (Django, Playwright), fazendo com que a automação falhasse antes mesmo de começar a logar.
    2.  **Erro de Extração de OCR:** A busca pelo texto "CERTIFICADO DE INSPEÇÃO" no PDF era muito rígida. O OCR frequentemente lia a string como "CERTIFICADO DE INSPEO", causando uma falha na extração de dados e interrompendo o script.
    3.  **Falta de Limpeza em Caso de Falha:** A lógica para deletar o `CertificadoVeiculo` e o arquivo PDF associado só era executada em caso de sucesso. Qualquer falha no processo deixava lixo no sistema, explicando os IDs incrementais a cada nova tentativa.

- **Soluções Estruturais Aplicadas:**
    - **Caminho Explícito do Python:** O `signals.py` foi corrigido para usar o caminho absoluto do executável do Python do ambiente virtual (`.venv/bin/python`), garantindo que a automação sempre rode com as dependências corretas.
    - **Regex Flexível para OCR:** A expressão regular no comando de automação foi alterada para `r"(CERTIFICADO DE INSPE.*?)"`, tornando a busca pelo bloco de texto tolerante a falhas de OCR.
    - **Limpeza Robusta com `finally`:** A lógica de exclusão do registro e do arquivo foi movida para um bloco `finally` dentro do `custom command`. Isso garante que a limpeza seja executada **sempre**, independentemente do sucesso ou falha da automação.

- **Resultado:** A automação tornou-se significativamente mais robusta, confiável e resiliente. O processo de debugging e limpeza foi solidificado, evitando problemas futuros e facilitando a manutenção.
