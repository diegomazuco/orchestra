# Histórico de Progresso do App: Common

## 14/08/2025 - Melhorias e Ajustes em Serviços Comuns

- **Atualização de URLs de Login:** As URLs de login no `login_to_portran` foram atualizadas para `https://sites2.ipiranga.com.br` para refletir o endereço correto do portal.
- **Aprimoramentos de OCR:**
    - Adicionada a função `cv2.resize` para redimensionamento de imagem, melhorando a precisão do OCR.
    - A função `determine_skew` foi atualizada para aceitar um logger e incluir logs mais detalhados.
    - A expressão regular em `extract_cipp_data` foi aprimorada para maior flexibilidade na extração de dados.

## 14/08/2025 - Ajustes de Qualidade de Código

- **Remoção de Código Comentado:** Removido código comentado relacionado a "Deskewing" em `apps/common/services.py` para aderir às diretrizes de qualidade de código e evitar `ERA001` do `ruff`.



## 13/08/2025 - Melhorias no Logging de Automação

- **Logging Detalhado:** Adicionado logging mais detalhado no arquivo `services.py` para melhorar a depuração e o rastreamento de problemas durante a execução da automação, especificamente nas funções de OCR e navegação.

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

Este arquivo registra as principais ações e configurações realizadas especificamente no app "Common".

## 12/08/2025 - Adição de Logging Granular em OCR

- **Logging Granular em OCR:** Adicionado logging mais granular à função `extract_text_from_pdf_image` em `apps/common/services.py` para depurar cada etapa do processamento de imagem e identificar gargalos na extração de texto OCR.

## 12/08/2025 - Melhoria na Extração de Dados OCR (DPI e PSM)

- **Melhoria na Extração OCR (DPI e PSM):** O arquivo `apps/common/services.py` foi atualizado para melhorar a robustez do OCR, aumentando o DPI da imagem para 600 e alterando o modo PSM (Page Segmentation Mode) do Tesseract para 3.

## 12/08/2025 - Melhoria na Extração de Dados OCR

- **Melhoria na Extração OCR:** O arquivo `apps/common/services.py` foi atualizado com uma expressão regular mais robusta para a extração do bloco "CERTIFICADO DE INSPEÇÃO" e a utilização da função `normalize_text` para lidar com erros de OCR.

## 11/08/2025 - Atualização de Dependências

- **Atualização de Dependências:**
    - O arquivo `apps/common/services.py` foi modificado devido à instalação de todas as dependências do projeto e ferramentas de desenvolvimento (`pytest`, `ruff`, `pyright`) utilizando `uv pip install --group all`.

## 10/08/2025 - Análise e Refatoração de Documentação

- **Análise Rigorosa do Projeto:** Contribuição para a análise detalhada de toda a estrutura do projeto Orchestra.
- **Refatoração de `GEMINI.md`:** O arquivo `GEMINI.md` deste app (se existir) foi lido em todas as suas versões históricas, analisado e refatorado para conter as melhores e mais robustas instruções. A versão refatorada foi substituída no seu devido local.
- **Refatoração de `progress.2md`:** Este arquivo `progress.2md` foi lido em todas as suas versões históricas, analisado e refatorado para consolidar e refinar o histórico de desenvolvimento do app. A versão refatorada será substituída no seu devido local.

## 01/08/2025 - Aprimoramentos de Robustez e Configuração de Ferramentas

- **Função `login_to_portran`:** Adicionada lógica de resiliência para instabilidade de login no portal Ipiranga, aumentando a robustez da automação.
- **Remoção de Testes:** Todos os arquivos de teste (`tests.py`) foram removidos do projeto, incluindo os testes específicos deste app.
- **Configuração de Ferramentas:** Contribuição para a implementação de `pre-commit` com hooks para `ruff` (formatação e linting) e `pyright` (verificação de tipos).
- **Instalação de Ferramentas de Performance:** Contribuição para a adição de `line-profiler` e `snakeviz` para análise de performance.
- **Refatoração Completa:** Contribuição para a remoção de testes (`tests.py`), configuração de `Ruff` e atualização de documentação.

## 30/07/2025 - Criação e Centralização de Serviços

- **Criação e Configuração do App:** Criado o app Django `common` e registrado em `INSTALLED_APPS`.
- **Centralização de Serviços:** Criado o arquivo `apps/common/services.py` e implementada a função assíncrona `login_to_portran(page, logger)` para encapsular a lógica de login.
- **Refatoração de Comandos Existentes:** Comandos como `login_portran.py`, `upload_licenca.py` e `automacao_documentos_ipiranga.py` foram modificados para remover a lógica de login duplicada e chamar a função `login_to_portran` do serviço `common`.
