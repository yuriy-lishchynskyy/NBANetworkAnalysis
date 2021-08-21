import csv
import os.path
import general_data as gd

# RUN FOR ALL YEARS AND TEAMS
years = gd.years
teams = gd.team_list
game_types = ["1", "2"]

for game_type in game_types:

    for year in years:

        if game_type == 1:
            game_s = "Regular Season"
            file_s = ""
        else:
            game_s = "Playoffs"
            file_s = " playoffs"

        player_list_string = os.path.join(year + file_s, 'player_list.csv')

        total_success_count = 0
        total_fail_count = 0

        already_done_c = 0
        no_playoffs_c = 0

        # BUILD PLAYER LIST AND EDGELIST FOR EVERY TEAM
        for team in teams:

            team_player_list = {}

            team_csv_string = os.path.join(year + file_s, "team_list_" + team + ".csv")
            print("IMPORTING: {0}".format(team))

            if os.path.isfile(team_csv_string): # delete previous version of csv team file and rebuild
                os.remove(team_csv_string)

            # CREATE CSV TO STORE PLAYERS ON TEAM, AS WELL AS LIST TO BUILD EDGELIST
            with open(team_csv_string, 'w', newline='') as team_file: # open team csv to write list of players on specific team
                fieldnames = ["Player", "Player_ID"]
                writer = csv.DictWriter(team_file, fieldnames=fieldnames)

                with open(player_list_string) as player_file: # open csv to read all players and pick out those on specific team
                    reader = csv.DictReader(player_file)

                    writer.writeheader() # write header to team player list csv

                    for row in csv.DictReader(player_file):

                        p_name = row["PLAYER"]
                        p_id = row["PLAYER_ID"]
                        p_team = row["TEAM"]

                        if p_team == team:
                            writer.writerow({'Player': p_name, 'Player_ID': p_id})
                            team_player_list[p_name] = p_id

            txt_string = os.path.join(year + file_s, "edge_list_" + team + ".txt")

            if len(team_player_list) == 0: # if list of players for team is empty - team didn't go to playoffs
                print("- TEAM DIDN'T GO TO PLAYOFFS")
                no_playoffs_c += 1
                continue

            if os.path.isfile(txt_string): # if edgelist exists
                if os.stat(txt_string).st_size == 0: # if edgelist is empty, delete and re-populate
                    os.remove(txt_string)
                else: # otherwise, skip and go to next team
                    print("- ALREADY EXISTS")
                    already_done_c += 1
                    continue

            with open(txt_string, 'a') as edge_file: # open text file to write network data

                team_success_count = 0
                team_fail_count = 0

                for player in team_player_list.keys(): # for each player on team
                    player_from_pass_id = team_player_list[player]
                    player_from_pass_name = player

                    success_count = 0
                    fail_count = 0

                    csv_string = os.path.join(year + file_s, "output_" + player_from_pass_id + ".csv")

                    if os.path.isfile(csv_string) is False: # if pass data csv for current player doesnt exist: skip import
                        success_count = "NA"
                        fail_count = "NA"
                        continue

                    player_from_pass_name = player_from_pass_name.replace(" ", "_")

                    with open(csv_string) as pass_file: # open relevant player pass data csv

                        pass_file.__next__()
                        reader = csv.DictReader(pass_file)

                        for row in csv.DictReader(pass_file): # for each teamate player passed to

                            player_to_pass_name = row["Pass To"]

                            # need to reverse "to" player name structure (if 2 parts to name)
                            if "," in player_to_pass_name:
                                split_name = player_to_pass_name.split(",")
                                player_to_pass_name = split_name[1] + " " + split_name[0]

                            if player_to_pass_name[0] == " ": # if first char is space, remove
                                player_to_pass_name = player_to_pass_name[1:]

                            player_to_pass_name_old = player_to_pass_name
                            player_to_pass_name = player_to_pass_name.replace(" ", "_") # replace space with underscore (so edgelist doesnt break)

                            if player_from_pass_name != player_to_pass_name: # avoid self pass (for whatever reason)
                                try:
                                    player_to_pass_id = team_player_list[player_to_pass_name_old]
                                    n_passes = row["PASS"]

                                    edge_file.write(player_from_pass_name + '\t' + player_to_pass_name + '\t' + n_passes)
                                    edge_file.write("\n")
                                    success_count += 1
                                except KeyError: # can't find player passing to in team list (didnt play for team consistently)
                                    fail_count += 1
                                    continue

                    team_success_count += success_count
                    team_fail_count += fail_count

                    print("- Player: {0:<25} | Edges Successfully Imported: {1:5} | Edges not Imported : {2:5}".format(player, success_count, fail_count))

            total_success_count += team_success_count
            total_fail_count += team_fail_count

            print("-----------------------------------------------------------------------------------------------------")
            print("- TOTAL for: {0:<22} | Edges Successfully Imported: {1:5} | Edges not Imported : {2:5}".format(team, team_success_count, team_fail_count))

            if team_success_count == 0: # if no successfull imports - remove team file (didn't actually reach playoffs - loaned players)
                os.remove(txt_string)

            print("")
