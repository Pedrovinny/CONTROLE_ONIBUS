from django.shortcuts import render
from django.http import HttpResponse
from src.banco import *

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)
from reportlab.lib.styles import getSampleStyleSheet

import csv
import io
from datetime import datetime

# Garante que as tabelas existem ao subir o servidor
# (no projeto original isso só rodava se "python src/banco.py"
# fosse executado manualmente antes).
criar_tabelas()


def home(request):
    return render(request, "home.html")


def importar_csv(request):

    mensagem = ""

    if request.method == "POST":

        arquivo = request.FILES.get("arquivo")

        if arquivo:

            # Le o arquivo CSV
            texto = io.StringIO(
                arquivo.read().decode("utf-8-sig")
            )

            leitor = csv.DictReader(texto)

            total = 0
            erros = 0

            for linha in leitor:

                try:
                    matricula = linha["matricula"].strip()
                    nome = linha["nome"].strip()
                    rota = linha["rota"].strip()
                except (KeyError, AttributeError):
                    erros += 1
                    continue

                if not matricula or not nome or not rota:
                    erros += 1
                    continue

                # Procurar rota
                rota_id = buscar_rota_nome(rota)

                # Se nao existir, cria
                if rota_id is None:

                    inserir_rota(
                        nome=rota,
                        descricao=""
                    )

                    rota_id = buscar_rota_nome(rota)

                # Verifica se o passageiro ja existe
                passageiro = buscar_passageiro_matricula(matricula)

                if passageiro is None:

                    inserir_passageiro(
                        nome,
                        matricula,
                        rota_id
                    )

                    total += 1

            mensagem = f"{total} passageiros importados com sucesso."

            if erros:
                mensagem += f" ({erros} linhas ignoradas por dados incompletos.)"

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
    rota_nome = ""

    if request.method == "POST":

        matricula = request.POST.get("matricula", "").strip()

        passageiro = buscar_passageiro_matricula(matricula)

        if passageiro is None:

            mensagem = "Passageiro não encontrado."
            cor = "danger"

        else:

            id_passageiro = passageiro[0]
            nome = passageiro[2]
            rota_nome = passageiro[4]

            if passageiro_ja_embarcou_hoje(id_passageiro):

                mensagem = "Passageiro já embarcou hoje."
                cor = "warning"

            else:

                registrar_embarque(id_passageiro)

                mensagem = "Embarque liberado."
                cor = "success"

    return render(
        request,
        "leitor.html",
        {
            "mensagem": mensagem,
            "cor": cor,
            "nome": nome,
            "rota_nome": rota_nome
        }
    )


def relatorio(request):

    if request.method == "POST":

        data_inicial = request.POST["data_inicial"]
        data_final = request.POST["data_final"]

        registros = listar_embarques_periodo(
            data_inicial,
            data_final
        )

        response = HttpResponse(content_type="application/pdf")

        response["Content-Disposition"] = (
            'attachment; filename="relatorio_onibus.pdf"'
        )

        doc = SimpleDocTemplate(
            response,
            pagesize=landscape(A4),
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            rightMargin=1.5 * cm,
        )

        estilos = getSampleStyleSheet()
        elementos = []

        titulo = Paragraph(
            "Relatório de Embarques", estilos["Title"]
        )
        elementos.append(titulo)

        subtitulo = Paragraph(
            f"Período: {data_inicial} a {data_final}",
            estilos["Normal"]
        )
        elementos.append(subtitulo)
        elementos.append(Spacer(1, 0.6 * cm))

        cabecalho = ["Matrícula", "Nome", "Rota", "Data", "Hora"]
        dados_tabela = [cabecalho] + [list(linha) for linha in registros]

        tabela = Table(dados_tabela, repeatRows=1)

        tabela.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d6efd")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]))

        elementos.append(tabela)

        elementos.append(Spacer(1, 0.8 * cm))

        rodape = Paragraph(
            f"Total de embarques no período: {len(registros)} — "
            f"Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
            estilos["Normal"]
        )
        elementos.append(rodape)

        doc.build(elementos)

        return response

    return render(request, "relatorio.html")
