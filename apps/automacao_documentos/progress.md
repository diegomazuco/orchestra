# Histórico de Progresso do App: automacao_documentos

Este arquivo registra as principais ações e configurações realizadas especificamente no app "automacao_documentos".

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

## 12/08/2025 - Atualização de Diretrizes de Limpeza

- **Atualização de `GEMINI.md`:** O arquivo `apps/automacao_documentos/GEMINI.md` foi atualizado para incluir a diretriz de limpeza obrigatória de recursos temporários gerados por automações.

## 10/08/2025 - Análise e Refatoração de Documentação

- **Análise Rigorosa do Projeto:** Contribuição para a análise detalhada de toda a estrutura do projeto Orchestra.
- **Refatoração de `GEMINI.md`:** O arquivo `GEMINI.md` deste app foi lido em todas as suas versões históricas, analisado e refatorado para conter as melhores e mais robustas instruções. A versão refatorada foi substituída no seu devido local.
- **Refatoração de `progress.md`:** Este arquivo `progress.md` foi lido em todas as suas versões históricas, analisado e refatorado para consolidar e refinar o histórico de desenvolvimento do app. A versão refatorada será substituída no seu devido local.

## 08/08/2025 - Refinamento do Processo de Automação

- **Contexto:** Durante a depuração da automação do app `automacao_ipiranga`, foi identificado um problema fundamental na forma como os subprocessos eram disparados a partir dos sinais do Django.
- **Problema:** O subprocesso que executava o `custom command` não utilizava o ambiente virtual (`.venv`) do projeto, levando a falhas silenciosas por falta de dependências.
- **Solução Aplicada (no app `automacao_ipiranga`):** A lógica em `signals.py` foi corrigida para apontar explicitamente para o executável do Python dentro do `.venv`. Esta solução, embora aplicada em um app específico, estabelece um padrão para todas as futuras automações orquestradas por este app, garantindo que elas sejam executadas no contexto correto.

## 01/08/2025 - Configuração de Ferramentas de Qualidade e Performance

- **Configuração de Ferramentas:** Contribuição para a implementação de `pre-commit` com hooks para `ruff` (formatação e linting) e `pyright` (verificação de tipos).
- **Instalação de Ferramentas de Performance:** Contribuição para a adição de `line-profiler` e `snakeviz` para análise de performance.
- **Refatoração Completa:** Contribuição para a remoção de testes (`tests.py`), configuração de `Ruff` e atualização de documentação.

## 30/07/2025 - Depuração e Ajustes Iniciais

- **Depuração e Ajustes para Inicialização do Servidor:** Contribuição para a investigação e ajuste de problemas de inicialização do servidor.
- **Atualização de Logs de Progresso e Refatoração de Automação:** Logs de progresso foram atualizados e a lógica de automação foi refatorada.
- **Implementação de Preenchimento de Vencimento e Armazenamento de Arquivo Original:** Funcionalidades para preenchimento de dados e armazenamento de arquivos originais foram implementadas.
- **Melhoria na Depuração de Sinal:** A depuração de sinais foi aprimorada.
- **Refatoração da Automação Ipiranga:** A automação Ipiranga foi refatorada para usar DB, Signals e login centralizado.

## 28/07/2025 - Criação do App e Inicialização

- **Criação do App:** Um app de automação inicial foi renomeado para `automacao_documentos` e a página Orchestra foi criada.
- **Inicialização Completa:** Contribuição para a inicialização completa do projeto Orchestra e do app de automação.

## 16/08/2025 - Atualização de Diretrizes do Framework de Automação

- **Refinamento de Diretrizes:** O arquivo `GEMINI.md` deste app foi atualizado para enfatizar a necessidade de tratamento de erros robusto e logging detalhado dentro dos `custom commands` para capturar e registrar falhas inesperadas, como `SyntaxError`, durante a execução da automação.

## 17/08/2025 - Restauração de Arquivos

- **Ação**: O conteúdo deste arquivo `progress.md` foi restaurado a partir do repositório GitHub, após um incidente de sobrescrita acidental no arquivo `progress.md` principal.
- **Observações**: Esta entrada reflete a recuperação do histórico do app `automacao_documentos`.

