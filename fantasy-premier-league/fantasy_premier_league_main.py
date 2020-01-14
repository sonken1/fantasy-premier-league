import players_calculations
import obtainingData
import os
import pathlib
import pandas as pd
import time
import sys


class GatherData:

    def __init__(self):

        self.this_season = '2019-20'
        self.base_path = str(pathlib.Path(__file__).parent.absolute()).replace('\\', '/') + '/'
        self.base_data_path = self.base_path + 'data/' + self.this_season + '/'
        self.base_url = "https://fantasy.premierleague.com/api/bootstrap-static/"
        self.url_specific_player = "https://fantasy.premierleague.com/api/element-summary/"
        # If folder already exists, don't create it again
        try:
            os.mkdir(self.base_data_path)
        except FileExistsError:
            pass

        self.player_headers = ['first_name', 'second_name', 'id', 'web_name', 'now_cost', 'cost_change_start',
                               'element_type', 'selected_by_percent', 'team', 'team_code', 'total_points', 'minutes',
                               'goals_scored', 'assists', 'clean_sheets', 'goals_conceded', 'yellow_cards', 'red_cards',
                               'saves', 'bonus', 'bps']
        self.team_headers = ['code', 'id', 'name', 'short_name', 'strength', 'team_division', 'strength_overall_home',
                             'strength_overall_away', 'strength_attack_home', 'strength_attack_away',
                             'strength_defence_home', 'strength_defence_away']
        self.player_history_headers = ['element', 'fixture', 'opponent_team', 'total_points', 'was_home',
                                       'kickoff_time', 'team_h_score', 'team_a_score','round', 'minutes',
                                       'goals_scored', 'assists', 'clean_sheets', 'goals_conceded', 'own_goals',
                                       'penalties_saved', 'penalties_missed', 'yellow_cards', 'red_cards', 'saves',
                                       'bonus', 'bps', 'influence', 'creativity', 'threat', 'ict_index', 'value',
                                       'transfers_balance', 'selected', 'transfers_in', 'transfers_out']
        self.type_players = "elements"  # players
        self.type_teams = "teams"  # teams
        self.type_history = "history"

        # Call initial method, gather and process first data
        self.gather_and_update_data()

    def gather_and_update_data(self):
        print('Downloading player data ...')
        try:
            os.mkdir(self.base_data_path + 'players/')
        except FileExistsError:
            pass
        headers, raw_path, clean_path = obtainingData.parse_data(self.base_data_path + 'players/', self.base_url,
                                                                 'players', self.player_headers, self.type_players)
        new_path_name = players_calculations.add_player_information(clean_path)

        dataframe = pd.read_csv(new_path_name)

        size = dataframe.shape[0]
        counter = 1
        print('Processing player data ...')
        for fname, lname, ident in zip(dataframe['first_name'], dataframe['second_name'], dataframe['id']):

            sys.stdout.write("\r{0}".format(str((float(counter) / size) * 100)+' %'))
            sys.stdout.flush()
            map_name = str(ident) + '_' + fname + '_' + lname + '/'

            try:
                os.mkdir(self.base_data_path + 'players/' + map_name)
            except FileExistsError:
                pass

            try:
                obtainingData.parse_data(self.base_data_path + map_name, self.url_specific_player + str(ident) + '/',
                                     'player_history', self.player_history_headers, self.type_history)
            except UnboundLocalError:
                print('\nNew Player Added to premier league:', fname + ' ' + lname)
                pass
            counter += 1

        print('\nDownloading team data ...')
        try:
            os.mkdir(self.base_data_path + 'teams/')
        except FileExistsError:
            pass
        headers, raw_path, clean_path = obtainingData.parse_data(self.base_data_path + 'teams/', self.base_url, 'teams',
                                                                 self.team_headers, self.type_teams)







e = GatherData()

# # urls:
#     url_all_players = "https://fantasy.premierleague.com/api/bootstrap-static/"
#     # All players but also teams, elements and gameweeks
#     url_specific_player_base = "https://fantasy.premierleague.com/api/element-summary/"  # needs + str(player_id) + str('/').
#     # Only for future
#     # url_team = "https://fantasy.premierleague.com/api/entry/" + team_id + "/"   # + str(entry_id) my own team!
#     # url_team_history = "https://fantasy.premierleague.com/api/entry/" + team_id + "/history/"
#     # url_team_picks = "https://fantasy.premierleague.com/api/entry/" + team_id + "/event/" + gameweek + "/picks/"
#     # url_team_transfers = "https://fantasy.premierleague.com/api/entry/" + team_id + "/transfers/"
#     # url_fixtures = "https://fantasy.premierleague.com/api/fixtures/"    # all fixtures