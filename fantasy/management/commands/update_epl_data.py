import requests
from django.core.management.base import BaseCommand
from fantasy.models import Fixture, PlayerStat  # Example models

class Command(BaseCommand):
    help = 'Fetches and updates EPL fixtures and player stats'

    def handle(self, *args, **kwargs):
        # Fixtures
        response = requests.get("https://fantasy.premierleague.com/api/fixtures/")
        fixtures = response.json()
        for fix in fixtures[:20]:
            Fixture.objects.update_or_create(
                fixture_id=fix['id'],
                defaults={
                    'team_a': fix['team_a'],
                    'team_h': fix['team_h'],
                    'kickoff_time': fix['kickoff_time']
                }
            )

        # Player Stats
        stats = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/").json()
        for player in stats['elements']:
            PlayerStat.objects.update_or_create(
                player_id=player['id'],
                defaults={
                    'name': f"{player['first_name']} {player['second_name']}",
                    'goals': player['goals_scored'],
                    'assists': player['assists'],
                    'injured': player['status'] in ['i', 'd'],
                }
            )

        self.stdout.write(self.style.SUCCESS("EPL data updated."))
