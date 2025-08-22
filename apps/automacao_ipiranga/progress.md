# Histórico de Progresso do App: automacao_ipiranga

Este arquivo registra as principais ações e configurações realizadas especificamente no app "automacao_ipiranga".

## 15/08/2025 - Consolidação de Melhorias Pós-Travamento

- **Análise e Consolidação de Alterações:** Após um travamento e reinicialização do ambiente WSL, todas as modificações de arquivo não commitadas foram analisadas.
- **Melhorias na Automação (`automacao_documentos_ipiranga.py`):**
    - O tempo limite da automação foi aumentado para 90 segundos para maior resiliência.
    - As URLs de navegação foram atualizadas para a nova URL do portal Ipiranga.
    - A lógica de extração de dados do PDF foi movida para um momento mais apropriado no fluxo da automação.
    - O logging foi aprimorado com mais detalhes e prefixos para facilitar a depuração.
    - A chamada para `cleanup_automation_data` foi tornada assíncrona.
    - Implementada a captura de tela em caso de erro para facilitar a análise de falhas.
- **Ajustes de Qualidade de Código:**
    - O comando `cleanup_media.py` foi refatorado para maior clareza e eficiência.
    - Removida uma importação não utilizada do comando `test_ocr_extraction.py`.

## 14/08/2025 - Melhorias na Automação e Depuração Visual do Playwright

- **Melhorias na Automação (`automacao_documentos_ipiranga.py`):**
    - Aumentado o tempo limite global da automação (`automation_timeout`) de 30 para 90 segundos.
    - A lógica de processamento de PDF foi realocada para ocorrer após o clique no botão "Atualizar".
    - URLs de navegação foram atualizadas para `https://sites2.ipiranga.com.br`.
    - Adicionados logs mais detalhados com prefixos para facilitar a depuração.
    - A chamada para `cleanup_automation_data` foi alterada para execução assíncrona.
    - Implementado tratamento de erro mais robusto com captura de screenshot em caso de falha.
    - Garantida a limpeza abrangente de dados de automação (`cleanup_automation_data`) no bloco `finally`.
- **Depuração da Visualização do Navegador Playwright (`signals.py`):**
    - O problema do navegador Playwright não aparecer durante a execução da automação foi corrigido.
    - A variável de ambiente `DISPLAY` agora é explicitamente passada para o subprocesso, permitindo que a interface gráfica do navegador seja exibida.
    - Adicionado logging para indicar o uso da variável `DISPLAY`.

## 13/08/2025 - Melhorias na Depuração e Correções de Código

- **Melhorias na Depuração:**
    - O `signals.py` foi modificado para redirecionar o `stdout` e `stderr` do subprocesso Playwright para o arquivo de log `logs/django.log`.
- **Correções de Código:**
    - Realizada uma tentativa de correção de erros B904 (relacionados a `try-except-raise`) e eliminação de funções duplicadas no comando `automacao_documentos_ipiranga.py`.

## 12/08/2025 - Resumo do Dia de Trabalho e Próximos Passos

- **Problemas Persistentes:** A automação Playwright ainda não consegue navegar para as URLs "Vencidos" e "À vencer" após a autenticação. O problema de limpeza de arquivos temporários também persistiu.
- **Ações Realizadas:**
    - Implementação de um tempo limite global de 30 segundos para a automação.
    - Adição de logging mais granular na função de OCR para depurar a extração de texto.
    - Refinamento da estratégia de limpeza de dados, movendo-a para o bloco `finally` da automação.
- **Próximos Passos (Foco Principal):**
    - Depuração da navegação pós-autenticação.
    - Revisão do processo de OCR.
    - Monitoramento da limpeza de arquivos temporários.

## 11/08/2025 - Ajustes de Qualidade de Código e Migrações

- **Ajustes de Tipagem:**
    - Correção de problemas de docstrings e simplificação de `if` aninhados no `cleanup_media.py`.
- **Migrações:**
    - Geração e aplicação da migração `0002_alter_certificadoveiculo_arquivo.py`.

## 10/08/2025 - Análise e Refatoração de Documentação

- **Análise Rigorosa do Projeto:** Contribuição para a análise detalhada de toda a estrutura do projeto.
- **Refatoração de `GEMINI.md` e `progress.md`:** Os arquivos de documentação e progresso foram leds, analisados e refatorados para consolidar as melhores instruções e histórico.

## 08/08/2025 - Correção do Gatilho de Automação e Ajuste na Extração de Dados do PDF

- **Correção do Gatilho de Automação:** Solucionado problema onde subprocessos disparados por sinal não utilizavam o ambiente virtual (`.venv`).
- **Ajuste na Extração de Dados do PDF:** Expressões regulares foram ajustadas para melhorar a precisão do OCR.

## 04/08/2025 - Melhorias na Depuração e Correção de Migrações

