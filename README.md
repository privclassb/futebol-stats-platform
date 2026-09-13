# Futebol Stats Platform

Plataforma de análises estatísticas para apostas esportivas em futebol (MVP).

## O que já funciona

- Coleta diária de jogos de 6 campeonatos (Premier League, La Liga, Serie A, Primeira Liga, Bundesliga, Brasileirão) via [API-Football](https://www.api-football.com/).
- Estatísticas de time e jogador (últimos 5 jogos + do campeonato).
- Dashboard web com lista de jogos do dia, filtros (mais escanteios, mais cartões) e página de detalhe do confronto.
- Estrutura de banco pronta para odds/probabilidades (fase 2) — hoje exibida com dados de exemplo até um provedor de odds pago ser configurado.

## Colocar no ar de graça (Render)

Este repositório já vem com um `render.yaml` pronto (deploy "Blueprint"):

1. Crie uma conta em https://render.com (dá pra entrar direto com o GitHub, sem cartão de crédito).
2. No painel, clique em **New +** → **Blueprint**.
3. Escolha o repositório `futebol-stats-platform`.
4. O Render vai ler o `render.yaml` sozinho e pedir só o valor de `API_FOOTBALL_KEY` — cole sua chave da API-Football.
5. Clique em **Apply**/**Create**. O banco de dados Postgres é criado automaticamente e já fica conectado.
6. Espere o build terminar (alguns minutos) e acesse a URL que o Render mostrar (algo como `https://futebol-stats-platform.onrender.com`).

No plano grátis, o site "dorme" depois de alguns minutos sem uso — a primeira visita depois de um tempo parado pode demorar ~30-50 segundos pra carregar, é normal.

Para ver o dashboard com dados sem esperar a coleta automática rodar, abra o **Shell** do serviço no painel do Render e rode:

```bash
python -m scripts.seed_dev_data
```

## Rodando localmente (alternativa)

1. Copie `.env.example` para `.env` e preencha `API_FOOTBALL_KEY` (crie uma conta grátis em https://www.api-football.com/).
2. Suba os serviços:

   ```bash
   docker compose up --build
   ```

3. Acesse http://localhost:8000

   Se ainda não tiver uma chave da API-Football (ou quiser só ver a interface
   funcionando), popule o banco com dados de exemplo:

   ```bash
   docker compose exec app python -m scripts.seed_dev_data
   ```

   Isso cria os 6 campeonatos, times, jogos passados (com estatísticas) e um
   jogo de "hoje" para cada liga, sem gastar nenhuma chamada da API.

## Estrutura do projeto

```
app/
  main.py            # entrypoint FastAPI
  config.py          # configurações (variáveis de ambiente)
  leagues.py         # campeonatos cobertos no MVP
  db/                # conexão com banco + migrations (Alembic)
  models/            # tabelas do banco (SQLAlchemy)
  providers/         # integração com fontes de dados externas
    api_football/    # fonte principal (client + mapper)
  services/          # regras de negócio (ingestão, filtros, forma, probabilidade)
  jobs/              # tarefas agendadas (coleta diária)
  web/               # dashboard (rotas + templates HTML)
scripts/             # scripts utilitários (seed de dados de teste)
tests/
render.yaml          # deploy automático no Render
```

## Próximos passos (roadmap)

- **Fase 2**: integrar um provedor de odds real (comparação entre casas, value betting, fair odds) — requer plano pago (~$30-80/mês) já que provedores gratuitos cobrem no máximo 2 casas de apostas.
- **Fase 3**: modelo estatístico de probabilidade próprio, cruzando as fontes já coletadas.
- **Fase 4**: fontes complementares via scraping (FlashScore/SofaScore) para dados de jogador não cobertos pela API principal — tratado como best-effort, isolado do resto do sistema.
