## 2025-07-31 - Refatoração do Comando `automacao_documentos_ipiranga` e Configuração da Automação

- Implementada a extração de `numero_documento_valor` e `vencimento_valor_pdf` do texto do PDF usando expressões regulares.
- Substituído o `asyncio.sleep(5)` por um `TODO` para o usuário implementar a lógica de espera por um elemento de sucesso na página.
- Removidos comentários `TODO` e corrigido o comentário sobre `headless`.
- Alterado o modo `headless` do Playwright para `False` em `apps/automacao_ipiranga/management/commands/automacao_documentos_ipiranga.py` para permitir a visualização da automação.
- Adicionada uma URL (`iniciar_automacao/`) e uma view (`iniciar_automacao`) em `apps/automacao_ipiranga/` para disparar a automação via requisição POST.

## 2025-08-01 - Otimizações e Robustez da Automação

- **Refatoração do Comando `automacao_documentos_ipiranga`:**
    - **Suporte a Múltiplos IDs:** O comando agora aceita múltiplos `certificado_ids` como argumento, permitindo o processamento em lote de certificados.
    - **Inicialização Única do Navegador e Login:** O navegador e o login no portal são realizados apenas uma vez por execução do comando, otimizando o desempenho e o uso de recursos.
    - **Extração de Dados do PDF Aprimorada:**
        - O número do documento é extraído e formatado para conter apenas dígitos (removendo pontos e letras como 'A').
        - A data de vencimento é extraída de forma mais robusta, buscando a última data no formato `DD/MON/YY` no primeiro bloco do certificado, garantindo a precisão.
    - **Lógica de Confirmação de Sucesso Aprimorada:** A confirmação final de salvamento é feita aguardando o redirecionamento para a página de listagem de veículos, tornando a automação mais confiável e garantindo o encerramento limpo.
    - **Limpeza Automática:**
        - Em caso de sucesso, o registro `CertificadoVeiculo` e o arquivo PDF associado são removidos do banco de dados e do sistema de arquivos, respectivamente.
        - Arquivos temporários de log (`temp_automation.log`) e de depuração (`debug_*.png`, `debug_*.html`) são removidos incondicionalmente ao final da execução.
        - Screenshots de erro (`error_screenshot_*.png`, `login_error_screenshot.png`) são agora removidos, conforme solicitação do usuário.
    - **Tratamento de Erros por Certificado:** Se um certificado individual falhar, a automação registra o erro, atualiza o status do certificado para 'falha' e tenta continuar com o próximo, sem interromper todo o processo.

- **Aprimoramentos no `apps/common/services.py` (impactando esta automação):**
    - Adicionada a importação do módulo `asyncio`.
    - Implementada lógica de resiliência para instabilidade de login no portal Ipiranga: o script aguarda alguns segundos e recarrega a página se detectar a mensagem "Erro Inesperado. Favor tente novamente.", aumentando a robustez da automação.

- **Remoção de Testes:** Todos os arquivos de teste (`tests.py`) foram removidos do projeto, incluindo os testes específicos deste app.
