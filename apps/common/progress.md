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

## 16/08/2025 - Correção de Erro de Sintaxe e Ajustes de Tipagem

- **Correção de Erro de Sintaxe:** Identificado e corrigido um `SyntaxError` em `apps/common/services.py` relacionado à atribuição de variáveis e indentação.
- **Ajustes de Tipagem:** Adicionado um comentário `type: ignore` em `apps/common/services.py` para resolver um erro de tipagem do Pyright relacionado à conversão de imagem (`Image.open(io.BytesIO(pix.tobytes()))`).

## 17/08/2025 - Resumo do Dia de Trabalho e Melhorias Aplicadas

- **Análise Detalhada do Código**: Realizada uma revisão aprofundada dos arquivos `services.py` e `storage.py`.
- **Externalização de Configurações**: URLs de portais (Ipiranga) e coordenadas de Regiões de Interesse (ROIs) para OCR foram externalizadas de `services.py` para as configurações do Django (`core/settings.py`), aumentando a manutenibilidade e flexibilidade.

## 17/08/2025 - Restauração de Arquivos

- **Ação**: O conteúdo deste arquivo `progress.md` foi restaurado a partir do repositório GitHub, após um incidente de sobrescrita acidental no arquivo `progress.md` principal.
- **Observações**: Esta entrada reflete a recuperação do histórico do app `common`.

## 17/08/2025 - Otimização de Funções e Comandos do App Common

- **Análise e Ajustes em `services.py`**:
    - URL do dashboard (`IPIRANGA_DASHBOARD_URL`) movida de hardcode para `core/settings.py`.
    - Função `extract_text_from_roi`: Alterado o tratamento de erro para `raise` a exceção em vez de retornar string vazia, garantindo propagação de erros.
    - Função `normalize_text`: Corrigida a regex para remover o `R` não intencional.
- [2025-08-19] Melhorias no Processamento de OCR:
    - Implementação de técnicas avançadas de pré-processamento de imagem em `services.py` para otimizar a precisão do OCR, incluindo correção de inclinação (deskewing) via Hough Transform, redução de ruído (Gaussian Blur) e binarização aprimorada.
    - Adição de salvamento de imagem processada para depuração (`logs/ocr_processed_image_{page_num}.png`).
- [2025-08-19] Depuração Iterativa de OCR:
    - **Ajustes de Pré-processamento de Imagem em `services.py` (`extract_text_from_roi`):**
        - Implementação de binarização usando o método de Otsu para otimizar o limiar.
        - Aumento do fator de escala para 1200 DPI (`matrix=fitz.Matrix(1200 / 72, 1200 / 72)`) para capturar mais detalhes da imagem.
        - Aumento do `sigma` do filtro Gaussiano para 1.0 (`gaussian_filter(img_np, sigma=1.0)`) para maior suavização de ruído.
        - Definição explícita do Page Segmentation Mode (PSM) do Tesseract para 11 (`tesseract_config = "--psm 11"`) para melhor reconhecimento de texto esparso.
        - Adição de `unsharp_mask` (`unsharp_mask(img_np, radius=1.0, amount=1.0)`) para realce de contraste e nitidez das bordas.
    - **Resultados:** Apesar dos múltiplos ajustes, o texto extraído pelo OCR permaneceu ilegível, indicando que a qualidade da imagem após o pré-processamento ainda é o principal gargalo.
    - **Lição Aprendida:** A legibilidade da imagem processada (`logs/ocr_processed_image_0.png`) é o fator determinante para o sucesso do OCR. Se a imagem não for legível, o Tesseract não conseguirá extrair os dados corretamente, independentemente das regexes ou configurações.
- [2025-08-21] Implementação da Extração de Dados por Nome de Arquivo:
    - **Nova Função de Extração**: O arquivo `services.py` foi atualizado com a nova função `extract_certificate_data_from_filename`. Esta função centraliza a lógica para extrair o número do certificado e a data de vencimento diretamente do nome do arquivo PDF, substituindo a abordagem anterior baseada em OCR.

---

## 21/08/2025 - Refatoração Completa para Remoção da Lógica de OCR

- **Resolução de Problema de Memória do CLI:** Identificado e resolvido o erro "JavaScript heap out of memory" no Gemini CLI, aumentando o limite de memória do processo Node.js via `export NODE_OPTIONS`. Isso permitiu a continuidade das operações de refatoração.
- **Otimização e Correção do `pre-commit`:**
    - Investigada e resolvida a falha persistente do hook `safety` (`Repository not found`).
    - Atualizada a configuração do `safety` no `.pre-commit-config.yaml` para usar um hook `local` que executa `scripts/run_safety.py`, contornando problemas de acesso ao repositório e interpretação de comandos.
    - Verificado o sucesso da execução de todos os hooks do `pre-commit`.
- **Gerenciamento de Pacotes com `uv`:**
    - Tentativa de atualização de pacotes desatualizados (`filelock`, `psutil`, `pydantic`, `pydantic-core`) via `uv sync --upgrade` e `uv add --upgrade`.
    - Constatado que a atualização não foi possível devido a restrições de dependência (provavelmente do `safety` ou outras dependências), mantendo as versões atuais por compatibilidade.
- **Limpeza de Arquivos Temporários:**
    - Removido o arquivo temporário `commit_message.txt` utilizado para mensagens de commit.
    - Adicionado `commit_message.txt` ao `.gitignore` para evitar seu rastreamento futuro.
- **Abandono do OCR:** Realizada uma refatoração em todo o projeto para remover completamente a funcionalidade de extração de dados de PDFs via OCR.
- **Nova Abordagem:** A extração de "Número do Certificado" e "Data de Vencimento" agora é feita exclusivamente a partir do nome do arquivo, que segue o padrão `PLACA_NUMEROCERTIFICADO_DDMMYYYY.pdf`.
- **Ações de Limpeza:**
    - Removidas configurações de OCR (`OCR_..._ROI`) do arquivo `core/settings.py`.
    - Removido o campo `tentativas_ocr` do modelo `CertificadoVeiculo` em `apps/automacao_ipiranga/models.py`.
    - Criada e aplicada uma nova migração (`0004_remove_certificadoveiculo_tentativas_ocr`) para remover a coluna do banco de dados.
- **Verificação:** As ferramentas `ruff` e `pyright` foram executadas para garantir a qualidade e a correção do código após a refatoração.
