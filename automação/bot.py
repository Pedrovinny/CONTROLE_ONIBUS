"""
Bot BotCity - conversao de listas de frequencia (PDF do SIGAA) em CSV de importacao.

Le todos os PDFs de entrada_pdfs/, extrai matricula/nome e gera um CSV
consolidado em saida_csv/, no formato esperado por /importar/ (teste/views.py).

A lista de frequencia e organizada por turma academica, nao por rota de
onibus - nao ha como derivar a rota a partir do PDF (o mesmo aluno pode
trocar de rota ao longo do tempo). Por isso todo passageiro extraido entra
com a rota placeholder ROTA_PADRAO; a atribuicao real de rota continua
manual no sistema.

Roda desconectado do BotCity Maestro por padrao. Se disparado com
--server/--login/--key (BotMaestroSDK.from_sys_args), passa a reportar a
execucao tambem no painel do Maestro.
"""

import csv
import re
from datetime import datetime
from pathlib import Path

import pdfplumber
from botcity.maestro import BotMaestroSDK

BASE_DIR = Path(__file__).resolve().parent
ENTRADA_DIR = BASE_DIR / "entrada_pdfs"
SAIDA_DIR = BASE_DIR / "saida_csv"

# Rota provisoria para todo passageiro importado via PDF - a rota real de
# onibus e definida depois, manualmente, no sistema.
ROTA_PADRAO = "A Definir"

# Ex: "1 2024333105 AMANDA BARROS CHAVES"
RE_ALUNO = re.compile(r"^\s*\d+\s+(\d{6,12})\s+(.+?)\s*$")

BotMaestroSDK.RAISE_NOT_CONNECTED = False
maestro = BotMaestroSDK.from_sys_args()


def extrair_alunos(texto):
    alunos = []

    for linha in texto.splitlines():
        match = RE_ALUNO.match(linha)
        if match:
            matricula, nome = match.groups()
            alunos.append((matricula, nome.strip()))

    return alunos


def processar_pdf(caminho_pdf):
    with pdfplumber.open(caminho_pdf) as pdf:
        texto = "\n".join(pagina.extract_text() or "" for pagina in pdf.pages)

    alunos = extrair_alunos(texto)

    if not alunos:
        return None

    return alunos


def main():
    pdfs = sorted(ENTRADA_DIR.glob("*.pdf"))

    if not pdfs:
        print(f"Nenhum PDF encontrado em {ENTRADA_DIR}")
        return

    linhas_csv = []
    pdfs_ok = 0
    pdfs_ignorados = []

    for caminho_pdf in pdfs:
        alunos = processar_pdf(caminho_pdf)

        if alunos is None:
            pdfs_ignorados.append(caminho_pdf.name)
            print(f"[AVISO] Nao foi possivel ler '{caminho_pdf.name}' (layout inesperado) - pulando.")
            continue

        pdfs_ok += 1

        for matricula, nome in alunos:
            linhas_csv.append((matricula, nome, ROTA_PADRAO))

        print(f"[OK] {caminho_pdf.name} -> {len(alunos)} alunos")

    if not linhas_csv:
        print("Nenhum aluno extraido. Nenhum CSV foi gerado.")
        return

    SAIDA_DIR.mkdir(exist_ok=True)
    nome_saida = f"passageiros_importar_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
    caminho_saida = SAIDA_DIR / nome_saida

    # utf-8-sig: mesma codificacao que teste/views.py espera ao ler o CSV importado
    with open(caminho_saida, "w", newline="", encoding="utf-8-sig") as arquivo:
        writer = csv.writer(arquivo)
        writer.writerow(["matricula", "nome", "rota"])
        writer.writerows(linhas_csv)

    print("=" * 50)
    print(f"PDFs processados: {pdfs_ok}")
    if pdfs_ignorados:
        print(f"PDFs ignorados (layout inesperado): {len(pdfs_ignorados)} -> {', '.join(pdfs_ignorados)}")
    print(f"Total de alunos: {len(linhas_csv)}")
    print(f"CSV gerado em: {caminho_saida}")
    print("=" * 50)

    maestro.new_log_entry(
        "conversao_pdf_passageiros",
        {
            "pdfs_processados": pdfs_ok,
            "pdfs_ignorados": len(pdfs_ignorados),
            "total_alunos": len(linhas_csv),
            "csv_gerado": str(caminho_saida),
        },
    )


if __name__ == "__main__":
    main()
