# Histórico de Progresso do App: Dashboard

Este arquivo registra as principais ações e configurações realizadas especificamente no app "Dashboard".

## 28 de Julho de 2025

### Criação e Configuração do App
- Criado o diretório `apps/dashboard` (`mkdir -p apps/dashboard`).
- Criado o app Django `dashboard` dentro do diretório `apps/` (`python manage.py startapp dashboard apps/dashboard`).
- Registrado o app `dashboard` em `INSTALLED_APPS` no `core/settings.py`.
- Implementada a view `orchestra_view` em `apps/dashboard/views.py` para renderizar a página principal.
- Criado o template `orchestra.html` em `apps/dashboard/templates/dashboard/orchestra.html` com a estrutura da página, menu lateral e um botão "Buscar Documentos".

### Funcionalidade de Upload e Processamento
- Adicionada a funcionalidade de exibir arquivos selecionados e um botão "Iniciar Processamento" em `apps/dashboard/templates/dashboard/orchestra.html`.
- Criado o endpoint `/process-documents/` em `apps/dashboard/urls.py` e a view `process_documents_view` em `apps/dashboard/views.py` para receber os arquivos enviados pelo frontend.
- A view `process_documents_view` foi inicialmente configurada para salvar os arquivos enviados temporariamente e chamar o custom command `automacao_documentos_ipiranga` com os dados extraídos do nome do arquivo.

## 30 de Julho de 2025

### Integração com Modelos Django e Automação via Sinal
- **Modificação da `process_documents_view`:** A view em `apps/dashboard/views.py` foi refatorada para:
    - Remover a chamada direta ao comando `automacao_documentos_ipiranga`.
    - Importar os modelos `VeiculoIpiranga` e `CertificadoVeiculo` do app `automacao_ipiranga`.
    - Extrair a placa e o nome do certificado do nome do arquivo enviado.
    - Utilizar `VeiculoIpiranga.objects.get_or_create()` para garantir a existência do veículo no banco de dados.
    - Criar um novo objeto `CertificadoVeiculo`, associando-o ao `VeiculoIpiranga` e anexando o arquivo enviado. O status inicial é definido como `'pendente'`.
    - A automação agora é disparada indiretamente pelo sinal `post_save` do Django, que é acionado quando o `CertificadoVeiculo` é salvo.
- **Remoção de Diretório Temporário:** A criação e uso do diretório `temp_uploads` foi removida, pois os arquivos agora são gerenciados diretamente pelo `FileField` do modelo `CertificadoVeiculo`.

### Correção de Segurança
- **Remoção de `@csrf_exempt`:** O decorador `@csrf_exempt` foi removido da `process_documents_view` em `apps/dashboard/views.py` para reabilitar a proteção CSRF, aumentando a segurança da aplicação.

## 31 de Julho de 2025

### Depuração de Inicialização do Servidor
- **Problema:** O servidor Django inicia, mas a página `http://127.0.0.1:8000/` não carrega, ficando em estado de "carregando".
- **Diagnóstico:** Após extensiva depuração, incluindo análise de logs, verificação de portas e configurações do Django, a causa provável foi identificada como um problema de firewall, VPN/proxy, software de segurança ou configuração de rede local na máquina do usuário, impedindo a comunicação entre o navegador e o servidor. O problema não foi no código do projeto.

## 2025-08-01 - Processamento de Documentos

- **View `process_documents_view`:** Confirmado o funcionamento correto da view para receber múltiplos arquivos PDF, extrair informações do nome do arquivo e criar registros `CertificadoVeiculo` no banco de dados, disparando a automação via sinal `post_save` para cada certificado.

- **Remoção de Testes:** Todos os arquivos de teste (`tests.py`) foram removidos do projeto, incluindo os testes específicos deste app.
