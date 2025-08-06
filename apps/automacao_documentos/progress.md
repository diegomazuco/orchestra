## 06/08/2025 - Diagnóstico e Depuração da Automação Playwright

- **Problema de Execução do Subprocesso:**
    - O subprocesso que executa o script Playwright não estava produzindo logs no `automation.log`.
    - **Diagnóstico:** O `stdout` e `stderr` do `subprocess.Popen` estavam sendo redirecionados para `subprocess.DEVNULL`.
    - **Solução:** Alterado o redirecionamento de `stdout` e `stderr` para `subprocess.PIPE` em `apps/automacao_ipiranga/signals.py` para capturar a saída no `orchestra.log`.
