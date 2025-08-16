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
    2.  O sinal `post_save` em `signals.py` é acionado por esta criação.
    3.  O handler do sinal executa o `custom command` `automacao_documentos_ipiranga` em um subprocesso.
    4.  O comando executa a automação (login, busca, extração, upload).
    5.  **Regra de Limpeza Crítica:** Ao final da execução, dentro de um bloco `finally`, o comando **deve obrigatoriamente deletar o registro `CertificadoVeiculo` e o arquivo PDF associado**.

* **Gerenciamento de Tempo Limite:** A automação implementa um tempo limite global (atualmente 90 segundos) para evitar travamentos, utilizando `asyncio.wait_for` em operações críticas como a extração OCR.

---

### 4. Pontos de Atenção Específicos (Lições Aprendidas)

* **Extração de Dados do PDF (OCR):**
    * **Calibração Iterativa:** A extração OCR é complexa. O processo deve ser iterativo, ajustando configurações do Tesseract e refinando as expressões regulares em `common/services.py` para lidar com erros de reconhecimento.
    * **Exemplos de Padrões Robustos:**
        * Para textos: `r"(CERTIFICADO DE INSPE.*?)"`
        * Para datas: `r"(\d{1,2}/[A-Z]{3}/\d{2,4})"`
        * Para números de documento: `r"([A-Z][0-9T]{6})"` (permite 'T' no lugar de dígitos)
    *   **Desafios de Tipagem (Pyright):** Mesmo com configurações relaxadas do Pyright, a tipagem de operações de OCR com bibliotecas como `fitz` e `pytesseract` pode gerar avisos ou erros (ex: `Argument type is unknown`, `Cannot access attribute`). Pode ser necessário usar `type: ignore` em linhas específicas para suprimir esses avisos/erros, especialmente em chamadas como `Image.open(io.BytesIO(pix.tobytes()))`.

* **Interação com o Portal Ipiranga:**
    * **IDs Dinâmicos de Campos:** Os campos de formulário no portal (ex: "Número do Documento", "Vencimento") têm IDs dinâmicos (`licenca-numero-X`). A automação deve primeiro extrair o número `X` do elemento pai para então construir os seletores corretos.
    * **Instabilidade:** O portal pode apresentar um "Erro Inesperado". A função de login em `common/services.py` já implementa uma lógica de espera e recarregamento para lidar com isso.
    *   **Robustez da Automação Playwright:** A interação com o portal deve incluir tratamento de erros robusto e logging detalhado para diagnosticar problemas de navegação e preenchimento de campos, especialmente quando o Pyright sinaliza `Argument type is unknown` em operações de preenchimento de formulário.

* **Depuração e Execução:**
    * **Depuração Visual:** Para assistir a automação, altere `headless=False` na chamada `p.chromium.launch()`. **É mandatório executar o servidor Django em primeiro plano (sem `nohup` ou `&`) em um terminal com ambiente gráfico para que o navegador seja visível.** Lembre-se de reverter para `True` antes de fazer o commit.
