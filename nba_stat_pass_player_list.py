import os.path
import pandas as pd
import requests
import time

# INPUT ANALYSIS YEAR
year = input("Please enter year (minimum 2013-14): \n")
game_type = 2 # 1 = regular season, 2 = playoffs

if game_type == 1:
    game_s = "Regular+Season"
    file_s = ""
else:
    game_s = "Playoffs"
    file_s = " playoffs"

player_list_string = os.path.join(year + file_s, 'player_list.csv')
folder_string = year + file_s

# OPEN STATS PAGE TO PULL ALL PLAYERS WITH MINUTES PLAYED > 1
address = "https://stats.nba.com/stats/leagueLeaders?LeagueID=00&PerMode=Totals&Scope=S&Season=" + year + "&SeasonType=" + game_s + "&StatCategory=MIN"

if not os.path.exists(folder_string): # if folder for year input doesnt exist - make one
    os.makedirs(folder_string)

if os.path.isfile(player_list_string): # delete previous version of player list
    os.remove(player_list_string)

try:
    print("DOWNLOADING...")
    r = requests.get(address).json()
    time.sleep(4)

    df = pd.DataFrame(r['resultSet']['rowSet'], columns=r['resultSet']['headers'])
    df.to_csv(player_list_string, index=False)
    print('DOWNLOAD: SUCCESSFUL')
except:
    print('DOWNLOAD: FAILED')
