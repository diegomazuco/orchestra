**Instrução:** Por favor, responda sempre em português.

# Diretrizes Específicas para o App: automacao_ipiranga

**Contexto:** Este app é uma **implementação** do framework de automação definido em `apps/automacao_documentos`. As regras aqui complementam as diretrizes globais e do framework.

---

### 1. Visão Geral e Objetivo

* **Objetivo do App:** Conter a lógica de negócio e o código do robô (web scraper) que automatiza processos especificamente no portal Ipiranga, com foco na atualização de certificados de veículos.

---

### 2. Dependências e Configurações Específicas

* **`playwright`:** A versão deve ser estritamente `1.54.0`.
* **Credenciais:** As credenciais de acesso ao portal devem ser configuradas nas variáveis `PORTRAN_USER` e `PORTRAN_PASSWORD` no arquivo `.env`.

---

### 3. Implementação do Padrão de Automação

* **Modelo Gatilho:**
    * `CertificadoVeiculo(models.Model)`: Atua como o **gatilho de automação temporário**. Armazena os dados necessários para o robô e um status.

* **Lógica de Negócio (Fluxo por Sinal):**
    1.  O upload de um PDF via `dashboard` cria um registro `CertificadoVeiculo` com status `pendente`.
    2.  O sinal `post_save` em `signals.py` é acionado por esta criação. **É crucial que o handler do sinal verifique `if created` para garantir que a automação seja disparada apenas na criação inicial do objeto, e não em atualizações subsequentes.**
    3.  O handler do sinal executa o `custom command` `automacao_documentos_ipiranga` em um subprocesso.
    4.  O comando executa a automação (login, busca, extração de dados do nome do arquivo, upload).
    5.  **Regra de Limpeza Crítica:** Ao final da execução, dentro de um bloco `finally`, o comando **deve obrigatoriamente deletar o registro `CertificadoVeiculo` e o arquivo PDF associado, com tratamento de erros robusto para garantir a limpeza mesmo em caso de falhas.**

* **Gerenciamento de Tempo Limite:** A automação implementa um tempo limite global para operações de Playwright para evitar travamentos.

---

### 4. Pontos de Atenção Específicos (Lições Aprendidas)

* **Extração de Dados do Nome do Arquivo:**
    *   **Abandono do OCR:** A extração de dados via OCR foi abandonada devido à sua complexidade e instabilidade.
    *   **Formato do Nome do Arquivo:** A extração do "Número do Certificado" e da "Data de Vencimento" agora depende **estritamente** do nome do arquivo PDF. O formato mandatório é `PLACA_NUMEROCERTIFICADO_DDMMYYYY.pdf` (ex: `ABC1234_T123456_25122025.pdf`).
    *   **Função Centralizada:** A lógica de extração está na função `extract_certificate_data_from_filename` no arquivo `apps/common/services.py`. Qualquer ajuste no padrão de extração deve ser feito de forma centralizada nesta função.
    *   **Validação:** A automação deve validar o nome do arquivo no início do processo. Arquivos com formato inválido devem ser marcados com status de erro e não devem prosseguir para a automação web.

* **Interação com o Portal Ipiranga:**
    * **IDs Dinâmicos de Campos:** Os campos de formulário no portal (ex: "Número do Documento", "Vencimento") têm IDs dinâmicos (`licenca-numero-X`). A automação deve primeiro extrair o número `X` do elemento pai para então construir os seletores corretos.
    * **Instabilidade e Tempos Limite:** O portal pode apresentar "Erro Inesperado" ou lentidão. A função de login em `common/services.py` já implementa uma lógica de espera e recarregamento. Além disso, tempos limite (`timeout`) aumentados para operações críticas do Playwright (ex: `wait_for_load_state`, `wait_for`) são essenciais para a resiliência da automação.
    *   **Robustez da Automação Playwright:** A interação com o portal deve incluir tratamento de erros robusto e logging detalhado para diagnosticar problemas de navegação e preenchimento de campos.

* **Depuração e Execução:**
    * **Depuração Visual:** Para assistir a automação, altere `headless=False` na chamada `p.chromium.launch()`. **É mandatório executar o servidor Django em primeiro plano (sem `nohup` ou `&`) em um terminal com ambiente gráfico para que o navegador seja visível.** Lembre-se de reverter para `True` antes de fazer o commit.

*   **Prevenção de Looping com Contador de Tentativas (`CertificadoVeiculo`):**
    Para garantir a robustez e evitar loops infinitos, o modelo `CertificadoVeiculo` foi aprimorado com o campo `tentativas_automacao`. A automação (`automacao_documentos_ipiranga.py`) **deve** incrementar `tentativas_automacao` no início de sua execução. Se o número de tentativas exceder um limite predefinido (ex: 3), o status do certificado será alterado para `"falha_max_tentativas"`, e a automação será interrompida para aquele registro. Em caso de qualquer falha, o status do certificado **deve** ser atualizado para `"falha"` e salvo, garantindo que o registro não permaneça no estado `"pendente"` indefinidamente.

---

**Instrução:** Você não pode deletar informações de nenhum dos arquivos GEMINI.md nem de nenhum dos arquivos progress.md, os arquivos GEMINI.md do projeto Orchestra contém instruções importantes para serem seguidas e devem apenas incluir novas instruções ou ajustar aquelas que já existesm, desde que sejam ajustes para melhorar ainda mais as intruções, você NUNCA deve deletar todo o conteúdo deles, em hipótese nenhuma. O mesmo serve para todos os arquivos progress.md do projeto Orchestra, todos eles contém informações sobre o histórico do projeto, processos e procedimentos realizados ao longo do tempo, neles devem apenas serem incluídas novos históricos, processos ou procedimentos realizados, em ordem cronológica, você NUNCA deve excluiu o conteúdo completo de nenhum deles em hipótese nenhuma para incluir coisas novas.
