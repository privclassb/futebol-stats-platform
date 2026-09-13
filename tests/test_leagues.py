import unittest
from datetime import date

from app.leagues import LEAGUES, LeagueConfig, season_for


class SeasonForTests(unittest.TestCase):
    def test_european_league_before_july_uses_previous_year(self):
        premier_league = next(l for l in LEAGUES if l.slug == "premier_league")
        self.assertEqual(season_for(premier_league, date(2027, 3, 15)), 2026)

    def test_european_league_from_july_uses_current_year(self):
        premier_league = next(l for l in LEAGUES if l.slug == "premier_league")
        self.assertEqual(season_for(premier_league, date(2026, 8, 20)), 2026)

    def test_calendar_season_league_always_uses_current_year(self):
        brasileirao = next(l for l in LEAGUES if l.slug == "brasileirao")
        self.assertEqual(season_for(brasileirao, date(2026, 2, 1)), 2026)
        self.assertEqual(season_for(brasileirao, date(2026, 11, 1)), 2026)

    def test_all_mvp_leagues_are_configured_without_duplicates(self):
        self.assertEqual(len(LEAGUES), 8)
        self.assertEqual(len({l.api_football_id for l in LEAGUES}), 8)
        self.assertEqual(len({l.slug for l in LEAGUES}), 8)


if __name__ == "__main__":
    unittest.main()