- **Melhorias na Depuração da Automação Playwright:** Ajustes para facilitar a depuração visual e o rastreamento de erros.
- **Correção de Migrações:** Problemas em migrações foram resolvidos.

## 01/08/2025 - Configuração de Automação Web e Ajustes de Testes

- **Configuração de Automação Web:** Configurada a automação web, permitindo a visualização do navegador durante a execução.
- **Ajustes de Testes:** Refatoração de testes para melhorar robustez e manutenibilidade (antes da remoção completa dos testes).

## 30/07/2025 - Refatoração da Automação Ipiranga com DB, Signals e Login Centralizado

- A automação Ipiranga foi refatorada para usar banco de dados, sinais e login centralizado, e funcionalidades de preenchimento de dados e armazenamento de arquivos foram implementadas.

## 29/07/2025 - Aprimoramento da Automação Ipiranga e Correção de Tratamento de Erros

- A automação Ipiranga foi aprimorada e o tratamento de erros foi corrigido.

## 28/07/2025 - Integração de Upload de Documentos e Refatoração da Arquitetura de Automação

- Funcionalidade de upload de documentos foi integrada e a arquitetura de automação foi refatorada com a criação deste app.

## 16/08/2025 - Ajustes de Tipagem e Refinamento de Diretrizes de Automação

- **Ajustes de Tipagem:** Adicionados comentários `type: ignore` em `apps/automacao_ipiranga/models.py` para resolver erros de tipagem do Pyright relacionados a argumentos de construtores de campo de modelo.
- **Refinamento de Diretrizes:** O arquivo `GEMINI.md` deste app foi atualizado para incluir lições aprendidas sobre os desafios de tipagem de operações de OCR com Pyright (ex: `fitz`, `pytesseract`) e a necessidade de `type: ignore` em linhas específicas. Também foi reforçada a importância de tratamento de erros robusto e logging detalhado na interação com o portal Playwright.

## 17/08/2025 - Restauração de Arquivos

- **Ação**: O conteúdo deste arquivo `progress.md` foi restaurado a partir do repositório GitHub, após um incidente de sobrescrita acidental no arquivo `progress.md` principal.
- **Observações**: Esta entrada reflete a recuperação do histórico do app `automacao_ipiranga`.

## 17/08/2025 - Otimização de Funções e Comandos do App AutomacaoIpiranga

- **Análise e Ajustes em `models.py`**:
    - Adicionados os campos `tentativas_automacao` e `tentativas_ocr` ao modelo `CertificadoVeiculo`.
    - Adicionado `falha_max_tentativas` às opções de `STATUS_CHOICES` do `CertificadoVeiculo`.
    - Criadas e aplicadas as migrações necessárias para as alterações nos modelos.
- **Análise e Ajustes em `management/commands/automacao_documentos_ipiranga.py`**:
    - Implementado o incremento do contador `tentativas_automacao` no início da execução.
    - Adicionada verificação de limite máximo de tentativas, com marcação de status `falha_max_tentativas` e interrupção da automação.
    - Refinado o bloco `except` para garantir a atualização robusta do status para `falha` em caso de erro.
- **Análise e Ajustes em `management/commands/cleanup_media.py`**:
    - Refatorada a lógica de exclusão de arquivos e registros para `CertificadoVeiculo`, garantindo que os arquivos sejam deletados do armazenamento antes dos registros do banco de dados.
- **Análise e Ajustes em `management/commands/test_ocr_extraction.py`**:
    - Melhorada a consistência na limpeza de texto para busca de dados.
- [2025-08-19] Melhorias na Automação e OCR:
    - Lógica de disparo de sinal aprimorada em `signals.py` para garantir que a automação seja disparada apenas na criação inicial do objeto (`if created`).
    - Tempos limite (`timeout`) aumentados para operações críticas do Playwright em `automacao_documentos_ipiranga.py` (de 30s para 60s) para maior resiliência.
    - Blocos `finally` em `automacao_documentos_ipiranga.py` aprimorados com tratamento de erros robusto para exclusão de `CertificadoVeiculo` e arquivos associados.
    - Implementação de técnicas avançadas de pré-processamento de imagem para OCR em `common/services.py` (correção de inclinação, redução de ruído, binarização) para otimizar a precisão.
- [2025-08-19] Ajustes na Extração e Formatação de Dados do PDF:
    - `apps/common/services.py`: A função `extract_cipp_data` foi atualizada para buscar "Número do Certificado" e "DATA DE VENCIMENTO" no PDF. O "Número do Certificado" agora é extraído como alfanumérico e filtrado para conter apenas números antes de ser usado no portal. A "DATA DE VENCIMENTO" é extraída e formatada para "DD/MM/YYYY".
    - `apps/automacao_ipiranga/management/commands/automacao_documentos_ipiranga.py`: O código foi ajustado para utilizar os valores numéricos do "Número do Documento" e a data formatada do "Vencimento" diretamente nos campos do Playwright, removendo lógicas de formatação redundantes.
