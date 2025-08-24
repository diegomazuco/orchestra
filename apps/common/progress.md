# Histórico de Progresso do App: common

Este arquivo registra o histórico de processos e procedimentos realizados no app `common`, que abriga a lógica de negócio e serviços compartilhados pelo projeto.

## 23/08/2025 - Consolidação do Histórico

- **Contexto:** Como parte de um esforço para melhorar a base de conhecimento do projeto, todos os arquivos `progress.md` foram revisados.
- **Ação:** As entradas neste arquivo foram reescritas e consolidadas para adicionar mais contexto sobre o "porquê" das decisões de design e para criar uma narrativa de desenvolvimento mais clara e lógica.

---

## 22/08/2025 - Melhorias em Serviços Compartilhados

- **Aprimoramento na Captura de Erros de Login (`services.py`):** Para facilitar a depuração de falhas de login, o local de salvamento do screenshot de erro foi movido para o diretório `logs`, centralizando os artefatos de depuração.
- **Novo Armazenamento de Arquivos (`storage.py`):**
    - **Problema:** O comportamento padrão do Django renomeia arquivos com nomes duplicados. Para a lógica de negócio de atualização de certificados, era necessário que um novo upload com o mesmo nome de arquivo (mesma placa de veículo) substituísse o antigo.
    - **Solução:** A classe `OriginalFilenameStorage` foi implementada para forçar o salvamento com o nome original do arquivo, garantindo a substituição intencional.

---

## 19/08/2025 - Resiliência e Abandono do OCR

- **Função de Login (`login_to_portal`):** Para aumentar a resiliência contra a instabilidade de portais externos, a função de login foi aprimorada com lógicas de espera e recarregamento de página.
- **Função `extract_certificate_data_from_filename`:** Com o abandono da estratégia de OCR, esta função foi criada para se tornar o método central e único de extração de dados de certificados, baseando-se em um formato de nome de arquivo padronizado. Isso tornou o processo mais determinístico e confiável.

---

## 18/08/2025 - Centralização de Lógica de Negócio

- **Contexto:** Para evitar a duplicação de código e promover a reutilização, o app `common` foi designado para abrigar toda a lógica de negócio compartilhada.
- **Ações:**
    - **`services.py`:** Criado para conter funções de serviço, como a lógica de login em portais.
    - **`storage.py`:** Criado para conter classes de armazenamento personalizadas.

---

## 15/08/2025 a 17/08/2025 - Estruturação Inicial

- **Criação do App:** O app `common` foi criado e adicionado ao `INSTALLED_APPS`.
- **Definição da Estrutura:** A estrutura de pastas do app foi definida dentro de `apps/`.

---

## 23/08/2025 - Continuação do Trabalho

### Refatoração e Melhorias de Código
- **Ação:** Refatoração da função de extração de dados de certificados para maior clareza e robustez.
- **Detalhes:**
    - **Refatoração:** A função `extract_certificate_data_from_filename` em `services.py` foi refatorada para retornar um dataclass (`ExtractedCertificateData`) e a regex foi ajustada para maior precisão.
- **Resultado:** Código mais limpo, robusto e com uma estrutura de dados de retorno mais clara.
