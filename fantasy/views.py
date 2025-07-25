import requests
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def home(request):
    # Example: Fetch data from FPL API
    fpl_data = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/').json()
    fixtures_data = requests.get('https://fantasy.premierleague.com/api/fixtures/').json()

    # Parse required sections
    players = fpl_data['elements']
    fixtures = fixtures_data

    top_scorers = sorted(players, key=lambda x: x['goals_scored'], reverse=True)
    top_assists = sorted(players, key=lambda x: x['assists'], reverse=True)
    injured_players = [p for p in players if p['status'] in ('i', 'd')]
    
    league_table = [
        {"position": 1, "team": "Manchester City", "played": 20, "points": 45},
        {"position": 2, "team": "Arsenal", "played": 20, "points": 43},
        {"position": 3, "team": "Liverpool", "played": 20, "points": 41},
        {"position": 4, "team": "Aston Villa", "played": 20, "points": 38},
        # ... add more if you want
    ]

    context = {
        "league_table": league_table,
        'fixtures': Paginator(fixtures, 5).get_page(request.GET.get('fixtures_page')),
        'top_scorers': Paginator(top_scorers, 5).get_page(request.GET.get('scorers_page')),
        'top_assists': Paginator(top_assists, 5).get_page(request.GET.get('assists_page')),
        'injured_players': Paginator(injured_players, 5).get_page(request.GET.get('injuries_page')),
    }

    return render(request, 'home.html', context)


def my_squad(request):
    return render(request, 'squad.html')


def stats(request):
    url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    response = requests.get(url)
    data = response.json()

    players = data['elements']
    teams = {team['id']: team['name'] for team in data['teams']}
    positions = {ptype['id']: ptype['singular_name'] for ptype in data['element_types']}

    formatted_players = sorted([
    {
        'id': player['id'],
        'name': f"{player['first_name']} {player['second_name']}",
        'team': teams[player['team']],
        'position': positions[player['element_type']],
        'price': player['now_cost'] / 10,
        'points': player['total_points'],
        'form': player['form'],
    }
    for player in players
    ], key=lambda x: x['points'], reverse=True)  # 🔥 Sorted by total_points descending


    # Add pagination
    paginator = Paginator(formatted_players, 20)  # Show 25 players per page
    page = request.GET.get('page')

    try:
        paginated_players = paginator.page(page)
    except PageNotAnInteger:
        paginated_players = paginator.page(1)
    except EmptyPage:
        paginated_players = paginator.page(paginator.num_pages)

    return render(request, 'stats.html', {
        'players': paginated_players,
    })


def value_picks(request):
    url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    response = requests.get(url)
    data = response.json()

    players = data['elements']
    teams = {team['id']: team['name'] for team in data['teams']}
    positions = {ptype['id']: ptype['singular_name'] for ptype in data['element_types']}

    value_players = []
    for player in players:
        price = player['now_cost'] / 10
        if price <= 7.0:  # You can adjust threshold as needed
            value_players.append({
                'id': player['id'],
                'name': f"{player['first_name']} {player['second_name']}",
                'team': teams[player['team']],
                'position': positions[player['element_type']],
                'price': price,
                'points': player['total_points'],
                'form': player['form'],
            })

    # Sort by highest points
    value_players = sorted(value_players, key=lambda x: x['points'], reverse=True)

    # Pagination (20 per page)
    paginator = Paginator(value_players, 20)
    page = request.GET.get('page')

    try:
        paginated_players = paginator.page(page)
    except PageNotAnInteger:
        paginated_players = paginator.page(1)
    except EmptyPage:
        paginated_players = paginator.page(paginator.num_pages)

    return render(request, 'value_picks.html', {'players': paginated_players})

def best_xi(request):
    response = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
    data = response.json()
    players = data["elements"]
    teams = data["teams"]

    team_difficulty = {team["id"]: team["strength"] for team in teams}

    for p in players:
        p["next_opponent_strength"] = team_difficulty.get(p["team"], 100)
        p["score"] = float(p["form"]) + int(p["total_points"]) - p["next_opponent_strength"] / 10

    sorted_players = sorted(players, key=lambda x: x["score"], reverse=True)

    selected = []
    counts = {"GKP": 0, "DEF": 0, "MID": 0, "FWD": 0}
    max_per_position = {"GKP": 2, "DEF": 5, "MID": 5, "FWD": 3}
    max_players = 16
    club_limit = {}
    
    for p in sorted_players:
        position = ["GKP", "DEF", "MID", "FWD"][p["element_type"] - 1]
        if counts[position] >= max_per_position[position]:
            continue
        if len(selected) >= max_players:
            break
        if club_limit.get(p["team"], 0) >= 3:
            continue

        counts[position] += 1
        club_limit[p["team"]] = club_limit.get(p["team"], 0) + 1
        selected.append({
            "name": p["web_name"],
            "position": position,
            "team": next(t["name"] for t in teams if t["id"] == p["team"]),
            "form": p["form"],
            "total_points": p["total_points"],
            "price": p["now_cost"] / 10,  # Add this line
            "role": "starter" if len(selected) < 11 else "sub"
        })

    return render(request, "best_xi.html", {"players": selected})


'''def get_best_xi():
    response = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/')
    data = response.json()
    elements = data['elements']
    teams = {team['id']: team['name'] for team in data['teams']}
    positions = {el['id']: el['singular_name'] for el in data['element_types']}

    # Use points_per_game or total_points for preseason prediction
    sorted_players = sorted(elements, key=lambda x: float(x['points_per_game']), reverse=True)

    # Select by position (2GK, 5DEF, 5MID, 3FWD logic)
    position_limits = {'Goalkeeper': 2, 'Defender': 5, 'Midfielder': 5, 'Forward': 3}
    selected = []

    count = {'Goalkeeper': 0, 'Defender': 0, 'Midfielder': 0, 'Forward': 0}
    for player in sorted_players:
        pos = positions[player['element_type']]
        if count[pos] < position_limits[pos]:
            selected.append({
                'name': player['web_name'],
                'position': pos,
                'team': teams[player['team']],
                'form': player['form'],
                'total_points': player['total_points'],
                'role': 'Starting' if len(selected) < 11 else 'Sub'
            })
            count[pos] += 1
        if len(selected) >= 16:
            break

    return selected'''
