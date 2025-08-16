# Histórico de Progresso do App: Dashboard

Este arquivo registra as principais ações e configurações realizadas especificamente no app "Dashboard".

## 12/08/2025 - Resumo do Dia de Trabalho e Próximos Passos

- **Problemas Persistentes:** A automação Playwright ainda não consegue navegar para as URLs "Vencidos" e "À vencer" após a autenticação, ficando presa no dashboard. O problema de limpeza de arquivos temporários na pasta `media/certificados_veiculos/` também persistiu, indicando que o arquivo é recriado rapidamente pela automação.
- **Ações Realizadas:**
    - Implementação de um tempo limite global de 30 segundos para a automação Playwright em `automacao_documentos_ipiranga.py` para evitar travamentos prolongados do navegador.
    - Adição de logging mais granular na função `extract_text_from_pdf_image` em `apps/common/services.py` para depurar o processo de OCR.
    - Refinamento da estratégia de limpeza de dados: a chamada para `cleanup_automation_data` foi removida do `AppConfig.ready()` e movida para o bloco `finally` em `automacao_documentos_ipiranga.py`, e a responsabilidade pela execução manual de `cleanup_automation_data` antes de cada início do servidor foi explicitamente atribuída a mim.
    - Atualização dos arquivos `GEMINI.md` e `progress.md` relevantes para refletir as mudanças na estratégia de limpeza e a implementação do tempo limite.
- **Próximos Passos (Foco Principal):**
    - **Depuração da Navegação:** A prioridade é depurar a lógica de navegação após a autenticação. Isso incluirá a adição de esperas explícitas por elementos no dashboard e logging detalhado das URLs após cada `page.goto()`.
    - **Revisão do OCR:** Com o logging granular, será possível identificar o ponto exato de falha na extração de texto do PDF, permitindo ajustes mais precisos.
    - **Robustez da Limpeza:** Continuar monitorando a limpeza de arquivos temporários para garantir que a automação não deixe resíduos.

## 11/08/2025 - Atualização de Dependências

- **Atualização de Dependências:**
    - O arquivo `apps/dashboard/views.py` foi modificado devido à instalação de todas as dependências do projeto e ferramentas de desenvolvimento (`pytest`, `ruff`, `pyright`) utilizando `uv pip install --group all`.

## 10/08/2025 - Análise e Refatoração de Documentação

- **Análise Rigorosa do Projeto:** Contribuição para a análise detalhada de toda a estrutura do projeto Orchestra.
- **Refatoração de `GEMINI.md`:** O arquivo `GEMINI.md` deste app (se existir) foi lido em todas as suas versões históricas, analisado e refatorado para conter as melhores e mais robustas instruções. A versão refatorada foi substituída no seu devido local.
- **Refatoração de `progress.md`:** Este arquivo `progress.md` foi lido em todas as suas versões históricas, analisado e refatorado para consolidar e refinar o histórico de desenvolvimento do app. A versão refatorada será substituída no seu devido local.

## 01/08/2025 - Processamento de Documentos e Ajustes Gerais

- **View `process_documents_view`:** Confirmado o funcionamento correto da view para receber múltiplos arquivos PDF, extrair informações do nome do arquivo e criar registros `CertificadoVeiculo` no banco de dados, disparando a automação via sinal `post_save` para cada certificado.
- **Remoção de Testes:** Todos os arquivos de teste (`tests.py`) foram removidos do projeto, incluindo os testes específicos deste app.
- **Configuração de Ferramentas:** Contribuição para a implementação de `pre-commit` com hooks para `ruff` (formatação e linting) e `pyright` (verificação de tipos).
- **Instalação de Ferramentas de Performance:** Contribuição para a adição de `line-profiler` e `snakeviz` para análise de performance.
- **Refatoração Completa:** Contribuição para a remoção de testes (`tests.py`), configuração de `Ruff` e atualização de documentação.

## 30/07/2025 - Integração com Modelos Django e Automação via Sinal

- **Modificação da `process_documents_view`:** A view foi refatorada para remover a chamada direta ao comando `automacao_documentos_ipiranga`, importar os modelos `VeiculoIpiranga` e `CertificadoVeiculo` do app `automacao_ipiranga`, extrair a placa e o nome do certificado do nome do arquivo enviado, utilizar `VeiculoIpiranga.objects.get_or_create()` para garantir a existência do veículo, e criar um novo objeto `CertificadoVeiculo` com status `pendente`, disparando a automação indiretamente pelo sinal `post_save`.
- **Remoção de Diretório Temporário:** A criação e uso do diretório `temp_uploads` foi removida.
- **Correção de Segurança:** O decorador `@csrf_exempt` foi removido da `process_documents_view` para reabilitar a proteção CSRF.

## 28/07/2025 - Criação do Projeto e Dashboard Inicial

- **Criação do Projeto Orchestra:** Inicialização do projeto Django "Orchestra".
- **Criação e Configuração do App `dashboard`:** Implementação da view `orchestra_view` e template `orchestra.html` para a página principal.
- **Funcionalidade de Upload e Processamento (Inicial):** Adicionada a funcionalidade de exibir arquivos selecionados e um botão "Iniciar Processamento" em `orchestra.html`. Criado o endpoint `/process-documents/` e a view `process_documents_view` para receber os arquivos enviados pelo frontend.
