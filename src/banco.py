import sqlite3
from pathlib import Path
from datetime import datetime

# ======================================================
# CONFIGURACAO DO BANCO
# ======================================================

BASE_DIR = Path(__file__).resolve().parent.parent
CAMINHO_BANCO = BASE_DIR / "dados" / "banco_onibus.db"

CAMINHO_BANCO.parent.mkdir(exist_ok=True)


def conectar():
    conn = sqlite3.connect(CAMINHO_BANCO)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ======================================================
# CRIACAO DAS TABELAS
# ======================================================

def criar_tabelas():
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

def inserir_rota(nome, descricao=""):
    with conectar() as conn:
        conn.execute(
            """
            INSERT INTO rotas(nome, descricao)
            VALUES(?,?)
            """,
            (nome, descricao)
        )
        conn.commit()


def listar_rotas():
    with conectar() as conn:
        return conn.execute("""
            SELECT *
            FROM rotas
            ORDER BY nome
        """).fetchall()


def buscar_rota_nome(nome):
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

def inserir_passageiro(nome, matricula, rota_id):
    with conectar() as conn:
        conn.execute("""
            INSERT INTO passageiros
            (nome,matricula,rota_id)
            VALUES(?,?,?)
        """,
        (nome, matricula, rota_id))

        conn.commit()


def listar_passageiros():
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


def buscar_passageiro_matricula(matricula):
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

def registrar_embarque(passageiro_id):

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


def listar_embarques():
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


def listar_embarques_hoje():

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


def passageiro_ja_embarcou_hoje(passageiro_id):

    hoje = datetime.now().strftime("%Y-%m-%d")

    with conectar() as conn:

        cursor = conn.execute("""

            SELECT COUNT(*)

            FROM embarques

            WHERE passageiro_id = ?

            AND data = ?

        """, (passageiro_id, hoje))

        return cursor.fetchone()[0] > 0


def listar_embarques_periodo(data_inicial, data_final):

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

    criar_tabelas()

    print("=" * 50)
    print("BANCO DE DADOS CRIADO COM SUCESSO!")
    print(f"Arquivo: {CAMINHO_BANCO}")
    print("=" * 50)
