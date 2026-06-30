# CONTROLE_ONIBUS

Sistema web de controle de embarque em ônibus desenvolvido em Django, usado pelo IFAM Humaitá para registrar e auditar embarques de passageiros por rota.

---

## Sumário

- [Visão Geral](#visão-geral)
- [Stack Técnica](#stack-técnica)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Schema do Banco de Dados](#schema-do-banco-de-dados)
- [Como Rodar](#como-rodar)
- [Funcionalidades](#funcionalidades)
- [Formato do CSV](#formato-do-csv)
- [Observações](#observações)

---

## Visão Geral

O sistema possui três fluxos principais:

1. **Importar CSV** — cadastra passageiros e rotas a partir de uma planilha.
2. **Leitor de Embarque** — o operador digita (ou lê via leitor de código de barras) a matrícula do passageiro; o sistema valida e registra o embarque.
3. **Relatório** — gera um PDF com todos os embarques de um período selecionado.

---

## Stack Técnica

| Camada      | Tecnologia                          |
|-------------|-------------------------------------|
| Backend     | Python 3.14 + Django 6.0.6          |
| Banco       | SQLite 3 (arquivo `dados/banco_onibus.db`) |
| Frontend    | HTML5 + Bootstrap 5.3.8 (via CDN)   |
| PDF         | ReportLab 5.0.0                     |
| Imagens     | Pillow 12.2.0                       |

---

## Estrutura do Projeto

```
CONTROLE_ONIBUS/
├── manage.py               # Ponto de entrada do Django (CLI)
├── requirements.txt        # Dependências Python
├── exemplo_passageiros.csv # Exemplo de CSV para importação
│
├── dados/
│   └── banco_onibus.db     # Banco SQLite (criado automaticamente)
│
├── src/
│   └── banco.py            # Camada de acesso ao banco (todas as queries)
│
├── static/
│   └── ifam_humaita_logo_inicio.png
│
├── templates/
│   ├── base.html           # Template base com Bootstrap e blocos
│   ├── home.html           # Página inicial com menu de navegação
│   ├── importar.html       # Formulário de upload de CSV
│   ├── leitor.html         # Interface do leitor de matrícula
│   └── relatorio.html      # Formulário de seleção de período
│
└── teste/                  # Pacote Django principal
    ├── settings.py         # Configurações do projeto
    ├── urls.py             # Roteamento de URLs
    ├── views.py            # Lógica das páginas (controllers)
    ├── wsgi.py             # Entrypoint WSGI (produção)
    └── asgi.py             # Entrypoint ASGI (async)
```

---

## Schema do Banco de Dados

```sql
-- Rotas de ônibus disponíveis
CREATE TABLE rotas (
    id_rota   INTEGER PRIMARY KEY AUTOINCREMENT,
    nome      TEXT NOT NULL UNIQUE,  -- ex: "Humaitá - Centro"
    descricao TEXT
);

-- Passageiros cadastrados, cada um vinculado a uma rota
CREATE TABLE passageiros (
    id_passageiro INTEGER PRIMARY KEY AUTOINCREMENT,
    matricula     TEXT NOT NULL UNIQUE,  -- identificador lido pelo leitor
    nome          TEXT NOT NULL,
    rota_id       INTEGER NOT NULL REFERENCES rotas(id_rota),
    ativo         INTEGER DEFAULT 1
);

-- Registro de cada embarque (uma linha por passageiro por viagem)
CREATE TABLE embarques (
    id_embarque   INTEGER PRIMARY KEY AUTOINCREMENT,
    passageiro_id INTEGER NOT NULL REFERENCES passageiros(id_passageiro),
    data          DATE NOT NULL,  -- formato YYYY-MM-DD
    hora          TIME NOT NULL   -- formato HH:MM:SS
);
```

---

## Como Rodar

```bash
# 1. Criar e ativar ambiente virtual
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / Mac

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Criar as tabelas do Django (admin, sessões etc.)
python manage.py migrate

# 4. Subir o servidor de desenvolvimento
python manage.py runserver
```

Acesse: http://127.0.0.1:8000/

> As tabelas do sistema (`rotas`, `passageiros`, `embarques`) são criadas
> automaticamente em `dados/banco_onibus.db` na primeira inicialização —
> não é necessário nenhum comando extra.

---

## Funcionalidades

### 1. Importar CSV (`/importar/`)

- Aceita upload de arquivo `.csv` com colunas: `matricula`, `nome`, `rota`.
- Cria a rota automaticamente se ela ainda não existir.
- Ignora passageiros com matrícula já cadastrada (sem duplicatas).
- Exibe um resumo de quantos registros foram importados e quantas linhas foram ignoradas.

### 2. Leitor de Embarque (`/leitor/`)

- Campo de matrícula otimizado para digitação manual ou leitura com scanner.
- Respostas visuais com cores Bootstrap:
  - **Verde** — embarque liberado e registrado.
  - **Amarelo** — passageiro já embarcou hoje.
  - **Vermelho** — matrícula não encontrada.
- O campo é limpo automaticamente após 2 segundos para a próxima leitura.

### 3. Relatório PDF (`/relatorio/`)

- Seleção de data inicial e final.
- PDF em formato A4 paisagem com tabela de embarques (matrícula, nome, rota, data, hora).
- Linhas alternadas para facilitar a leitura.
- Rodapé com total de embarques e timestamp de geração.

---

## Formato do CSV

```csv
matricula,nome,rota
2023001,Ana Paula Silva,Humaitá - Centro
2023002,Carlos Mendes,Humaitá - Vila Nova
2023003,Fernanda Costa,Humaitá - Centro
```

Veja [exemplo_passageiros.csv](exemplo_passageiros.csv) para referência.

> O arquivo pode ser salvo pelo Excel com codificação UTF-8 com BOM — o sistema trata isso automaticamente.

---

## Observações

- **Uma viagem por dia:** a regra atual permite apenas um embarque por passageiro por dia. Para suportar ida + volta no mesmo dia como dois embarques distintos, basta remover a verificação `passageiro_ja_embarcou_hoje` na view `leitor`.
- **Banco separado:** o arquivo `dados/banco_onibus.db` é o banco do sistema. O `db.sqlite3` na raiz é o banco padrão do Django (usado apenas para admin e sessões).
- **Sem autenticação:** a aplicação não possui login. Para uso em produção, considere adicionar autenticação Django ou restringir o acesso por rede.
