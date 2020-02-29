import players_calculations
import obtainingData
import os
import pathlib
import pandas as pd
import time
import sys
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm


class GatherData:

    def __init__(self):

        self.this_season = '2019-20'
        self.base_path = str(pathlib.Path(__file__).parent.absolute()).replace('\\', '/') + '/'
        self.base_data_path = self.base_path + 'data/' + self.this_season + '/'
        self.base_url = "https://fantasy.premierleague.com/api/bootstrap-static/"
        self.url_specific_player = "https://fantasy.premierleague.com/api/element-summary/"


        # If folder already exists, don't create it again
        try:
            os.makedirs(self.base_data_path)
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
            map_name = str(ident) + '/'

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

        if new_players_added:
            print('\nNew Players added to premier league (has not played yet this season):')
            for new_plp in new_players_added:
                print(new_plp)

        print('\nDownloading team data ...')
        # Gather the initial teams data, light version and minor processing.
        obtainingData.parse_data(teams_path, self.base_url, 'teams', self.team_headers, self.type_teams)
        #

    def gather_specific_team_data(self, my_team_id):
        own_path = self.base_data_path + 'my_team/'
        my_team_url = "https://fantasy.premierleague.com/api/entry/" + str(my_team_id) + '/'
        print('\nDownloading your team data ...')
        data = obtainingData.get_data(own_path, my_team_url, 'my_team', False)
        team_name = data['name']
        try:
            os.makedirs(own_path + team_name)  # For teams
        except FileExistsError:
            pass
        data = obtainingData.get_data(own_path + team_name + '/', my_team_url + 'history/', 'my_team_history')

        headers, path = obtainingData.build_statistic_header(data, own_path + team_name + '/' + 'raw_my_team_history' +
                                                             '.csv', 'current')


def get_result_dataframe(file_path, season):
    players_light = pd.read_csv(file_path)

    teams = []
    for fname, lname, ident, team_id, team_id_this_season in zip(players_light['first_name'],
                                                                 players_light['second_name'], players_light['id'],
                                                                 players_light['team_code'], players_light['team']):

        if not team_id in teams:
            map_name = str(ident) + '_' + fname + '_' + lname + '\\' + 'cleaned_player_history.csv'
            try:
                path = 'C:\\Users\\elias\\mainFolder\\fantasy-premier-league\\data\\' + season + '\\players\\' + \
                       map_name
                gw_stats = pd.read_csv(path)
                try:
                    team_read = pd.read_csv('C:\\Users\\elias\\mainFolder\\fantasy-premier-league\\data\\' + season +
                                            '\\teams\\cleaned_teams.csv')
                    folder_name = str(team_id) + '_' + team_read[team_read['code'] == team_id]['name'].values[0]
                    team_path = 'C:\\Users\\elias\\mainFolder\\fantasy-premier-league\\data\\' + season + '\\teams\\' + \
                                folder_name
                    os.makedirs(team_path)  # For teams
                    teams.append(team_id)

                    home_goals = []
                    home_team = []
                    away_team = []
                    away_goals = []
                    dates = []
                    for date, was_home, opponent, home_score, away_score in zip(gw_stats['kickoff_time'], gw_stats['was_home'], gw_stats['opponent_team'], gw_stats['team_h_score'], gw_stats['team_a_score']):
                        if home_score != 'None':
                            if was_home:
                                home_team.append(team_id_this_season)
                                away_team.append(opponent)
                            else:
                                home_team.append(opponent)
                                away_team.append(team_id_this_season)
                            home_goals.append(home_score)
                            away_goals.append(away_score)
                            dates.append(date)

                    # TODO: This needs to be fixed. We want to save the results as a dataframe, but something goes wrong
                    # when i try this....
                    df_past = pd.DataFrame(np.array([dates, home_team, away_team, home_goals, away_goals], ).transpose(), columns=["date", "home_team", "away_team", "home_goals", "away_goals"])
                    df_past["home_goals"] = df_past["home_goals"].astype(int)
                    df_past["away_goals"] = df_past["away_goals"].astype(int)
                    df_past["date"] = pd.to_datetime(df_past["date"])
                    print('Created Folder:', folder_name)
                    df_past.to_csv(team_path + '\\team_history.csv', index=None, header=True)
                except FileExistsError:
                    pass
            except FileNotFoundError:
                pass


