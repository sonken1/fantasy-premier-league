import requests
import json
import os
import csv


def get_data(path):
    """ Retrieve the fpl player stats
    """
    response = requests.get("https://fantasy.premierleague.com/api/bootstrap-static/")
    if response.status_code != 200:
        raise Exception("Response was code " + str(response.status_code))
    response_text = response.text
    data = json.loads(response_text)
    with open(path + 'allDataRaw.json', 'w') as out:
        json.dump(data, out)
    return data


def parse_data(path):
    data = get_data(path)
    stats = build_statistic_header(data, path)


def build_statistic_header(statistics_dict_full, path):
    # Empty variable to fill
    statistics_dict = statistics_dict_full["elements"][0]
    headers = []

    # Save all keys into one massive header
    for key, val in statistics_dict.items():
        headers += [key]

    # Save all headers into a .csv file
    with open(path + 'raw_player_data.csv', 'w+', encoding='utf8', newline='') as file:
        w = csv.DictWriter(file, sorted(headers))
        w.writeheader()
        for player in statistics_dict_full["elements"]:
            w.writerow({k:str(v).encode('utf-8').decode('utf-8') for k, v in player.items()})
    return headers

    # stat_names = extract_stat_names(list_of_players[0])
    # filename = base_filename + 'players_raw.csv'
    # os.makedirs(os.path.dirname(filename), exist_ok=True)
    # f = open(filename, 'w+', encoding='utf8', newline='')
    # w = csv.DictWriter(f, sorted(stat_names))
    # w.writeheader()
    # for player in list_of_players:
    #         w.writerow({k:str(v).encode('utf-8').decode('utf-8') for k, v in player.items()})

if __name__ == '__main__':
    data_path = 'C:/Users/elias/mainFolder/fantasy-premier-league/data/'
    parse_data(data_path)
    # path = str(os.path.dirname(os.path.abspath(__file__))) + '/data/'
    # data = get_data()
    # with open(path + 'allDataRaw.json', 'w') as out:
    #     json.dump(data, out)