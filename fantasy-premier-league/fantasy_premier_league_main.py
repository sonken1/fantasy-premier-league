import players_calculations
import obtainingData
import os
import pathlib
import pandas as pd
import time
import sys
import matplotlib.pyplot as plt
import numpy as np


class GatherData:

    def __init__(self, my_team_id):

        self.this_season = '2019-20'
        self.my_team_id = str(my_team_id)
        self.my_team_url = "https://fantasy.premierleague.com/api/entry/" + self.my_team_id + '/'
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
        self.gameweek_headers = ['id', 'name', 'deadline_time', 'average_entry_score', 'finished', 'data_checked',
                                 'highest_scoring_entry', 'deadline_time_epoch', 'deadline_time_game_offset',
                                 'highest_score', 'is_previous', 'is_current', 'is_next', 'chip_plays', 'most_selected',
                                 'most_transferred_in', 'top_element', 'top_element_info', 'transfers_made',
                                 'most_captained', 'most_vice_captained']
        self.type_players = "elements"  # players
        self.type_teams = "teams"  # teams
        self.type_history = "history"
        self.type_gameweeks = "events"

        # Call initial method, gather and process first data
        self.gather_and_update_data()

    def gather_and_update_data(self):
        # Set base paths
        players_path = self.base_data_path + 'players/'
        teams_path = self.base_data_path + 'teams/'
        gameweek_path = self.base_data_path + 'gameweeks/'
        own_path = self.base_data_path + 'my_team/'

        print('Creating folders and subfolders ...')

        # Make directories if not already existing
        try:
            os.mkdir(gameweek_path)  # For gameweeks
        except FileExistsError:
            pass

        try:
            os.mkdir(players_path)  # For players
        except FileExistsError:
            pass

        try:
            os.mkdir(teams_path)    # For teams
        except FileExistsError:
            pass

        print('\nDownloading gameweek data ...')
        headers, raw_path, clean_path = obtainingData.parse_data(gameweek_path, self.base_url, 'gameweeks',
                                                                 self.gameweek_headers, self.type_gameweeks)

        print('\nDownloading player data ...')
        # Gather the initial player data, light version and minor processing. Adding stuff
        headers, raw_path, clean_path = obtainingData.parse_data(players_path, self.base_url, 'players',
                                                                 self.player_headers, self.type_players)
        new_path_name = players_calculations.add_player_information(clean_path)

        # Load as dataframe for easy handling
        dataframe = pd.read_csv(new_path_name)


        # Counters for visualization
        number_of_players = dataframe.shape[0]
        counter = 1
        new_players_added = []

        print('\nProcessing player data ...')
        for fname, lname, ident in zip(dataframe['first_name'], dataframe['second_name'], dataframe['id']):

            # Write how many players have been processed
            sys.stdout.write("\r{0}".format(str((float(counter) / number_of_players) * 100)+' %'))
            sys.stdout.flush()

            # Name of folder to create
            map_name = str(ident) + '_' + fname + '_' + lname + '/'

            # Create individual player's directory if not already existing
            try:
                os.mkdir(players_path + map_name)
            except FileExistsError:
                pass

            # Obtain and parse + clean player data
            try:
                obtainingData.parse_data(players_path + map_name, self.url_specific_player + str(ident) + '/',
                                         'player_history', self.player_history_headers, self.type_history)
            # If player is newly bought (has no history data for this season) methods will throw error. Catch here:
            except UnboundLocalError:
                new_players_added.append(fname + ' ' + lname)
                pass
            counter += 1

        print('\nNew Players added to premier league (has not played yet this season):')
        for new_plp in new_players_added:
            print(new_plp)

        print('\nDownloading team data ...')
        # Gather the initial teams data, light version and minor processing.
        obtainingData.parse_data(teams_path, self.base_url, 'teams', self.team_headers, self.type_teams)
        #
        print('\nDownloading your team data ...')
        data = obtainingData.get_data(own_path, self.my_team_url, 'my_team', False)
        team_name = data['name']
        try:
            os.makedirs(own_path + team_name)    # For teams
        except FileExistsError:
            pass
        data = obtainingData.get_data(own_path + team_name + '/', self.my_team_url + 'history/', 'my_team_history')

        headers, path = obtainingData.build_statistic_header(data, own_path + team_name + '/' + 'raw_my_team_history' + '.csv', 'current')


id = 3022773
e = GatherData(id)
my_team_data = pd.read_csv('C:/Users/elias/mainFolder/fantasy-premier-league/data/2019-20/my_team/Spurtastic/raw_my_team_history.csv')
gw_data = pd.read_csv('C:/Users/elias/mainFolder/fantasy-premier-league/data/2019-20/gameweeks/cleaned_gameweeks.csv')

mtp = my_team_data['points']
nbr_gw = len(mtp)
gwp = gw_data['average_entry_score']
maxgw = gw_data['highest_score']
gwp = gwp[:nbr_gw]
maxgw = maxgw[:nbr_gw]
awp = [np.mean(gwp)]*nbr_gw
mawp = [np.mean(mtp)]*nbr_gw

plt.plot(mtp)
plt.plot(gwp)
# plt.plot(mawp)
# plt.plot(awp)
plt.legend(['My Team', 'All Average Points, week-by-week'])#, 'My average', 'All Average Points'])
plt.xlabel('Gameweek')
plt.ylabel('Points')
plt.show()