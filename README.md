# CONTROLE_ONIBUS

Sistema de Controle de Embarque em Onibus (adaptado a partir do Ticket Digital)

## Como rodar

1. python -m venv venv
2. venv\Scripts\activate  (Windows) ou source venv/bin/activate (Linux/Mac)
3. pip install -r requirements.txt
4. python manage.py migrate
5. python manage.py runserver

## Fluxo

1. Tela inicial: acesse "Importar CSV" para cadastrar os passageiros.
   O CSV precisa ter as colunas: matricula, nome, rota
   (veja exemplo_passageiros.csv)
2. "Leitor de Embarque": digite ou leia a matricula. O sistema verifica
   se o passageiro existe e se ja embarcou hoje. A rota e identificada
   automaticamente pelo cadastro do passageiro.
3. "Relatorios": escolha um periodo de datas e exporte um PDF com
   matricula, nome, rota, data e hora de cada embarque no periodo.

## Observacoes

- Os dados de alunos/refeicoes do projeto original foram substituidos por
  passageiros/embarques/rotas. O banco fica em dados/banco_onibus.db
  e e criado automaticamente na primeira execucao.
- O controle de "ja embarcou hoje" e por dia (um embarque por passageiro
  por dia). Se o onibus roda ida e volta no mesmo dia e isso precisa
  contar como 2 embarques, e so avisar que da pra ajustar essa regra.
