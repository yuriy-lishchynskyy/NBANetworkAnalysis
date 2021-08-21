import csv
import os.path
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import pandas as pd

# INPUT ANALYSIS YEAR
year = input("Please enter year (minimum 2013-14): \n")
game_type = 2 # 1 = regular season, 2 = playoffs

if game_type == 1:
    game_s = "Regular Season"
    file_s = ""
else:
    game_s = "Playoffs"
    file_s = " playoffs"

player_list_string = os.path.join(year + file_s, 'player_list.csv')

# READ IN LIST OF PLAYERS TO BE SCRAPED
player_list = {}

with open(player_list_string) as player_list_file:
    reader = csv.DictReader(player_list_file)

    for row in csv.DictReader(player_list_file):

        p_name = row["PLAYER"]
        p_id = row["PLAYER_ID"]

        player_list[p_name] = p_id

# START CHROMEDRIVER TO SCRAPE PAGES
driver = webdriver.Chrome(executable_path='C:/Program Files (x86)/Microsoft Visual Studio/Shared/Chromedriver/chromedriver.exe')

# open one player page to get rid of cookies popup in advance
driver.get('https://www.nba.com/stats/player/201939/passes-dash/?Season=2015-16&SeasonType=Regular%20Season&PerMode=Totals')
driver.implicitly_wait(5)
driver.find_element_by_xpath('//*[@id="onetrust-accept-btn-handler"]').click() # click cookies button
time.sleep(0.5) # wait for cookies pop-up to disappear

count = 0
player_count = len(player_list)
error_count = 0

print("DOWNLOADING PASSING DATA FOR {0}".format(year))

for player in player_list.keys(): # for each player in player list for given year

    count += 1

    # define portions of URL to be combined
    url_s = "https://www.nba.com/stats/player/"
    url_id = player_list[player]
    url_e = "/passes-dash/?Season=" + year + "&SeasonType=" + game_s + "&PerMode=Totals"

    url1 = url_s + url_id + url_e

    csv1 = os.path.join(year + file_s, "output_" + str(url_id) + '.csv') # location of output csv

    if os.path.isfile(csv1) is False: # if file doesn't already exist (ie data already downloaded)

        try:  # go to page and wait for it to fully load
            driver.get(url1)
            element = WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CLASS_NAME, "nba-stat-table"))) # wait until table element appears on webpage
            time.sleep(1)

            try: # read table on webpage as pandas dataframe
                df = pd.read_html(driver.page_source)[0].dropna(axis=1)
                try: # try saving as csv
                    df.to_csv(csv1, index=False)
                    result = "COMPLETED"
                except:
                    result = "FAILED TO WRITE TO CSV"
                    error_count += 1
                    pass
            except:
                result = "FAILED TO READ WEBPAGE"
                error_count += 1
                pass
        except TimeoutException: # unless no table (player didnt play that year)
            result = "NO PASSING DATA FOR PLAYER IN GIVEN YEAR"
            error_count += 1
            pass

    else:
        result = "DATA ALREADY DOWNLOADED"

    print("{0}/{1} PLAYER: {2:<20s}\t\t{3:>15s}".format(count, player_count, player, result))

print("SUCCESSFULLY DOWNLOADED DATA FOR: {0}/{1}".format(player_count - error_count, player_count))
print("FAILED TO DOWNLOAD DATA FOR: {0}/{1}".format(error_count, player_count))
driver.close()
