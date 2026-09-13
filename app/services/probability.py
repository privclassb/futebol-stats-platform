from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BookmakerOdds:
    bookmaker_name: str
    home: float
    draw: float
    away: float


@dataclass
class ProbabilityPanel:
    """Dados exibidos na área de probabilidades de um confronto.

    `is_placeholder=True` significa que ainda NÃO há um provedor de odds real
    configurado (ODDS_API_KEY vazio) — os números abaixo são só um exemplo de
    como a tela vai funcionar. Assim que um provedor de odds for contratado
    (ver README, Fase 2), esta função passa a calcular os valores de verdade
    a partir de app.models.odds.OddsSnapshot, sem mudar a página.
    """

    is_placeholder: bool
    home_win_pct: float
    draw_pct: float
    away_win_pct: float
    fair_odds_home: float
    fair_odds_draw: float
    fair_odds_away: float
    bookmakers: list[BookmakerOdds] = field(default_factory=list)
    best_value_bet: str | None = None
    arbitrage_opportunity: str | None = None
    clv_note: str | None = None


def get_probability_panel_placeholder() -> ProbabilityPanel:
    return ProbabilityPanel(
        is_placeholder=True,
        home_win_pct=45.0,
        draw_pct=27.0,
        away_win_pct=28.0,
        fair_odds_home=2.22,
        fair_odds_draw=3.70,
        fair_odds_away=3.57,
        bookmakers=[
            BookmakerOdds("Casa A (exemplo)", 2.30, 3.60, 3.40),
            BookmakerOdds("Casa B (exemplo)", 2.25, 3.75, 3.50),
            BookmakerOdds("Casa C (exemplo)", 2.35, 3.55, 3.45),
        ],
        best_value_bet="Exemplo: Casa A paga 2.30 na vitória do mandante, "
        "acima da odd justa estimada de 2.22 — value bet ilustrativo.",
        arbitrage_opportunity=None,
        clv_note="CLV (Closing Line Value) precisa de odds de abertura E de "
        "fechamento salvas — só fica disponível com provedor de odds ativo.",
    )