def calculate_home_advantage(file_path, team_code):
    team_id = players_calculations.map_team_code_to_id(team_code)
    team_df = pd.read_csv(file_path)
    home_df = team_df[team_df['home_team'] == team_id]
    scored = home_df['home_goals'].values
    conceded = home_df['away_goals'].values
    mean_scored, std_scored = norm.fit(scored, loc=0, scale=1)
    mean_conceded, std_conceded = norm.fit(conceded, loc=0, scale=1)
    print(np.std(scored))
    plt.hist(scored)
    plt.hist(conceded)
    plt.legend(["Density, scored", "Density, conceded"])
    plt.title(str(players_calculations.map_team_code_to_name(team_code)) + ' at home')
    plt.show()


def player_picks(id, gws):
    """
    id: team_id
    gws: list of gws
    """
    data = []
    players_path = 'C:\\Users\\elias\\mainFolder\\fantasy-premier-league\\data\\2019-20\\players\\'
    for gw in gws:
        url = 'https://fantasy.premierleague.com/api/entry/' + str(id) + '/event/' + str(gw) + '/picks/'
        gw_picks = obtainingData.get_data('path', url, 'name_dump', save_data=True)
        for entry in gw_picks['picks']:
            player = pd.read_csv(players_path + str(entry['element']) + '\\cleaned_player_history.csv')
            try:
                player_points = player[player['round'] == gw]['total_points'].values[0]
            except IndexError:
                player_points = 0
            entry.update({'player_points': int(player_points)})

        max_player_points = max(gw_picks['picks'], key=lambda x:x['player_points'])['player_points']
        gw_captain = max(gw_picks['picks'], key=lambda x:x['is_captain'])['player_points']
        gw_vice = max(gw_picks['picks'], key=lambda x: x['is_vice'])['player_points']
        data.append({'gw': gw, 'Captain points': gw_captain, 'Vice Points': gw_vice, 'Player Max': max_player_points,
                     'Lost Points': max_player_points - gw_captain})
    return data


if __name__ == "__main__":
    import pandas as pd
    id_elias = 3022773
    id_josef = 3959938
    id_max = 3321209
    id_rickard = 3553907
    name_elias = 'Spurtastic\\'
    name_josef = 'Locos Lobos\\'
    name_max = 'Snäppetörps FK\\'
    name_rickard = 'Goolaazoo\\'
    captain_picks = player_picks(id_elias, [i for i in range(1, 27)])
    lost_points_total_elias = 0
    for entry in captain_picks:
        lost_points_total_elias += entry['Lost Points']
    captain_picks = player_picks(id_josef, [i for i in range(1, 27)])
    lost_points_total_josef = 0
    for entry in captain_picks:
        lost_points_total_josef += entry['Lost Points']
    captain_picks = player_picks(id_max, [i for i in range(1, 27)])
    lost_points_total_max = 0
    for entry in captain_picks:
        lost_points_total_max += entry['Lost Points']
    captain_picks = player_picks(id_rickard, [i for i in range(1, 27)])
    lost_points_total_rickard = 0
    for entry in captain_picks:
        lost_points_total_rickard += entry['Lost Points']
    print('Elias:', lost_points_total_elias, '\nJosef:', lost_points_total_josef, '\nMax:', lost_points_total_max,
          '\nRickard:', lost_points_total_rickard)




    #calculate_home_advantage('C:/Users/elias/mainFolder/fantasy-premier-league/data/2019-20/teams/14_Liverpool/team_history.csv', 14)
    base_path = 'C:\\Users\\elias\\mainFolder\\fantasy-premier-league\\data\\2019-20\\my_team\\'
    end_path = 'raw_my_team_history.csv'
    elias = pd.read_csv(base_path + name_elias + end_path)
    josef = pd.read_csv(base_path + name_josef + end_path)
    Max = pd.read_csv(base_path + name_max + end_path)
    rickard = pd.read_csv(base_path + name_rickard + end_path)


