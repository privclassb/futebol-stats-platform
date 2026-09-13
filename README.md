# Futebol Stats Platform

Plataforma de análises estatísticas para apostas esportivas em futebol (MVP).

## O que já funciona

- Coleta diária de jogos de 6 campeonatos (Premier League, La Liga, Serie A, Primeira Liga, Bundesliga, Brasileirão) via [API-Football](https://www.api-football.com/).
- Estatísticas de time e jogador (últimos 5 jogos + do campeonato).
- Dashboard web com lista de jogos do dia, filtros (mais escanteios, mais cartões) e página de detalhe do confronto.
- Estrutura de banco pronta para odds/probabilidades (fase 2) — hoje exibida com dados de exemplo até um provedor de odds pago ser configurado.

## Colocar no ar de graça (Render + Neon)

O site fica no **Render** (grátis) e o banco de dados no **Neon** (grátis e sem
expirar, ao contrário do Postgres grátis do próprio Render):

1. Crie o banco em https://neon.tech (login com GitHub) e copie a **connection string** do projeto criado.
2. No Render, crie um **Web Service** novo apontando pro repositório `futebol-stats-platform` (o Render detecta o `Dockerfile` sozinho).
3. Em "Environment Variables", adicione:
   - `API_FOOTBALL_KEY` → sua chave da API-Football
   - `DATABASE_URL` → a connection string copiada do Neon
   - `DATABASE_SSL` → `true`
   - `ADMIN_TOKEN` → qualquer texto secreto (usado no próximo passo)
4. Crie o serviço e espere o build terminar (alguns minutos). A URL final aparece no topo da página do serviço (algo como `https://futebol-stats-platform.onrender.com`).

No plano grátis, o site "dorme" depois de alguns minutos sem uso — a primeira visita depois de um tempo parado pode demorar ~30-50 segundos pra carregar, é normal. Isso também significa que o job diário automático só roda se o site estiver acordado às 05:00 UTC — no plano grátis, é mais confiável disparar a coleta manualmente (próximo item) sempre que quiser dados atualizados.

O plano grátis do Render não dá acesso a terminal, então a coleta de dados e o "seed" de exemplo são acionados abrindo uma URL no navegador (protegida pelo `ADMIN_TOKEN` que você configurou):

- Buscar jogos reais de hoje: `https://SEU-SITE.onrender.com/admin/sync-today?token=SEU_ADMIN_TOKEN`
- Popular com dados de exemplo (só funciona se o banco ainda estiver vazio): `https://SEU-SITE.onrender.com/admin/seed?token=SEU_ADMIN_TOKEN`

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
