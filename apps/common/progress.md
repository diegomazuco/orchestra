# Histórico de Progresso do App: common

Este documento registra o histórico de processos e procedimentos realizados no app `common`, servindo como um log detalhado das ações e decisões tomadas ao longo do desenvolvimento.

---

## 2025-08-21

### Consolidação de Arquivos `progress.md`

*   **Processo:** Realizada a leitura completa de todas as versões históricas do arquivo `apps/common/progress.md` através de cada commit.
*   **Análise:** Análise detalhada de todas as entradas históricas para identificar a evolução dos processos e procedimentos.
*   **Consolidação:** Criação de uma nova versão consolidada do `apps/common/progress.md`, unificando todas as entradas históricas de forma cronológica e eliminando redundâncias.
*   **Atualização:** O arquivo `apps/common/progress.md` existente foi substituído pela sua versão consolidada.

---

## 2025-08-19

### Melhorias na Extração de Dados e Serviços

*   **Função `extract_certificate_data_from_filename`:** Aprimorada a função para extrair 'Número do Certificado' e 'DATA DE VENCIMENTO' diretamente do nome do arquivo PDF, seguindo o formato padronizado `PLACA_NUMEROCERTIFICADO_DDMMYYYY.pdf`.
*   **Função de Login (`login_to_portal`):** Aprimorada a função de login para incluir lógicas de espera e recarregamento de página, aumentando a resiliência contra instabilidades de portais externos.

---

## 2025-08-18

### Implementação de Serviços Compartilhados

*   **Módulo `services.py`:** Criado o módulo `services.py` para abrigar funções e lógicas de negócio compartilhadas entre os apps, como a função de login em portais externos.
*   **Módulo `storage.py`:** Criado o módulo `storage.py` com a classe `OriginalFilenameStorage` para garantir que os arquivos sejam salvos com seus nomes originais, o que é intencional para a substituição de certificados existentes.

---

## 2025-08-17

### Configuração Inicial do App `common`

*   **Criação do App:** O app `common` foi criado para abrigar funcionalidades e lógicas compartilhadas entre os demais apps do projeto.
*   **Integração:** O app `common` foi adicionado ao `INSTALLED_APPS` em `core/settings.py`.

---

## 2025-08-16

### Definição de Estrutura de Pastas

*   **Estrutura de Pastas:** Definição da estrutura inicial de pastas do projeto, incluindo `apps/common/`.

---

## 2025-08-15

### Início do Desenvolvimento

*   **Criação do Repositório:** Repositório Git inicializado para o projeto Orchestra.
*   **Primeiro Commit:** Primeiro commit do projeto, incluindo a estrutura básica e o arquivo `progress.md` na raiz.
