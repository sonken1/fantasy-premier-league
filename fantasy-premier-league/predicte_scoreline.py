import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def calculate_team_strength(dataframe, team, mu_home_scored, mu_away_scored, form_game=False):
    """
    Calculate a team's home/away strength based on what ever data is sent in
    mu_home/away_scored is the league's average home/away score per game
    """
    home_scored = dataframe[dataframe['HomeTeam'] == team]['FTHG'].sum()
    home_conceded = dataframe[dataframe['AwayTeam'] == team]['FTAG'].sum()
    away_scored = dataframe[dataframe['AwayTeam'] == team]['FTAG'].sum()
    away_conceded = dataframe[dataframe['AwayTeam'] == team]['FTHG'].sum()
    number_of_games = dataframe[dataframe['HomeTeam'] == team].shape[0]

    if form_game:
        home_scored = dataframe[dataframe['HomeTeam'] == team]['FTHG'][-5:].sum()
        home_conceded = dataframe[dataframe['AwayTeam'] == team]['FTAG'][-5:].sum()
        away_scored = dataframe[dataframe['AwayTeam'] == team]['FTAG'][-5:].sum()
        away_conceded = dataframe[dataframe['AwayTeam'] == team]['FTHG'][-5:].sum()
        number_of_games = 5

    home_attack_strength = (home_scored / number_of_games) / mu_home_scored
    home_defence_strength = (home_conceded / number_of_games) / mu_away_scored
    away_attack_strength = (away_scored / number_of_games) / mu_away_scored
    away_defence_strength = (away_conceded / number_of_games) / mu_home_scored

    return home_attack_strength, home_defence_strength, away_attack_strength, away_defence_strength


def poisson_distribution(mu, k=6):
    downsample = 0.01
    probabilities = np.zeros((int(k/downsample), 1))
    y = np.arange(0, k, downsample)
    for i, val in zip(range(len(y)), y):
        probabilities[i] = (np.exp(-mu)*mu**val)/np.math.factorial(np.floor(val))

    temp = np.zeros((k, 1))
    for i in range(0, k):
        temp[i] = np.mean(probabilities[int(i/downsample):int(len(probabilities)/k)*(i+1)])
    return temp


def poisson_matrix(p_home, p_away):
    if len(p_home) != len(p_away):
        return print('Not the same number of probabilities')

    matrix = np.outer(p_home, p_away)
    max_prob = np.max(matrix)
    max_index = np.unravel_index(matrix.argmax(), matrix.shape)

    return matrix, max_prob, max_index

def home_draw_away_probability(matrix):
    num = len(matrix)
    print('')
    home_win = []
    away_win = []
    for i in range(1,num):
        home_win.append(matrix[i, 0:i])
        away_win.append(matrix[0:i, i])
    home_win = np.sum([item for sublist in home_win for item in sublist])
    away_win = np.sum([item for sublist in away_win for item in sublist])
    draw = np.sum(matrix.diagonal())
    return home_win, away_win, draw

def plot_poisson_matrix(matrix, home, away):
    plt.matshow(matrix)
    plt.xlabel(away)
    plt.ylabel(home)
    plt.title('Scoreline probability, ' + home + ' VS ' + away)
    plt.colorbar()
    plt.show()


base_path = 'C:\\Users\\elias\\mainFolder\\fantasy-premier-league\\data\\'
end_path = '\\results\\results.csv'
this_season = '2019-20'
last_season = '2018-19'
current_season_frame = pd.read_csv(base_path+this_season+end_path)
passed_season_frame = pd.read_csv(base_path+last_season+end_path)
merged_frame = pd.concat([passed_season_frame, current_season_frame])

file_path = 'C:\\Users\\elias\\mainFolder\\fantasy-premier-league\\data\\2018-19\\results\\results.csv'
headers = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']
season_frame = pd.read_csv(file_path)
season_frame = season_frame[headers]
season_frame = merged_frame
home_goals = season_frame['FTHG'].sum()
away_goals = season_frame['FTAG'].sum()
N = season_frame.shape[0]
mu_home_scored = home_goals/N
mu_home_conceded = away_goals/N
mu_away_scored = mu_home_conceded
mu_away_conceded = mu_home_scored
season_frame = current_season_frame

