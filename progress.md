# Histórico de Progresso do Projeto Orchestra

Este arquivo registra as principais ações e configurações realizadas no projeto principal "Orchestra".

## 25 de Julho de 2025

### Inicialização do Projeto
- Verificado o ambiente e a ausência de `requirements.txt`.
- Instalado o Django utilizando `uv add django`.
- Criado o projeto Django `core` no diretório raiz (`django-admin startproject core .`).
- Criado o diretório `apps/` para subprojetos (`mkdir apps`).
- Criado o arquivo `.gitkeep` em `apps/` para rastreamento Git (`touch apps/.gitkeep`).
- Executadas as migrações iniciais do Django (`python manage.py migrate`).

### Ajustes de Configuração Global
- **Atualização do GEMINI.md:** Ajustada a seção "3.2. Ambiente e Dependências (`uv` e `.env`)" para reforçar o uso exclusivo de `uv add` para gerenciamento de pacotes e dependências, e para referenciar `pyproject.toml` em vez de `requirements.txt`.
- **Configuração de Idioma e Fuso Horário:**
    - Alterado `LANGUAGE_CODE` para `'pt-br'` em `core/settings.py`.
    - Alterado `TIME_ZONE` para `'America/Sao_Paulo'` em `core/settings.py`.
- **Instalação de Dependências Globais:**
    - Instalado `playwright` e `python-decouple` utilizando `uv add playwright python-decouple`.
    - Instalados os navegadores do Playwright (`playwright install`).
- **Estrutura de Arquivos:**
    - Criado o diretório `media/licencas` para armazenamento de arquivos de licença (`mkdir -p media/licencas`).

## 28 de Julho de 2025

### Configuração e Sincronização do Repositório Git
- **Diagnóstico Inicial:** Verificado o status do Git e constatado que não havia um repositório remoto (`origin`) configurado e que existiam alterações não commitadas.
- **Criação do Repositório Remoto:** O repositório `orchestra` foi criado manualmente no GitHub (https://github.com/diegomazuco/orchestra).
- **Conexão Local-Remoto:** O repositório remoto foi adicionado ao projeto local com o nome `origin`.
- **Consistência de Branches:** O branch local `master` foi renomeado para `main` para alinhar com o padrão do GitHub.
- **Primeiro Push:** Realizado o primeiro push para o repositório remoto, sincronizando o histórico local com o remoto após resolver um conflito inicial com `git pull --rebase`.
- **Formalização das Diretrizes:** Atualizadas as diretrizes de fluxo de trabalho Git nos arquivos `GEMINI.md` (principal e do app `automacao_ibama`) para incluir a obrigatoriedade do `git pull` na inicialização, o padrão de commits detalhados e o procedimento de push seguro.
- **Commit das Diretrizes:** As alterações nos arquivos `GEMINI.md` foram commitadas e enviadas ao repositório remoto.