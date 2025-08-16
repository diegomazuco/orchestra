# Histórico de Progresso do App: Common

Este arquivo registra as principais ações e configurações realizadas especificamente no app "Common".

## 15/08/2025 - Verificação e Tentativa de Atualização de Pacotes Python

- **Verificação de Pacotes Desatualizados:**
    - Executado `uv pip list --outdated` para identificar pacotes Python com versões mais recentes disponíveis.
    - Identificados os seguintes pacotes desatualizados: `filelock`, `opencv-python`, `psutil`, `pydantic`, `pydantic-core`.
- **Tentativa de Atualização de Pacotes:**
    - Tentado atualizar os pacotes utilizando `uv sync --upgrade`.
    - Tentado atualizar os pacotes individualmente utilizando `uv add <pacote>`.
    - Observado que os pacotes permaneceram desatualizados após as tentativas de atualização, indicando possíveis restrições de versão no `pyproject.toml` ou dependências que impedem a atualização para as versões mais recentes.

## 15/08/2025 - Correção de Erro de Tipagem em `services.py`

- **Correção de Erro de Tipagem:** Corrigido um erro de tipagem na função `extract_cipp_data` em `apps/common/services.py`. O erro ocorria porque a variável `numero_documento_valor` poderia ser `None`, enquanto a assinatura da função esperava um `str`. A correção implementada garante que um `ValueError` seja levantado caso `numero_documento_valor` seja `None`, assegurando que o tipo de retorno `tuple[str, str]` seja sempre respeitado.

## 15/08/2025 - Consolidação de Melhorias Pós-Travamento

- **Análise e Consolidação de Alterações:** Após um travamento e reinicialização do ambiente WSL, todas as modificações de arquivo não commitadas foram analisadas.
- **Melhorias em Serviços Comuns:**
    - A URL de login no portal Ipiranga foi atualizada em `login_to_portran`.
    - O processo de OCR foi aprimorado com a adição de correção de inclinação da imagem e a remoção de um redimensionamento de imagem redundante, otimizando a performance e a precisão.

## 14/08/2025 - Melhorias e Ajustes em Serviços Comuns

- **Atualização de URLs de Login:** As URLs de login no `login_to_portran` foram atualizadas para `https://sites2.ipiranga.com.br` para refletir o endereço correto do portal.
- **Aprimoramentos de OCR:**
    - Adicionada a função `cv2.resize` para redimensionamento de imagem, melhorando a precisão do OCR.
    - A função `determine_skew` foi atualizada para aceitar um logger e incluir logs mais detalhados.
    - A expressão regular em `extract_cipp_data` foi aprimorada para maior flexibilidade na extração de dados.
- **Ajustes de Qualidade de Código:**
    - Removido código comentado relacionado a "Deskewing" em `apps/common/services.py` para aderir às diretrizes de qualidade de código.

## 13/08/2025 - Melhorias no Logging de Automação

- **Logging Detalhado:** Adicionado logging mais detalhado no arquivo `services.py` para melhorar a depuração e o rastreamento de problemas durante a execução da automação, especificamente nas funções de OCR e navegação.

## 12/08/2025 - Resumo do Dia de Trabalho e Próximos Passos

- **Problemas Persistentes:** A automação Playwright ainda não consegue navegar para as URLs "Vencidos" e "À vencer" após a autenticação. O problema de limpeza de arquivos temporários também persistiu.
- **Ações Realizadas:**
    - Implementação de um tempo limite global de 30 segundos para a automação.
    - Adição de logging mais granular na função de OCR para depurar a extração de texto.
    - Refinamento da estratégia de limpeza de dados.
- **Próximos Passos (Foco Principal):**
    - Depuração da navegação pós-autenticação.
    - Revisão do processo de OCR.
    - Monitoramento da limpeza de arquivos temporários.

## 11/08/2025 - Atualização de Dependências

- **Atualização de Dependências:**
    - O arquivo `apps/common/services.py` foi modificado devido à instalação de todas as dependências do projeto e ferramentas de desenvolvimento.

## 10/08/2025 - Análise e Refatoração de Documentação

- **Análise Rigorosa do Projeto:** Contribuição para a análise detalhada de toda a estrutura do projeto.
- **Refatoração de `GEMINI.md` e `progress.md`:** Os arquivos de documentação e progresso foram lidos, analisados e refatorados para consolidar as melhores instruções e histórico.

## 01/08/2025 - Aprimoramentos de Robustez e Configuração de Ferramentas

- **Função `login_to_portran`:** Adicionada lógica de resiliência para instabilidade de login no portal Ipiranga.
- **Remoção de Testes:** Todos os arquivos de teste (`tests.py`) foram removidos do projeto.
- **Configuração de Ferramentas:** Contribuição para a implementação de `pre-commit`, `ruff`, `pyright`, `line-profiler`, e `snakeviz`.

## 30/07/2025 - Criação e Centralização de Serviços

- **Criação e Configuração do App:** Criado o app Django `common` e registrado em `INSTALLED_APPS`.
- **Centralização de Serviços:** Criado `apps/common/services.py` com a função assíncrona `login_to_portran(page, logger)` para encapsular a lógica de login.
- **Refatoração de Comandos Existentes:** Comandos de automação foram modificados para remover a lógica de login duplicada e chamar a função centralizada.
