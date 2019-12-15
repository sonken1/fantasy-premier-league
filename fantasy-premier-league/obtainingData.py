import requests
import json
import time
import csv


def get_data(path, url, name_dump):
    """ Retrieve fpl stats from url
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


def parse_data(path):
    data = get_data(path)
    headers, raw_path = build_statistic_header(data, path)
    int_headers = ['first_name', 'second_name', 'id', 'web_name', 'now_cost', 'cost_change_start', 'element_type',
                   'selected_by_percent', 'team', 'team_code', 'total_points', 'minutes', 'goals_scored', 'assists',
                   'clean_sheets', 'goals_conceded', 'yellow_cards', 'red_cards', 'saves', 'bonus', 'bps']
    clp = clean_data(raw_path, path + 'clean_player_data.csv', int_headers)
    return headers, raw_path, clp

def clean_data(raw_path, clean_path, headers_of_interest):
    """
    This cleaner should be able to be used as a generic cleaner, not only for player data but also gw etc.
    """
    raw_file = open(raw_path, 'r+', encoding='utf-8')
    r = csv.DictReader(raw_file)

    with open(clean_path, 'w+', encoding='utf8', newline='') as file:
        w = csv.DictWriter(file, headers_of_interest, extrasaction='ignore')
        w.writeheader()
        for line in r:
            w.writerow(line)
    return clean_path

def build_statistic_header(statistics_dict_full, path):
    """
    Right now, the passed stats_dict is assumed to be player data. To make this more generic/general, remove "elements"
    and pass the type (elements/events...) as an argument to the function and this could clean all data.
    """
    # Empty variable to fill
    statistics_dict = statistics_dict_full["elements"][0]
    headers = []

    # Save all keys into one massive header
    for key, val in statistics_dict.items():
        headers += [key]

    # Save all headers into a .csv file
    raw_path = path + 'raw_player_data.csv'
    with open(raw_path, 'w+', encoding='utf8', newline='') as file:
        w = csv.DictWriter(file, sorted(headers))
        w.writeheader()
        for player in statistics_dict_full["elements"]:
            w.writerow({k:str(v).encode('utf-8').decode('utf-8') for k, v in player.items()})
    return headers, raw_path


if __name__ == '__main__':
    url_all_players = "https://fantasy.premierleague.com/api/bootstrap-static/"
    url_specific_player = "https://fantasy.premierleague.com/api/element-summary/"  # needs + str(player_id)
    url_team = "https://fantasy.premierleague.com/api/entry/"   # + str(entry_id) could be team (Arsenal) or my own team?

    data_path = 'C:/Users/elias/mainFolder/fantasy-premier-league/data/'
    h, p, clp = parse_data(data_path)

    # test_data = data_path + 'raw_player_data.csv'
    # header, raw_path = build_statistic_header('C:/Users/elias/mainFolder/fantasy-premier-league/data/allDataRaw.json', test_data)
    # print(header)