---

## 21/08/2025 - Refatoração Completa para Remoção da Lógica de OCR

- **Resolução de Problema de Memória do CLI:** Identificado e resolvido o erro "JavaScript heap out of memory" no Gemini CLI, aumentando o limite de memória do processo Node.js via `export NODE_OPTIONS`. Isso permitiu a continuidade das operações de refatoração.
- **Otimização e Correção do `pre-commit`:**
    - Investigada e resolvida a falha persistente do hook `safety` (`Repository not found`).
    - Atualizada a configuração do `safety` no `.pre-commit-config.yaml` para usar um hook `local` que executa `scripts/run_safety.py`, contornando problemas de acesso ao repositório e interpretação de comandos.
    - Verificado o sucesso da execução de todos os hooks do `pre-commit`.
- **Gerenciamento de Pacotes com `uv`:**
    - Tentativa de atualização de pacotes desatualizados (`filelock`, `psutil`, `pydantic`, `pydantic-core`) via `uv sync --upgrade` e `uv add --upgrade`.
    - Constatado que a atualização não foi possível devido a restrições de dependência (provavelmente do `safety` ou outras dependências), mantendo as versões atuais por compatibilidade).
- **Limpeza de Arquivos Temporários:**
    - Removido o arquivo temporário `commit_message.txt` utilizado para mensagens de commit.
    - Adicionado `commit_message.txt` ao `.gitignore` para evitar seu rastreamento futuro.
- **Gerenciamento do `.gitignore`:** O arquivo `.gitignore` foi revisado e atualizado para garantir que todos os arquivos e diretórios temporários, de cache e de ambiente (`test_log.log`, `uv.lock`, `commit_message.txt`) sejam corretamente ignorados pelo controle de versão.
- **Abandono do OCR:** Realizada uma refatoração em todo o projeto para remover completamente a funcionalidade de extração de dados de PDFs via OCR.
- **Nova Abordagem:** A extração de "Número do Certificado" e "Data de Vencimento" agora é feita exclusivamente a partir do nome do arquivo, que segue o padrão `PLACA_NUMEROCERTIFICADO_DDMMYYYY.pdf`.
- **Ações de Limpeza:**
    - Removidas configurações de OCR (`OCR_..._ROI`) do arquivo `core/settings.py`.
    - Removido o campo `tentativas_ocr` do modelo `CertificadoVeiculo` em `apps/automacao_ipiranga/models.py`.
    - Criada e aplicada uma nova migração (`0004_remove_certificadoveiculo_tentativas_ocr`) para remover a coluna do banco de dados.
- **Verificação:** As ferramentas `ruff` e `pyright` foram executadas para garantir a qualidade e a correção do código após a refatoração.

**Instrução:** Você não pode deletar informações de nenhum dos arquivos GEMINI.md nem de nenhum dos arquivos progress.md, os arquivos GEMINI.md do projeto Orchestra contém instruções importantes para serem seguidas e devem apenas incluir novas instruções ou ajustar aquelas que já existesm, desde que sejam ajustes para melhorar ainda mais as intruções, você NUNCA deve deletar todo o conteúdo deles, em hipótese nenhuma. O mesmo serve para todos os arquivos progress.md do projeto Orchestra, todos eles contém informações sobre o histórico do projeto, processos e procedimentos realizados ao longo do tempo, neles devem apenas serem incluídas novos históricos, processos ou procedimentos realizados, em ordem cronológica, você NUNCA deve excluiu o conteúdo completo de nenhum deles em hipótese nenhuma para incluir coisas novas.

## 21/08/2025 - Correção de Histórico e Reinserção de Instruções

- **Problema:** Identificado que a seção "Refatoração Completa para Remoção da Lógica de OCR" e a instrução de não deletar informações dos arquivos `GEMINI.md` e `progress.md` foram acidentalmente removidas durante operações anteriores.
- **Ação:** As seções e instruções foram reinseridas nos arquivos `progress.md` afetados para garantir a integridade e completude do histórico.
- **Observações:** Este incidente reforça a importância da revisão cuidadosa das operações de escrita e da validação do conteúdo após as modificações.
