import pandas
import numpy as np

df_players = pandas.read_csv('C:/Users/elias/mainFolder/fantasy-premier-league/data/cleaned_players.csv')
df_players['points_per_million'] = df_players['total_points'].values
df_players['points_per_million'].div(df_players['now_cost'])
df_players.sort_values(by="total_points")

