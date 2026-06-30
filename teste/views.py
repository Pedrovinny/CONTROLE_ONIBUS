from django.shortcuts import render
from django.http import HttpResponse
from src.banco import *

import csv
import io


def home(request):
    return render(request, "home.html")


def importar_csv(request):

    mensagem = ""

    if request.method == "POST":

        arquivo = request.FILES.get("arquivo")

        if arquivo:

            # Lê o arquivo CSV
            texto = io.StringIO(
                arquivo.read().decode("utf-8-sig")
            )

            leitor = csv.DictReader(texto)

            # Debug
            print("=" * 50)
            print("Colunas encontradas:", leitor.fieldnames)
            print("=" * 50)

            total = 0

            for linha in leitor:

                print(linha)

                matricula = linha["matricula"].strip()
                nome = linha["nome"].strip()
                turma = linha["turma"].strip()

                # Procurar turma
                turma_id = buscar_turma_nome(turma)

                # Se não existir, cria
                if turma_id is None:

                    inserir_turma(
                        nome=turma,
                        curso="",
                        ano=2026,
                        campus_id=1
                    )

                    turma_id = buscar_turma_nome(turma)

                # Verifica se o aluno já existe
                aluno = buscar_aluno_matricula(matricula)

                if aluno is None:

                    inserir_aluno(
                        nome,
                        matricula,
                        turma_id
                    )

                    total += 1

            mensagem = f"{total} alunos importados com sucesso."

    return render(
        request,
        "importar.html",
        {
            "mensagem": mensagem
        }
    )


def leitor(request):

    mensagem = ""
    cor = "secondary"
    nome = ""

    if request.method == "POST":

        matricula = request.POST.get("matricula", "").strip()

        aluno = buscar_aluno_matricula(matricula)

        if aluno is None:

            mensagem = "Aluno não encontrado."
            cor = "danger"

        else:

            id_aluno = aluno[0]
            nome = aluno[2]

            if aluno_ja_almocou_hoje(id_aluno):

                mensagem = "Aluno já retirou a refeição hoje."
                cor = "warning"

            else:

                registrar_refeicao(id_aluno)

                mensagem = "Pode retirar a refeição."
                cor = "success"

    return render(
        request,
        "leitor.html",
        {
            "mensagem": mensagem,
            "cor": cor,
            "nome": nome
        }
    )


def relatorio(request):

    if request.method == "POST":

        data_inicial = request.POST["data_inicial"]
        data_final = request.POST["data_final"]

        registros = listar_refeicoes_periodo(
            data_inicial,
            data_final
        )

        response = HttpResponse(
            content_type="text/csv"
        )

        response["Content-Disposition"] = (
            f'attachment; filename="relatorio.csv"'
        )

        writer = csv.writer(response)

        writer.writerow([
            "Matricula",
            "Nome",
            "Turma",
            "Data",
            "Hora"
        ])

        for linha in registros:
            writer.writerow(linha)

        return response

    return render(request, "relatorio.html")