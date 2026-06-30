"""
src/banco.py
------------
Camada de acesso ao banco de dados SQLite do sistema de controle de embarque.

Responsabilidades:
- Criar e manter o schema das tabelas (rotas, passageiros, embarques)
- Fornecer funções CRUD para cada entidade
- Encapsular toda lógica SQL, mantendo as views livres de queries diretas

Schema resumido:
    rotas       (id_rota, nome UNIQUE, descricao)
    passageiros (id_passageiro, matricula UNIQUE, nome, rota_id FK, ativo)
    embarques   (id_embarque, passageiro_id FK, data DATE, hora TIME)
"""

import sqlite3
from pathlib import Path
from datetime import datetime

# ======================================================
# CONFIGURACAO DO BANCO
# ======================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# O banco fica em <raiz_do_projeto>/dados/banco_onibus.db
CAMINHO_BANCO = BASE_DIR / "dados" / "banco_onibus.db"

# Garante que a pasta 'dados/' existe antes de qualquer operação
CAMINHO_BANCO.parent.mkdir(exist_ok=True)


def conectar() -> sqlite3.Connection:
    """Abre e retorna uma conexão com o banco SQLite com FK habilitadas."""
    conn = sqlite3.connect(CAMINHO_BANCO)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ======================================================
# CRIACAO DAS TABELAS
# ======================================================

def criar_tabelas() -> None:
    """
    Cria as tabelas do sistema caso ainda não existam.

    Chamada automaticamente ao subir o servidor Django (em views.py).
    É idempotente — pode ser chamada múltiplas vezes sem efeito colateral.
    """
    with conectar() as conn:

        conn.executescript("""

        CREATE TABLE IF NOT EXISTS rotas(
            id_rota INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            descricao TEXT
        );

        CREATE TABLE IF NOT EXISTS passageiros(
            id_passageiro INTEGER PRIMARY KEY AUTOINCREMENT,
            matricula TEXT NOT NULL UNIQUE,
            nome TEXT NOT NULL,
            rota_id INTEGER NOT NULL,
            ativo INTEGER DEFAULT 1,
            FOREIGN KEY(rota_id)
            REFERENCES rotas(id_rota)
        );

        CREATE TABLE IF NOT EXISTS embarques(
            id_embarque INTEGER PRIMARY KEY AUTOINCREMENT,
            passageiro_id INTEGER NOT NULL,
            data DATE NOT NULL,
            hora TIME NOT NULL,
            FOREIGN KEY(passageiro_id)
            REFERENCES passageiros(id_passageiro)
        );

        """)

        conn.commit()


# ======================================================
# ROTAS
# ======================================================

def inserir_rota(nome: str, descricao: str = "") -> None:
    """
    Cadastra uma nova rota no banco.

    Args:
        nome: Nome único da rota (ex: "Humaitá - Centro").
        descricao: Descrição opcional da rota.
    """
    with conectar() as conn:
        conn.execute(
            """
            INSERT INTO rotas(nome, descricao)
            VALUES(?,?)
            """,
            (nome, descricao)
        )
        conn.commit()


def listar_rotas() -> list:
    """
    Retorna todas as rotas cadastradas, ordenadas por nome.

    Returns:
        Lista de tuplas (id_rota, nome, descricao).
    """
    with conectar() as conn:
        return conn.execute("""
            SELECT *
            FROM rotas
            ORDER BY nome
        """).fetchall()


def buscar_rota_nome(nome: str) -> int | None:
    """
    Busca o ID de uma rota pelo nome exato.

    Args:
        nome: Nome da rota a localizar.

    Returns:
        id_rota (int) se encontrada, None caso contrário.
    """
    with conectar() as conn:

        cursor = conn.execute("""
            SELECT id_rota
            FROM rotas
            WHERE nome = ?
        """, (nome,))

        resultado = cursor.fetchone()

        if resultado:
            return resultado[0]

        return None


# ======================================================
# PASSAGEIROS
# ======================================================

def inserir_passageiro(nome: str, matricula: str, rota_id: int) -> None:
    """
    Cadastra um novo passageiro vinculado a uma rota.

    Args:
        nome: Nome completo do passageiro.
        matricula: Matrícula única (usada como identificador no leitor).
        rota_id: FK para a tabela rotas.
    """
    with conectar() as conn:
        conn.execute("""
            INSERT INTO passageiros
            (nome,matricula,rota_id)
            VALUES(?,?,?)
        """,
        (nome, matricula, rota_id))

        conn.commit()


def listar_passageiros() -> list:
    """
    Retorna todos os passageiros com o nome da respectiva rota.

    Returns:
        Lista de tuplas (id_passageiro, nome, matricula, nome_rota).
    """
    with conectar() as conn:
        return conn.execute("""

            SELECT

                p.id_passageiro,
                p.nome,
                p.matricula,
                r.nome

            FROM passageiros p

            INNER JOIN rotas r

            ON p.rota_id = r.id_rota

            ORDER BY p.nome

        """).fetchall()


