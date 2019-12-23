import requests
import json
import time
import csv


def get_data(path, url, name_dump):
    """
    Retrieve fpl stats from url
    Save in path with name_dump
    """
    #response = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
    response = ''
    while response == '':
        try:
            response = requests.get(url)
        except:
            time.sleep(5)
    if response.status_code != 200:
        raise Exception("Response was code " + str(response.status_code))
    response_text = response.text
    data = json.loads(response_text)
    with open(path + name_dump + '.json', 'w') as out:
        json.dump(data, out)
    return data


def parse_data(path, url, name_dump, headers_of_interest, types=''):
    data = get_data(path, url, name_dump)
    headers, raw_path = build_statistic_header(data, path + 'raw_' + name_dump + '.csv', types)
    # int_headers = ['first_name', 'second_name', 'id', 'web_name', 'now_cost', 'cost_change_start', 'element_type',
    #                'selected_by_percent', 'team', 'team_code', 'total_points', 'minutes', 'goals_scored', 'assists',
    #                'clean_sheets', 'goals_conceded', 'yellow_cards', 'red_cards', 'saves', 'bonus', 'bps']
    clean_path = clean_data(raw_path, path + 'cleaned_' + name_dump + '.csv', headers_of_interest)
    return headers, raw_path, clean_path


def build_statistic_header(statistics_dict_full, path, entry_type):
    """
    Right now, the passed stats_dict is assumed to be player data. To make this more generic/general, remove "elements"
    and pass the type (elements/events/teams...) as an argument to the function and this could clean all data.
    """
    # Empty variable to fill
    statistics_dict = statistics_dict_full[entry_type][0]
    headers = []

    # Save all keys into one massive header
    for key, val in statistics_dict.items():
        headers += [key]

    # Save all headers into a .csv file
    with open(path, 'w+', encoding='utf8', newline='') as file:
        w = csv.DictWriter(file, sorted(headers))
        w.writeheader()
        for player in statistics_dict_full[entry_type]:
            w.writerow({k: str(v).encode('utf-8').decode('utf-8') for k, v in player.items()})
    return headers, path


def clean_data(path, clean_path, headers_of_interest):
    """
    This cleaner should be able to be used as a generic cleaner, not only for player data but also gw etc.
    """
    raw_file = open(path, 'r+', encoding='utf-8')
    r = csv.DictReader(raw_file)

    with open(clean_path, 'w+', encoding='utf8', newline='') as file:
        w = csv.DictWriter(file, headers_of_interest, extrasaction='ignore')
        w.writeheader()
        for line in r:
            w.writerow(line)
    return clean_path


if __name__ == '__main__':
    team_id = "3022773"
    gameweek = "1"
    url_all_players = "https://fantasy.premierleague.com/api/bootstrap-static/"
    # All players but also teams, elements and gameweeks
    url_specific_player = "https://fantasy.premierleague.com/api/element-summary/"  # needs + str(player_id) + str('/').
    # Only for future
    url_team = "https://fantasy.premierleague.com/api/entry/" + team_id + "/"   # + str(entry_id) my own team!
    url_team_history = "https://fantasy.premierleague.com/api/entry/" + team_id + "/history/"
    url_team_picks = "https://fantasy.premierleague.com/api/entry/" + team_id + "/event/" + gameweek + "/picks/"
    url_team_transfers = "https://fantasy.premierleague.com/api/entry/" + team_id + "/transfers/"
    url_fixtures = "https://fantasy.premierleague.com/api/fixtures/"    # all fixtures

    data_path = 'C:/Users/elias/mainFolder/fantasy-premier-league/data/'
    player_headers = ['first_name', 'second_name', 'id', 'web_name', 'now_cost', 'cost_change_start', 'element_type',
                   'selected_by_percent', 'team', 'team_code', 'total_points', 'minutes', 'goals_scored', 'assists',
                   'clean_sheets', 'goals_conceded', 'yellow_cards', 'red_cards', 'saves', 'bonus', 'bps']
    team_headers = ['code', 'draw', 'form', 'id', 'loss', 'name', 'played', 'points', 'position', 'short_name',
                    'strength', 'team_division', 'unavailable', 'win', 'strength_overall_home', 'strength_overall_away',
                    'strength_attack_home', 'strength_attack_away', 'strength_defence_home', 'strength_defence_away']
    type_players = "elements"   # players
    type_teams = "teams"    # teams
    type_positions = "element_types"    # position specifications for FPL
    type_gw = "events"  # gw summary (light)

    header, raw_datapath, clp = parse_data(data_path, url_all_players, 'players', player_headers, type_players)
    print('headers:', header, '\nRaw Path:', raw_datapath, '\nCleanPath:', clp, '\n')
    header, raw_datapath, clp = parse_data(data_path, url_all_players, 'teams', team_headers, type_teams)
    print('headers:', header, '\nRaw Path:', raw_datapath, '\nCleanPath:', clp, '\n')
