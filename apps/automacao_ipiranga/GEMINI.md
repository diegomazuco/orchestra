**Instrução:** Por favor, responda sempre em português.

# Diretrizes Específicas para o App: automacao_ipiranga

**Contexto:** Este app é uma **implementação** do framework de automação definido em `apps/automacao_documentos`. As regras aqui complementam as diretrizes globais e do framework.

---

### 1. Visão Geral e Objetivo

* **Objetivo do App:** Conter a lógica de negócio e o código do robô (web scraper) que automatiza processos especificamente no portal Ipiranga, com foco na atualização de certificados de veículos.

---

### 2. Dependências e Configurações Específicas

* **`playwright`:** A versão deve ser estritamente `1.54.0`, conforme definido no `pyproject.toml`.
* **Credenciais:** As credenciais de acesso ao portal devem ser configuradas nas variáveis `PORTRAN_USER` e `PORTRAN_PASSWORD` no arquivo `.env`.

---

### 3. Implementação do Padrão de Automação

* **Modelo Gatilho:**
    * `CertificadoVeiculo(models.Model)`: Atua como o **gatilho de automação temporário**. Ele armazena os dados necessários para o robô (tipo de certificado, arquivo PDF) e um status (`pendente`, `processando`, `falha`, `sucesso`).

* **Lógica de Negócio (Fluxo por Sinal):**
    1.  O upload de um PDF via `dashboard` cria um registro `CertificadoVeiculo` com status `pendente`.
    2.  O sinal `post_save` em `signals.py` é acionado por esta criação.
    3.  O handler do sinal executa o `custom command` `automacao_documentos_ipiranga` em um subprocesso, passando o ID do `CertificadoVeiculo`.
    4.  O comando executa a automação (login, busca, extração de dados do PDF, upload).
    5.  **Regra de Limpeza Crítica:** Ao final da execução, dentro de um bloco `finally`, o comando **deve obrigatoriamente deletar o registro `CertificadoVeiculo` e o arquivo PDF associado** para não deixar resíduos. Esta limpeza também deve ser garantida no nível do servidor (início, reinício, término) para a pasta `media/certificados_veiculos/`.

### 3.1. Política de Limpeza de Arquivos Temporários

*   A pasta `media/certificados_veiculos/` deve ser **sempre** limpa de arquivos temporários.
*   Esta limpeza deve ocorrer:
    *   Ao final de cada execução de automação (sucesso ou falha).
    *   No início, reinício ou término do servidor Django.
*   Utilize o `custom command` `python manage.py cleanup_media` para realizar esta operação.
*   **Gerenciamento de Tempo Limite da Automação:** A automação agora inclui um tempo limite global (atualmente 90 segundos) para evitar que o navegador permaneça aberto indefinidamente em caso de travamento.
*   **Depuração Visual:** Para assistir a automação, altere `headless=False` na chamada `p.chromium.launch()` no `custom command`. **É mandatório executar o servidor Django em primeiro plano (sem `nohup` ou `&`) em um terminal com ambiente gráfico para que o navegador seja visível.** **Lembre-se de reverter para `True` antes de fazer o commit.**

---

### 4. Pontos de Atenção Específicos (Lições Aprendidas)

* **Extração de Dados do PDF (OCR):**
    * **Flexibilidade é chave:** Use regex flexíveis para contornar falhas de OCR.
    * **Exemplos de Padrões Robustos:**
        * Para textos: `r"(CERTIFICADO DE INSPE.*?)"`
        * Para datas: `r"(\d{2}/[A-Z]{3}/\d{2})"`
        * Para números de documento: `r"(\d{2}\.\d{3}\.\s*\d{3})"`
* **Interação com o Portal Ipiranga:**
    * **Instabilidade:** O portal pode apresentar um "Erro Inesperado". A função de login em `common/services.py` já implementa uma lógica de espera e recarregamento para lidar com isso.
    * **Depuração Visual:** Para assistir a automação, altere `headless=False` na chamada `p.chromium.launch()` no `custom command`. **É mandatório executar o servidor Django em primeiro plano (sem `nohup` ou `&`) em um terminal com ambiente gráfico para que o navegador seja visível.** **Lembre-se de reverter para `True` antes de fazer o commit.**
* **Correção de Execução de Subprocesso em `signals.py`:** Um `SyntaxError` anterior na construção do comando de subprocesso em `signals.py` impedia a execução correta da automação Playwright. A correção envolveu remover a injeção de código Python complexo via `python -c` e passar o comando `manage.py` diretamente ao subprocesso.