def buscar_passageiro_matricula(matricula: str) -> tuple | None:
    """
    Localiza um passageiro pela matrícula, incluindo dados da rota.

    Args:
        matricula: Matrícula a consultar.

    Returns:
        Tupla (id_passageiro, matricula, nome, rota_id, nome_rota)
        ou None se não encontrado.
    """
    with conectar() as conn:
        return conn.execute("""

            SELECT
                p.id_passageiro,
                p.matricula,
                p.nome,
                p.rota_id,
                r.nome

            FROM passageiros p

            INNER JOIN rotas r

            ON p.rota_id = r.id_rota

            WHERE p.matricula = ?

        """, (matricula,)).fetchone()


# ======================================================
# EMBARQUES
# ======================================================

def registrar_embarque(passageiro_id: int) -> None:
    """
    Registra o embarque de um passageiro com a data e hora atuais.

    Args:
        passageiro_id: PK do passageiro que está embarcando.
    """
    agora = datetime.now()

    data = agora.strftime("%Y-%m-%d")
    hora = agora.strftime("%H:%M:%S")

    with conectar() as conn:

        conn.execute("""

            INSERT INTO embarques

            (passageiro_id,data,hora)

            VALUES(?,?,?)

        """,
        (passageiro_id, data, hora))

        conn.commit()


def listar_embarques() -> list:
    """
    Retorna todos os embarques registrados, do mais recente ao mais antigo.

    Returns:
        Lista de tuplas (nome, matricula, nome_rota, data, hora).
    """
    with conectar() as conn:
        return conn.execute("""

            SELECT

                p.nome,
                p.matricula,
                r.nome,
                e.data,
                e.hora

            FROM embarques e

            INNER JOIN passageiros p

            ON e.passageiro_id = p.id_passageiro

            INNER JOIN rotas r

            ON p.rota_id = r.id_rota

            ORDER BY e.data DESC,
                     e.hora DESC

        """).fetchall()


def listar_embarques_hoje() -> list:
    """
    Retorna apenas os embarques registrados no dia atual.

    Returns:
        Lista de tuplas (nome, matricula, nome_rota, hora).
    """
    hoje = datetime.now().strftime("%Y-%m-%d")

    with conectar() as conn:
        return conn.execute("""

            SELECT

                p.nome,
                p.matricula,
                r.nome,
                e.hora

            FROM embarques e

            INNER JOIN passageiros p

            ON e.passageiro_id = p.id_passageiro

            INNER JOIN rotas r

            ON p.rota_id = r.id_rota

            WHERE e.data = ?

            ORDER BY e.hora

        """, (hoje,)).fetchall()


def passageiro_ja_embarcou_hoje(passageiro_id: int) -> bool:
    """
    Verifica se o passageiro já possui embarque registrado no dia atual.

    Regra de negócio: cada passageiro pode embarcar apenas uma vez por dia.
    Para suportar ida + volta no mesmo dia basta remover essa restrição na view.

    Args:
        passageiro_id: PK do passageiro a verificar.

    Returns:
        True se já embarcou hoje, False caso contrário.
    """
    hoje = datetime.now().strftime("%Y-%m-%d")

    with conectar() as conn:

        cursor = conn.execute("""

            SELECT COUNT(*)

            FROM embarques

            WHERE passageiro_id = ?

            AND data = ?

        """, (passageiro_id, hoje))

        return cursor.fetchone()[0] > 0


def listar_embarques_periodo(data_inicial: str, data_final: str) -> list:
    """
    Retorna todos os embarques dentro de um intervalo de datas.

    Usado pela view de relatório para gerar o PDF com o período selecionado.

    Args:
        data_inicial: Data de início no formato 'YYYY-MM-DD'.
        data_final:   Data de fim no formato 'YYYY-MM-DD' (inclusiva).

    Returns:
        Lista de tuplas (matricula, nome, nome_rota, data, hora),
        ordenada por rota, data e hora.
    """
    with conectar() as conn:

        cursor = conn.execute("""

            SELECT

                p.matricula,
                p.nome,
                r.nome,
                e.data,
                e.hora

            FROM embarques e

            INNER JOIN passageiros p

                ON e.passageiro_id = p.id_passageiro

            INNER JOIN rotas r

                ON p.rota_id = r.id_rota

            WHERE e.data BETWEEN ? AND ?

            ORDER BY r.nome, e.data, e.hora

        """, (data_inicial, data_final))

        return cursor.fetchall()


# ======================================================
# INICIALIZACAO
# ======================================================

if __name__ == "__main__":
    # Execução direta: cria as tabelas e confirma no terminal.
    criar_tabelas()

    print("=" * 50)
    print("BANCO DE DADOS CRIADO COM SUCESSO!")
    print(f"Arquivo: {CAMINHO_BANCO}")
    print("=" * 50)