home_teams = ['Bournemouth', 'Watford', 'Newcastle', 'West Ham']
away_teams = ['Chelsea', 'Liverpool', 'Burnley', 'Southampton']
prob_score = []

for ht, at in zip(home_teams, away_teams):
    s_home_a, s_home_d, s_away_a, s_away_d = calculate_team_strength(season_frame, ht, mu_home_scored,
                                                                     mu_away_scored)
    e_home_a, e_home_d, e_away_a, e_away_d = calculate_team_strength(season_frame, at, mu_home_scored,
                                                                     mu_away_scored)
    mu_home = s_home_a * e_away_d * mu_home_scored  # Home team attack strength * Away team defence strength * average number of home goals
    mu_away = e_away_a * s_home_d * mu_away_scored  # Away team attack strength * home team defence strength * average number of away goals
    probability_matrix, max_prob, max_ind = poisson_matrix(poisson_distribution(mu_home), poisson_distribution(mu_away))
    prob_score.append(ht + ' ' + str(max_ind[0]) + ' - ' + str(max_ind[1]) + ' ' + at)
    home_win, away_win, draw = home_draw_away_probability(probability_matrix)
    total_perc = home_win + away_win + draw
    home_win = home_win/total_perc
    away_win = away_win/total_perc
    draw = draw/total_perc
    teams = ht + ' VS ' + at
    season = 'Season Stats' + ': Home Win= ' + str(round(home_win*100, 1)) + ' %, Draw= ' + str(round(draw*100, 1)) + ' %, Away Win= ' + str(round(away_win*100, 1)) + ' %'
    season_goal = ht + ' ' + str(max_ind[0]) + ' - ' + str(max_ind[1]) + ' ' + at

    s_home_a, s_home_d, s_away_a, s_away_d = calculate_team_strength(season_frame, ht, mu_home_scored,
                                                                     mu_away_scored, form_game=True)
    e_home_a, e_home_d, e_away_a, e_away_d = calculate_team_strength(season_frame, at, mu_home_scored,
                                                                     mu_away_scored, form_game=True)
    mu_home = s_home_a * e_away_d * mu_home_scored  # Home team attack strength * Away team defence strength * average number of home goals
    mu_away = e_away_a * s_home_d * mu_away_scored  # Away team attack strength * home team defence strength * average number of away goals
    probability_matrix, max_prob, max_ind = poisson_matrix(poisson_distribution(mu_home), poisson_distribution(mu_away))
    prob_score.append(ht + ' ' + str(max_ind[0]) + ' - ' + str(max_ind[1]) + ' ' + at)
    home_win, away_win, draw = home_draw_away_probability(probability_matrix)
    total_perc = home_win + away_win + draw
    home_win = home_win/total_perc
    away_win = away_win/total_perc
    draw = draw/total_perc

    form = 'Form Stats' + ': Home Win= ' + str(round(home_win*100, 1)) + ' %, Draw= ' + str(round(draw*100, 1)) + ' %, Away Win= ' + str(round(away_win*100, 1)) + ' %'
    form_goal = ht + ' ' + str(max_ind[0]) + ' - ' + str(max_ind[1]) + ' ' + at
    print(teams, '\nSeason:', season, '\nForm:', form, '\nSeason:', season_goal, '\nForm:', form_goal)


base_path = 'C:\\Users\\elias\\mainFolder\\fantasy-premier-league\\data\\championship\\'
end_path1 = 'results1819.csv'
end_path2 = 'results1920.csv'
current_season_frame = pd.read_csv(base_path+end_path2)
passed_season_frame = pd.read_csv(base_path+end_path1)
merged_frame = pd.concat([passed_season_frame, current_season_frame])

