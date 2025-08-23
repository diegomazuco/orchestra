# Histórico de Progresso do App: automacao_ipiranga

Este arquivo registra as principais ações e configurações realizadas especificamente no app "automacao_ipiranga", que é um implementador do framework de automação.

## 23/08/2025 - Aprimoramento das Diretrizes de Automação Ipiranga

- **Contexto:** A automação deste app interage com um portal externo (Ipiranga), que é suscetível a mudanças inesperadas. As diretrizes precisavam refletir melhor essa realidade.
- **Ação:** O arquivo `GEMINI.md` deste app foi atualizado com uma nova "Lição Aprendida" sobre a necessidade de **adaptação a mudanças no portal externo**. A diretriz agora orienta que, em caso de falha, a primeira hipótese deve ser uma alteração no portal, e instrui o uso de ferramentas de depuração para diagnosticar e adaptar o código da automação.

---

## 22/08/2025 - Robustez no Gerenciamento de Certificados

- **Contexto:** A automação precisava ser mais robusta para lidar com cenários de falha específicos e evitar loops, além de fornecer feedback mais claro ao usuário.
- **Ações:**
    - **Prevenção de Sobrescrita Indevida:** Implementado o `OriginalFilenameStorage` para garantir que os uploads de certificados com o mesmo nome de arquivo (mesma placa) substituam o antigo intencionalmente.
    - **Tratamento de Falhas Múltiplas:** Adicionados os status `falha_max_tentativas` e `falha_outros_vencidos` ao modelo `CertificadoVeiculo` para lidar com cenários de erro específicos e fornecer feedback detalhado ao frontend via polling.
    - **Melhoria na Depuração:** O caminho para salvar screenshots de erro foi alterado para incluir o ID do certificado, facilitando a associação do erro ao registro correspondente.
    - **Limpeza de Ambiente:** Criado o comando `reset_automation_sequences` para facilitar a limpeza e a preparação do ambiente de teste.

---

## 21/08/2025 - Abandono da Estratégia de OCR

- **Contexto:** A extração de dados de PDFs via OCR mostrou-se consistentemente instável e complexa, sendo um grande ponto de falha nas automações.
- **Decisão Estratégica:** A funcionalidade de OCR foi completamente removida do projeto.
- **Nova Abordagem:** A responsabilidade pela extração de dados foi transferida para o nome do arquivo, que agora deve seguir um padrão rigoroso (`PLACA_TIPOLICENCA_NUMEROCERTIFICADO_DDMMYYYY.pdf`). Esta abordagem é mais simples, determinística e confiável.
- **Impacto:** Esta decisão simplificou drasticamente o fluxo de automação, removendo dependências complexas e pontos de falha.

---

## 19/08/2025 - Depuração Iterativa e Lições Aprendidas com OCR

- **Contexto:** A extração de dados via OCR estava falhando consistentemente, apesar de múltiplos ajustes.
- **Ações de Depuração:**
    - Utilizado o comando `test_ocr_extraction.py` para isolar e depurar o processo de OCR.
    - Implementadas várias técnicas de pré-processamento de imagem (binarização de Otsu, aumento de DPI, filtro Gaussiano, unsharp mask, etc.).
- **Lição Aprendida Crucial:** Foi constatado que a legibilidade da imagem após o pré-processamento era o fator determinante. Se a imagem processada (`logs/ocr_processed_image_0.png`) não fosse legível para um humano, o Tesseract também não conseguiria extrair os dados, independentemente das configurações. Esta lição foi fundamental para a decisão de abandonar o OCR.

---

## 14/08/2025 - Melhorias na Depuração Visual do Playwright

- **Problema:** O navegador Playwright não estava sendo exibido em execuções de depuração (`headless=False`), dificultando a análise de problemas de interação com o portal.
- **Solução:** A variável de ambiente `DISPLAY` foi explicitamente passada para o subprocesso no `signals.py`, permitindo que a interface gráfica do navegador fosse renderizada corretamente.

---

## 08/08/2025 - Correção Crítica na Execução de Subprocessos

- **Problema:** As automações disparadas por sinais do Django estavam falhando silenciosamente porque os `custom commands` eram executados pelo Python do sistema, e não pelo ambiente virtual (`.venv`) do projeto.
- **Solução:** A lógica em `signals.py` foi corrigida para usar o caminho absoluto do executável do Python do `.venv`, garantindo que a automação sempre execute com as dependências corretas.

---

## 28/07/2025 a 30/07/2025 - Estruturação Inicial da Automação

- **Criação do App:** O app `automacao_ipiranga` foi criado para conter a lógica de negócio específica da automação do portal Ipiranga.
- **Refatoração Inicial:** A lógica de automação foi refatorada para utilizar o banco de dados (modelo `CertificadoVeiculo`) e sinais do Django, estabelecendo a arquitetura base do app.


---

## 23/08/2025 - Continuação do Trabalho

### Análise Detalhada da Estrutura e Código do Projeto (Aspectos Específicos do `automacao_ipiranga`)
- **Ação:** Análise de arquivos e pastas para identificar itens não utilizados e verificar a correção do código.
- **Detalhes:**
    - **Remoção de comandos de limpeza redundantes:** `apps/automacao_ipiranga/management/commands/cleanup_media.py` e `apps/automacao_ipiranga/management/commands/cleanup_test_data.py` foram deletados.
    - **Remoção de view não utilizada:** A view `iniciar_automacao` e sua URL em `apps/automacao_ipiranga` foram removidas.
    - **Movimentação de valores hardcoded para `settings.py`:**
        - URL hardcoded em `login_to_portran` movida para `settings.IPIRANGA_DASHBOARD_URL`.
- **Resultado:** Código limpo e configurações centralizadas.