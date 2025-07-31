## 2025-07-31 - Refatoração do Comando `automacao_documentos_ipiranga` e Configuração da Automação

- Implementada a extração de `numero_documento_valor` e `vencimento_valor_pdf` do texto do PDF usando expressões regulares.
- Substituído o `asyncio.sleep(5)` por um `TODO` para o usuário implementar a lógica de espera por um elemento de sucesso na página.
- Removidos comentários `TODO` e corrigido o comentário sobre `headless`.
- Alterado o modo `headless` do Playwright para `False` em `apps/automacao_ipiranga/management/commands/automacao_documentos_ipiranga.py` para permitir a visualização da automação.
- Adicionada uma URL (`iniciar_automacao/`) e uma view (`iniciar_automacao`) em `apps/automacao_ipiranga/` para disparar a automação via requisição POST.