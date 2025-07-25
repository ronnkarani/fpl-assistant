from django import template
from fantasy.utils import get_team_name_by_id  # Adjust import if needed

register = template.Library()
# Map team IDs to team names
TEAM_ID_NAME_MAP = {
    1: 'Arsenal',
    2: 'Aston Villa',
    3: 'Bournemouth',
    4: 'Brentford',
    5: 'Brighton',
    6: 'Burnley',
    7: 'Chelsea',
    8: 'Crystal Palace',
    9: 'Everton',
    10: 'Fulham',
    11: 'Liverpool',
    12: 'Luton',
    13: 'Man City',
    14: 'Man United',
    15: 'Newcastle',
    16: 'Nott\'m Forest',
    17: 'Sheffield Utd',
    18: 'Spurs',
    19: 'West Ham',
    20: 'Wolves',
}

@register.filter
def team_name(team_id):
    return get_team_name_by_id(team_id)
