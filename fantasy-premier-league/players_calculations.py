import pandas
import numpy as np


def map_team_code_to_name(team_code):
    """
    Maps team_code from player data to team names (for visualisation)
    """
    df_teams = pandas.read_csv('C:/Users/elias/mainFolder/fantasy-premier-league/data/cleaned_teams.csv')
    return df_teams[df_teams['code'] == team_code]['name'].values[0]


def add_player_information(data_path):
    """
    Adds additional data into player .csv
    """
    df_players = pandas.read_csv(data_path)
    df_players['points_per_million'] = df_players['total_points'].div(df_players['now_cost'])
    df_players['points_per_minute'] = df_players['total_points'].div(df_players['minutes'])
    df_players['full_name'] = df_players['first_name'] + ' ' + df_players['second_name']
    new_path_name = data_path.strip(data_path.split('/')[-1]) + 'cleaned_additional_players.csv'
    df_players.to_csv(new_path_name)
    return new_path_name


def sort_top_players(data_path, by_type, number_of_top=10, limit=None, limit_type=None, ascending_sort=False):
    """
    Sorts players based on category=by_type
    """
    dataframe = pandas.read_csv(data_path)

    if limit is not None:
        cleaned_frame = dataframe[dataframe[limit_type] > limit]
    else:
        cleaned_frame = dataframe

    first_sort = cleaned_frame.sort_values(by=by_type, ascending=ascending_sort)
    second_sort = first_sort.head(number_of_top)

    top_list = ''
    string_by_type = by_type.replace("_", " ")
    for full_name, category, top_number, team in zip(second_sort['full_name'], second_sort[by_type], range(len(second_sort[by_type])), second_sort['team_code']):
        top_list += "" + str(top_number+1) + ": " + full_name + " (" + map_team_code_to_name(team) + ")" + ", with " + str(round(category,3)) + " " + string_by_type + '\n'

    return top_list

def expeted_points(player_id, data_path):

    dataframe = pandas.read_csv(data_path)
    dataframe = dataframe[dataframe['id'] == player_id]
    print('')



if __name__ == '__main__':
    path = 'C:/Users/elias/mainFolder/fantasy-premier-league/data/cleaned_players.csv'
    new_headers, new_path = add_player_information(path)
    efficient = sort_top_players(new_path, 'points_per_minute', 10, 300, 'minutes')
    price = sort_top_players(new_path, 'points_per_million')
    inflation = sort_top_players(new_path, 'cost_change_start')
    neg_inflation = sort_top_players(new_path, 'cost_change_start', ascending_sort=True)
    bonus_point_system = sort_top_players(new_path, 'bps')
    worst_bonus_point_system = sort_top_players(new_path, 'bps', limit=300, limit_type='minutes', ascending_sort=True)
    print("Most price-worthy players (top 10):")
    print(price)
    print("Most efficient players (top 10):")
    print(efficient)
    print("Most inflation players (top 10):")
    print(inflation)
    print("Least inflation players (top 10):")
    print(neg_inflation)
    print("Best players by BPS (top 10):")
    print(bonus_point_system)
    print("Worst players by BPS, that has played more than 300 minutes, (top 10):")
    print(worst_bonus_point_system)

    expeted_points(166, new_path) # 166 = Jamie Vardy
    # print("Headers in DataFrame: ", new_headers)
