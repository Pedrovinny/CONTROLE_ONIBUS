"""
teste/urls.py
-------------
Mapeamento de URLs para as views do sistema de controle de embarque.

Rotas registradas:
    /              → views.home         — Página inicial
    /importar/     → views.importar_csv — Importação de passageiros via CSV
    /leitor/       → views.leitor       — Leitura de matrícula e registro de embarque
    /relatorio/    → views.relatorio    — Geração de relatório PDF por período
    /admin/        → admin.site.urls    — Interface administrativa do Django
"""

from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("importar/", views.importar_csv, name="importar_csv"),
    path("leitor/", views.leitor, name="leitor"),
    path("relatorio/", views.relatorio, name="relatorio"),
]
