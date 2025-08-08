# Diretrizes Específicas para o App: automacao_ipiranga

**Contexto:** Este arquivo complementa o `GEMINI.md` principal da raiz do projeto "Orchestra" e o `GEMINI.md` do app `automacao_documentos`. As regras e o contexto aqui definidos têm **precedência** para qualquer tarefa relacionada a este app.

---

### 0. Contexto do App

Ao iniciar qualquer tarefa relacionada a este app, leia e analise o arquivo `progress.md` localizado neste diretório (`apps/automacao_ipiranga/progress.md`) para carregar o histórico de ações e o contexto atual do app.

### 1. Visão Geral do App

*   **Objetivo do App:** Este app contém a implementação específica do robô (web scraper) que automatiza processos no portal Ipiranga, focando na atualização de certificados de veículos.

### 2. Dependências e Restrições Específicas

*   **Exceção Crítica de Pacotes:** Nenhuma definida até o momento. (Avaliar a necessidade de fixar versões de pacotes de web scraping como `playwright` se forem utilizados, para evitar que atualizações do browser quebrem a automação).
*   **Fontes de Dados Adicionais:**
    *   **Principal:** Portal Ipiranga.

---

### 3. Contexto Técnico do App

*   **Modelos Principais (Implementação Real):**
    *   `VeiculoIpiranga(models.Model)`: Armazena a placa do veículo para manter um registro dos veículos já processados.
    *   `CertificadoVeiculo(models.Model)`: O coração do processo. Este modelo atua como um **gatilho de automação temporário**. Ele armazena o tipo de certificado, o arquivo PDF enviado, um status (`pendente`, `processando`, `falha`, `sucesso`) e a `ForeignKey` para o `VeiculoIpiranga`.

*   **Lógica de Negócio Chave (Fluxo por Sinal):**
    1.  Um arquivo PDF é enviado pela view `process_documents_view` no app `dashboard`.
    2.  A view extrai a placa e o tipo de certificado do nome do arquivo e cria um registro `CertificadoVeiculo` com status `pendente`.
    3.  Um sinal `post_save` em `CertificadoVeiculo` (definido em `apps/automacao_ipiranga/signals.py`) é acionado pela nova criação.
    4.  O handler do sinal executa o `custom command` `automacao_documentos_ipiranga`, passando o ID do `CertificadoVeiculo` recém-criado.
    5.  O comando executa toda a lógica de automação (login, busca, upload) e, ao final, **deleta o registro `CertificadoVeiculo` e o arquivo PDF associado**, garantindo que nenhum lixo seja deixado para trás.

*   **Comandos de Teste Específicos:**
    *   Para rodar os testes apenas deste app com relatório de cobertura:
        ```bash
        pytest apps/automacao_ipiranga/ --cov=apps.automacao_ipiranga --cov-report=html
        ```

---

### 4. Pontos de Atenção e Debug (Lições Aprendidas)

*   **Erro de OCR em PDFs:** A extração de texto de PDFs pode ser imprecisa. Ao buscar por textos específicos (ex: "CERTIFICADO DE INSPEÇÃO"), use expressões regulares flexíveis (ex: `r"(CERTIFICADO DE INSPE.*?)"`) para contornar falhas de reconhecimento de caracteres como "Ç" e "Ã".
*   **Extração de Dados Específicos do PDF (Número e Data):** Além da busca por blocos de texto, a extração de informações como número do documento e datas de vencimento de PDFs via OCR pode ser imprecisa. Utilize expressões regulares flexíveis e teste-as exaustivamente com diferentes formatos de documentos para garantir a captura correta dos dados, considerando variações de formatação e possíveis erros de reconhecimento de caracteres. Ex: para datas, considere `r"(\d{2}/[A-Z]{3}/\d{2})"` e para números, `r"(\d{2}\.\d{3}\.\s*\d{3})"`.
*   **Execução de Subprocesso (`signals.py`):** Ao disparar um `custom command` a partir de um sinal usando `subprocess.Popen`, é **mandatório** especificar o caminho absoluto para o executável do Python do ambiente virtual (`.venv/bin/python`). Não fazer isso fará com que o sistema use o Python global, resultando em erros de `ModuleNotFoundError` pois as dependências do projeto não estarão disponíveis.
*   **Debug Visual com Playwright:** Para assistir a automação em tempo real, altere o parâmetro `headless` para `False` na chamada `p.chromium.launch()` no arquivo do `custom command`. Lembre-se de reverter para `True` em produção.
*   **Falhas de Inicialização do Servidor:** Se o servidor Django não iniciar (`conexão recusada`), a causa mais provável é um erro de sintaxe ou importação em algum arquivo Python. Use o comando `python manage.py runserver --noreload` para obter o `Traceback` exato do erro no console.
