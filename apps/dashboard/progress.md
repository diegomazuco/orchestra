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
- **Diagnóstico:** Suspeita de que o problema estava no `signals.py` ou em alguma configuração inicial.
- **Tentativa 1: Desativar `signals.py`:** Comentado todo o código em `apps/automacao_ipiranga/signals.py` para isolar o problema. O servidor ainda não iniciou.
- **Tentativa 2: Depuração com `print` no `settings.py`:** Adicionados prints de depuração em `core/settings.py` para rastrear o carregamento das configurações. Todos os prints foram exibidos no log, indicando que o `settings.py` é lido completamente.
- **Tentativa 3: Desativar apps em `INSTALLED_APPS`:** Comentados todos os apps personalizados (`apps.automacao_documentos`, `apps.dashboard`, `apps.automacao_ipiranga`, `apps.common`) em `core/settings.py`. O servidor ainda não iniciou.
- **Tentativa 4: `python manage.py check`:** Executado `python manage.py check` para verificar a integridade do projeto. O comando falhou com `RuntimeError: Model class apps.automacao_ipiranga.models.VeiculoIpiranga doesn't declare an explicit app_label and isn't in an application in INSTALLED_APPS.`, indicando que o modelo `VeiculoIpiranga` estava sendo importado sem que seu app estivesse em `INSTALLED_APPS`.
- **Tentativa 5: Descomentar apps `dashboard` e `automacao_ipiranga`:** Descomentados `apps.dashboard` e `apps.automacao_ipiranga` em `INSTALLED_APPS`. O `python manage.py check` passou com sucesso.
- **Tentativa 6: Acesso via `localhost` ou `127.0.0.1`:** Orientado o usuário a tentar acessar `http://127.0.0.1:8000/` ou `http://localhost:8000/` em vez de `http://0.0.0.0:8000/` para evitar `ERR_ADDRESS_INVALID`. O problema de carregamento da página persistiu.
- **Tentativa 7: Análise de portas com `lsof`:** Verificado que o processo `python3` está escutando na porta 8000, mas a conexão ainda é recusada pelo navegador. Outras portas (3116, 45545) estão em uso por processos `node`, mas não parecem interferir diretamente.
- **Status Atual:** O servidor Django inicia e escuta na porta 8000, mas a página não carrega. A causa provável é um problema de firewall, VPN/proxy, software de segurança ou configuração de rede local na máquina do usuário, impedindo a comunicação entre o navegador e o servidor. Uma reinicialização do computador foi sugerida como próximo passo para tentar resolver problemas de rede temporários.
- **Tentativa 8: Reverter `manage.py`:** Removidas as linhas `from dotenv import load_dotenv` e `load_dotenv()` de `manage.py` para evitar carregamento duplicado ou problemático de variáveis de ambiente. O problema de carregamento da página persistiu.
- **Tentativa 9: Depuração com `print` no `settings.py` (mais detalhada):** Adicionados prints de depuração em várias seções do `core/settings.py` para rastrear o ponto exato de travamento. Todos os prints foram exibidos no log, indicando que o `settings.py` é lido completamente. O problema persiste após a leitura completa do `settings.py`.