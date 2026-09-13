# Futebol Stats Platform

Plataforma de análises estatísticas para apostas esportivas em futebol (MVP).

## O que já funciona

- Coleta diária de jogos de 6 campeonatos (Premier League, La Liga, Serie A, Primeira Liga, Bundesliga, Brasileirão) via [API-Football](https://www.api-football.com/).
- Estatísticas de time e jogador (últimos 5 jogos + do campeonato).
- Dashboard web com lista de jogos do dia, filtros (mais escanteios, mais cartões) e página de detalhe do confronto.
- Estrutura de banco pronta para odds/probabilidades (fase 2) — hoje exibida com dados de exemplo até um provedor de odds pago ser configurado.

## Rodando localmente

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
  db/                # conexão com banco + migrations (Alembic)
  models/            # tabelas do banco (SQLAlchemy)
  schemas/           # validação/serialização (Pydantic)
  providers/         # integração com fontes de dados externas
    api_football/    # fonte principal
    scrapers/         # fontes complementares (best-effort)
  services/          # regras de negócio (ingestão, filtros, probabilidade)
  api/               # rotas da API
  jobs/              # tarefas agendadas (coleta diária)
  web/               # dashboard (templates HTML)
scripts/             # scripts utilitários (seed de dados de teste)
tests/
```

## Próximos passos (roadmap)

- **Fase 2**: integrar um provedor de odds real (comparação entre casas, value betting, fair odds) — requer plano pago (~$30-80/mês) já que provedores gratuitos cobrem no máximo 2 casas de apostas.
- **Fase 3**: modelo estatístico de probabilidade próprio, cruzando as fontes já coletadas.
- **Fase 4**: fontes complementares via scraping (FlashScore/SofaScore) para dados de jogador não cobertos pela API principal — tratado como best-effort, isolado do resto do sistema.