- [2025-08-19] Depuração Iterativa de OCR:
    - Análise inicial do log (`django.log`) revelou falha na extração de "Número do Certificado" e "DATA DE VENCIMENTO" devido a `ValueError: Bloco 'Número do Certificado' não encontrado.`.
    - Utilização do comando `test_ocr_extraction.py` para depuração isolada do OCR.
    - **Ajustes de Pré-processamento de Imagem em `apps/common/services.py` (`extract_text_from_roi`):**
        - Implementação de binarização usando o método de Otsu para otimizar o limiar.
        - Aumento do fator de escala para 1200 DPI (`matrix=fitz.Matrix(1200 / 72, 1200 / 72)`) para capturar mais detalhes da imagem.
        - Aumento do `sigma` do filtro Gaussiano para 1.0 (`gaussian_filter(img_np, sigma=1.0)`) para maior suavização de ruído.
        - Definição explícita do Page Segmentation Mode (PSM) do Tesseract para 11 (`tesseract_config = "--psm 11"`) para melhor reconhecimento de texto esparso.
        - Adição de `unsharp_mask` (`unsharp_mask(img_np, radius=1.0, amount=1.0)`) para realce de contraste e nitidez das bordas.
    - **Resultados:** Apesar dos múltiplos ajustes, o texto extraído pelo OCR permaneceu ilegível, indicando que a qualidade da imagem após o pré-processamento ainda é o principal gargalo.
    - **Lição Aprendida:** A legibilidade da imagem processada (`logs/ocr_processed_image_0.png`) é o fator determinante para o sucesso do OCR. Se a imagem não for legível, o Tesseract não conseguirá extrair os dados corretamente, independentemente das regexes ou configurações.
- [2025-08-21] Consolidação da Abordagem de Extração de Dados via Nome de Arquivo:
    - **Atualização de Diretrizes**: O arquivo `GEMINI.md` deste app foi extensivamente revisado e atualizado para remover todas as diretrizes e lições aprendidas relacionadas à extração de dados por OCR, que foi abandonada.
    - **Foco no Nome do Arquivo**: As novas diretrizes agora focam exclusivamente na extração de dados a partir do nome do arquivo, enfatizando o formato `PLACA_NUMEROCERTIFICADO_DDMMYYYY.pdf` e a função centralizada `extract_certificate_data_from_filename` em `common/services.py`.
    - **Remoção de Código Obsoleto**: O comando de teste de OCR (`test_ocr_extraction.py`), que pertencia a este app, foi removido do projeto.

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

## 22/08/2025 - Melhorias na Automação e Gerenciamento de Certificados

- **Atualização de Diretrizes (`GEMINI.md`):** O arquivo `apps/automacao_ipiranga/GEMINI.md` foi atualizado para incluir o status `falha_max_tentativas` na seção "Modelo Gatilho" sob "Status Adicional", refletindo a nova opção de status para certificados.
- **Aprimoramentos no Comando de Automação (`automacao_documentos_ipiranga.py`):**
    - **Captura de Tela Aprimorada:** O caminho para salvar screenshots agora inclui o ID do certificado, tornando os nomes dos arquivos únicos e facilitando a depuração.
    - **Processo de Upload Mais Robusto:** A lógica de espera após o upload foi ajustada para maior confiabilidade.
    - **Nova Verificação de Certificados Vencidos:** Implementada uma nova funcionalidade que verifica a existência de outros certificados vencidos para o mesmo veículo antes de salvar as alterações. Se encontrados, a automação é interrompida e o certificado é marcado com o status `falha_outros_vencidos`.
    - **Limpeza de Screenshots:** Adicionada uma etapa no bloco `finally` para remover screenshots gerados durante a execução da automação, garantindo a limpeza de arquivos temporários.
- **Atualizações no Modelo `CertificadoVeiculo` (`models.py` e `migrations/0001_initial.py`):**
    - **Novo Armazenamento de Arquivos:** O campo `arquivo` agora utiliza `OriginalFilenameStorage()`, um armazenamento personalizado que mantém o nome original do arquivo, permitindo a sobrescrita intencional.
    - **Novos Status:** Adicionados os status `falha_max_tentativas` e `falha_outros_vencidos` às opções do campo `status`, e o `max_length` do campo foi aumentado para 30.
    - **Campo de Mensagem de Erro:** Adicionado o campo `error_message` para armazenar mensagens detalhadas em caso de falhas na automação.
- **Novo Comando de Gerenciamento (`reset_automation_sequences.py`):** Adicionado um novo comando de gerenciamento para resetar as sequências de auto-incremento das tabelas `CertificadoVeiculo` e `VeiculoIpiranga`, útil para limpeza de ambiente de desenvolvimento/teste.
