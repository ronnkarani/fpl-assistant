import requests

def get_team_name_by_id(team_id):
    response = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/')
    teams = response.json().get('teams', [])
    team = next((t for t in teams if t['id'] == team_id), None)
    return team['name'] if team else 'Unknown'
