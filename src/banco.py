import sqlite3
from pathlib import Path
from datetime import datetime

# ======================================================
# CONFIGURAÇÃO DO BANCO
# ======================================================

BASE_DIR = Path(__file__).resolve().parent.parent
CAMINHO_BANCO = BASE_DIR / "dados" / "banco_ticket.db"

CAMINHO_BANCO.parent.mkdir(exist_ok=True)


def conectar():
    conn = sqlite3.connect(CAMINHO_BANCO)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ======================================================
# CRIAÇÃO DAS TABELAS
# ======================================================

def criar_tabelas():
    with conectar() as conn:

        conn.executescript("""

        CREATE TABLE IF NOT EXISTS campus(
            id_campus INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            sigla TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS turmas(
            id_turma INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            curso TEXT NOT NULL,
            ano INTEGER NOT NULL,
            campus_id INTEGER NOT NULL,
            FOREIGN KEY(campus_id)
            REFERENCES campus(id_campus)
        );

        CREATE TABLE IF NOT EXISTS alunos(
            id_aluno INTEGER PRIMARY KEY AUTOINCREMENT,
            matricula TEXT NOT NULL UNIQUE,
            nome TEXT NOT NULL,
            turma_id INTEGER NOT NULL,
            ativo INTEGER DEFAULT 1,
            FOREIGN KEY(turma_id)
            REFERENCES turmas(id_turma)
        );

        CREATE TABLE IF NOT EXISTS refeicoes(
            id_refeicao INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER NOT NULL,
            data DATE NOT NULL,
            hora TIME NOT NULL,
            tipo TEXT NOT NULL DEFAULT 'ALMOCO',
            FOREIGN KEY(aluno_id)
            REFERENCES alunos(id_aluno)
        );

        """)

        # Cria automaticamente o campus padrão
        conn.execute("""
            INSERT OR IGNORE INTO campus (id_campus, nome, sigla)
            VALUES (1, 'IFAM Campus Humaitá', 'CHUM')
        """)

        conn.commit()


# ======================================================
# CAMPUS
# ======================================================

def inserir_campus(nome, sigla):
    with conectar() as conn:
        conn.execute(
            """
            INSERT INTO campus(nome,sigla)
            VALUES(?,?)
            """,
            (nome, sigla)
        )
        conn.commit()


def listar_campus():
    with conectar() as conn:
        return conn.execute("""
            SELECT *
            FROM campus
            ORDER BY nome
        """).fetchall()


# ======================================================
# TURMAS
# ======================================================

def inserir_turma(nome, curso, ano, campus_id):
    with conectar() as conn:
        conn.execute("""
            INSERT INTO turmas
            (nome,curso,ano,campus_id)
            VALUES(?,?,?,?)
        """,
        (nome, curso, ano, campus_id))

        conn.commit()


def listar_turmas():
    with conectar() as conn:
        return conn.execute("""

            SELECT
                t.id_turma,
                t.nome,
                t.curso,
                t.ano,
                c.nome

            FROM turmas t

            INNER JOIN campus c

            ON c.id_campus = t.campus_id

            ORDER BY t.nome

        """).fetchall()


# ======================================================
# ALUNOS
# ======================================================

def inserir_aluno(nome, matricula, turma_id):
    with conectar() as conn:
        conn.execute("""
            INSERT INTO alunos
            (nome,matricula,turma_id)
            VALUES(?,?,?)
        """,
        (nome, matricula, turma_id))

        conn.commit()


def listar_alunos():
    with conectar() as conn:
        return conn.execute("""

            SELECT

                a.id_aluno,
                a.nome,
                a.matricula,
                t.nome

            FROM alunos a

            INNER JOIN turmas t

            ON a.turma_id=t.id_turma

            ORDER BY a.nome

        """).fetchall()


def buscar_aluno_matricula(matricula):
    with conectar() as conn:
        return conn.execute("""

            SELECT *

            FROM alunos

            WHERE matricula=?

        """, (matricula,)).fetchone()


# ======================================================
# REFEIÇÕES
# ======================================================

def registrar_refeicao(aluno_id, tipo="ALMOCO"):

    agora = datetime.now()

    data = agora.strftime("%Y-%m-%d")
    hora = agora.strftime("%H:%M:%S")

    with conectar() as conn:

        conn.execute("""

            INSERT INTO refeicoes

            (aluno_id,data,hora,tipo)

            VALUES(?,?,?,?)

        """,
        (aluno_id, data, hora, tipo))

        conn.commit()


def listar_refeicoes():
    with conectar() as conn:
        return conn.execute("""

            SELECT

                a.nome,
                a.matricula,
                r.data,
                r.hora,
                r.tipo

            FROM refeicoes r

            INNER JOIN alunos a

            ON r.aluno_id=a.id_aluno

            ORDER BY r.data DESC,
                     r.hora DESC

        """).fetchall()


def listar_refeicoes_hoje():

    hoje = datetime.now().strftime("%Y-%m-%d")

    with conectar() as conn:
        return conn.execute("""

            SELECT

                a.nome,
                a.matricula,
                r.hora

            FROM refeicoes r

            INNER JOIN alunos a

            ON r.aluno_id=a.id_aluno

            WHERE r.data=?

            ORDER BY r.hora

        """, (hoje,)).fetchall()

def buscar_turma_nome(nome):
    with conectar() as conn:

        cursor = conn.execute("""
            SELECT id_turma
            FROM turmas
            WHERE nome = ?
        """, (nome,))

        resultado = cursor.fetchone()

        if resultado:
            return resultado[0]

        return None

def aluno_ja_almocou_hoje(aluno_id):

    hoje = datetime.now().strftime("%Y-%m-%d")

    with conectar() as conn:

        cursor = conn.execute("""

            SELECT COUNT(*)

            FROM refeicoes

            WHERE aluno_id = ?

            AND data = ?

        """, (aluno_id, hoje))

        return cursor.fetchone()[0] > 0
    
def listar_refeicoes_periodo(data_inicial, data_final):

    with conectar() as conn:

        cursor = conn.execute("""

            SELECT

                a.matricula,
                a.nome,
                t.nome,
                r.data,
                r.hora

            FROM refeicoes r

            INNER JOIN alunos a

                ON r.aluno_id = a.id_aluno

            INNER JOIN turmas t

                ON a.turma_id = t.id_turma

            WHERE r.data BETWEEN ? AND ?

            ORDER BY r.data, r.hora

        """, (data_inicial, data_final))

        return cursor.fetchall()

# ======================================================
# INICIALIZAÇÃO
# ======================================================

if __name__ == "__main__":

    criar_tabelas()

    print("=" * 50)
    print("BANCO DE DADOS CRIADO COM SUCESSO!")
    print(f"Arquivo: {CAMINHO_BANCO}")
    print("=" * 50)