headers = ['Date', 'HomeTeam', 'AwayTeam', 'FTHG', 'FTAG']
season_frame = pd.read_csv(base_path+end_path2)
season_frame = season_frame[headers]
season_frame = merged_frame
home_goals = season_frame['FTHG'].sum()
away_goals = season_frame['FTAG'].sum()
N = season_frame.shape[0]
mu_home_scored = home_goals/N
mu_home_conceded = away_goals/N
mu_away_scored = mu_home_conceded
mu_away_conceded = mu_home_scored
season_frame = current_season_frame

home_teams = ['Blackburn', 'Fulham', 'Cardiff', 'Sheffield Weds', 'Millwall', 'QPR', 'Reading', 'Huddersfield', 'Luton']
away_teams = ['Swansea', 'Preston', 'Brentford', 'Derby', 'Bristol City', 'Birmingham', 'Barnsley', 'Charlton', 'Stoke']
prob_score = []

for ht, at in zip(home_teams, away_teams):
    s_home_a, s_home_d, s_away_a, s_away_d = calculate_team_strength(season_frame, ht, mu_home_scored,
                                                                     mu_away_scored)
    e_home_a, e_home_d, e_away_a, e_away_d = calculate_team_strength(season_frame, at, mu_home_scored,
                                                                     mu_away_scored)
    mu_home = s_home_a * e_away_d * mu_home_scored  # Home team attack strength * Away team defence strength * average number of home goals
    mu_away = e_away_a * s_home_d * mu_away_scored  # Away team attack strength * home team defence strength * average number of away goals
    probability_matrix, max_prob, max_ind = poisson_matrix(poisson_distribution(mu_home), poisson_distribution(mu_away))
    prob_score.append(ht + ' ' + str(max_ind[0]) + ' - ' + str(max_ind[1]) + ' ' + at)
    home_win, away_win, draw = home_draw_away_probability(probability_matrix)
    total_perc = home_win + away_win + draw
    home_win = home_win/total_perc
    away_win = away_win/total_perc
    draw = draw/total_perc
    teams = ht + ' VS ' + at
    season = 'Season Stats' + ': Home Win= ' + str(round(home_win*100, 1)) + ' %, Draw= ' + str(round(draw*100, 1)) + ' %, Away Win= ' + str(round(away_win*100, 1)) + ' %'
    season_goal = ht + ' ' + str(max_ind[0]) + ' - ' + str(max_ind[1]) + ' ' + at

    s_home_a, s_home_d, s_away_a, s_away_d = calculate_team_strength(season_frame, ht, mu_home_scored,
                                                                     mu_away_scored, form_game=True)
    e_home_a, e_home_d, e_away_a, e_away_d = calculate_team_strength(season_frame, at, mu_home_scored,
                                                                     mu_away_scored, form_game=True)
    mu_home = s_home_a * e_away_d * mu_home_scored  # Home team attack strength * Away team defence strength * average number of home goals
    mu_away = e_away_a * s_home_d * mu_away_scored  # Away team attack strength * home team defence strength * average number of away goals
    probability_matrix, max_prob, max_ind = poisson_matrix(poisson_distribution(mu_home), poisson_distribution(mu_away))
    prob_score.append(ht + ' ' + str(max_ind[0]) + ' - ' + str(max_ind[1]) + ' ' + at)
    home_win, away_win, draw = home_draw_away_probability(probability_matrix)
    total_perc = home_win + away_win + draw
    home_win = home_win/total_perc
    away_win = away_win/total_perc
    draw = draw/total_perc

    form = 'Form Stats' + ': Home Win= ' + str(round(home_win*100, 1)) + ' %, Draw= ' + str(round(draw*100, 1)) + ' %, Away Win= ' + str(round(away_win*100, 1)) + ' %'
    form_goal = ht + ' ' + str(max_ind[0]) + ' - ' + str(max_ind[1]) + ' ' + at
    print(teams, '\nSeason:', season, '\nForm:', form, '\nSeason:', season_goal, '\nForm:', form_goal)