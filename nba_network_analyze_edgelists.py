import networkx as nx
import os.path
import statistics as stat
import general_centralization as ncntr
import general_data as gd
import csv

years = gd.years
teams = gd.team_list
game_types = ["1", "2"]

overall_header = ["Year"] + teams
overall_measures = ["passes", "closeness_centralization", "average_contribution_ratio", "average_pass_ratio"]

overall_passes = [] # table of 30 teams, for each of 7 years (4 quantities)
overall_closeness_cntrz = []
overall_average_contribution_ratio = []
overall_average_pass_ratio = []
overall_results = [overall_passes, overall_closeness_cntrz, overall_average_contribution_ratio, overall_average_pass_ratio]

for game_type in game_types:

    if game_type == "1":
        game_s = "Regular Season"
        file_s = ""
        string_s = "_regular"
    else:
        game_s = "Playoffs"
        file_s = " playoffs"
        string_s = "_playoffs"

    for year in years:

        year_passes = [year]
        year_closeness_cntrz = [year]
        year_average_contribution_ratio = [year]
        year_average_pass_ratio = [year]

        for team in teams:

            edgelist_path = os.path.join(year + file_s, "edge_list_" + team + ".txt")
            analysis_csv_path = os.path.join(year + file_s, "analysis_" + team + ".csv")

            if (game_type == "2" and year == "2013-14" and team == "BOS"): # debugging
                xx = 3

            # READ TEAM EDGELIST
            if os.path.isfile(edgelist_path) is False: # id edgelist doesn't exist (ie team didnt go to playoffs)
                print(game_s + " | " + year + " | " + team + ": EDGELIST DOESN'T EXIST")
                continue
            if os.stat(edgelist_path).st_size == 0: # if edgelist empty - skip and go to next team
                print(game_s + " | " + year + " | " + team + ": EDGELIST EMPTY")
                continue

            file = open(edgelist_path, 'r')
            G_team = nx.read_weighted_edgelist(file, nodetype=str, create_using=nx.DiGraph())
            file.close()

            # RUN BASIC GRAPH ANALYSIS
            team_nodes = nx.number_of_nodes(G_team)
            team_edges = nx.number_of_edges(G_team)
            team_connectivity = nx.edge_connectivity(G_team)

            # RUN CENTRALITY ANALYSIS
            g_distance_dict = {(e1, e2): 1 / weight for e1, e2, weight in G_team.edges(data='weight')} # set up 'distance' measure as inverse of 'weight' - no. passes
            nx.set_edge_attributes(G_team, g_distance_dict, 'distance')

            team_in_degree_centrality = {}
            team_out_degree_centrality = {}

            for player in G_team:
                player_row = {}
                team_in_degree_centrality[player] = G_team.in_degree(player, weight="weight") # no.passes players have received (Prestige)
                team_out_degree_centrality[player] = G_team.out_degree(player, weight="weight") # no.passes players have made (Centrality)

            total_in_degree = round(sum(team_in_degree_centrality.values()))
            total_out_degree = round(sum(team_out_degree_centrality.values()))

            team_in_closeness = nx.closeness_centrality(G_team, distance="distance") # the inverse of farness, the sum of its distance to all other nodes in the network
            team_in_closeness_cntrz = ncntr.getCentralization(team_in_closeness, "close") # uses incoming distances for a node

            team_out_closeness = nx.closeness_centrality(G_team.reverse(), distance="distance") # the inverse of farness, the sum of its distance to all other nodes in the network
            team_out_closeness_cntrz = ncntr.getCentralization(team_out_closeness, "close") # uses incoming distances for a node

            team_betweenness = nx.betweenness_centrality(G_team, weight='distance') # no. times player in shortest path (1 / no. passes) between other players

            team_clustering = nx.clustering(G_team, weight=None) # fraction of possible triangles through player
            team_clustering_mean = stat.mean(team_clustering.values()) # higher clustering = player more important as middle-man in passing between 2 others

            team_pagerank = nx.pagerank(G_team, weight="weight") # probability that player has the ball at any given time

            # RUN PASSING PERFORMANCE ANALYSIS
            team_contribution = {}
            team_contribution_ratio = {}
            team_pass_ratio = {}

            for player in G_team:
                n_pass_in = round(G_team.in_degree(player, weight="weight")) # no. passes this player has received
                n_pass_out = round(G_team.out_degree(player, weight="weight")) # no. passes this player has made

                contribution = n_pass_out + n_pass_in # no. of passes player has managed (received or made)
                team_contribution[player] = contribution
                contribution_ratio = contribution / (total_in_degree + total_out_degree)
                team_contribution_ratio[player] = contribution_ratio
                pass_ratio = (n_pass_out - n_pass_in) / contribution # measure of player passing or receiving more
                team_pass_ratio[player] = pass_ratio

            # STORE OVERALL TEAM DATA FOR GIVEN YEAR
            if game_type == "1":

                year_passes.append(sum(team_in_degree_centrality.values()))
                year_closeness_cntrz.append(team_in_closeness_cntrz)
                year_average_contribution_ratio.append(stat.mean(team_contribution_ratio.values()))
                year_average_pass_ratio.append(stat.mean(team_pass_ratio.values()))

            # DELETE EXISTING CSV
            if os.path.isfile(analysis_csv_path): # delete previous version of analysis
                os.remove(analysis_csv_path)

            # WRITE DATA TO CSV
            with open(analysis_csv_path, 'w', newline='') as analysis_file: # stop csv writer inserting blank rows

                try:
                    writer = csv.writer(analysis_file)

                    header = ["Player", "Prestige", "Centrality", "Incoming Closeness", "Outgoing Closeness", "Betweenness", "Clustering", "PageRank", "Contribution", "Contribution Ratio", "Pass Ratio"]
                    writer.writerow(header)
                    players = sorted(team_in_degree_centrality.keys())

                    for player in players: # for each player write values for:

                        datarow = [player, # player
                                   team_in_degree_centrality[player], # prestige
                                   team_out_degree_centrality[player], # centrality
                                   team_in_closeness[player], # closeness (incoming passes)
                                   team_out_closeness[player], # closeness (outgoing passes)
                                   team_betweenness[player], # betweenness
                                   team_clustering[player], # clustering
                                   team_pagerank[player], # pagerank
                                   team_contribution[player], # contribution
                                   team_contribution_ratio[player], # contribution ratio
                                   team_pass_ratio[player]] # pass ratio

                        writer.writerow(datarow)

                    writer.writerow(["TOTAL", sum(team_in_degree_centrality.values()), sum(team_out_degree_centrality.values())])

                    writer.writerow("")
                    writer.writerow(["Team"])

                    team_row = [["Number of Nodes", team_nodes],
                                ["Number of Edges", team_edges],
                                ["Edge Connectivity", team_connectivity],
                                ["Incoming Closeness Centralization", team_in_closeness_cntrz],
                                ["Outgoing Closeness Centralization", team_out_closeness_cntrz],
                                ["Global Cluster Coefficient", team_clustering_mean],
                                ["Average Pass Contribution", stat.mean(team_contribution.values())],
                                ["SD Pass Contribution", stat.stdev(team_contribution.values())],
                                ["Average Pass Ratio", stat.mean(team_pass_ratio.values())],
                                ["SD Pass Ratio", stat.stdev(team_pass_ratio.values())]]

                    writer.writerows(team_row)

                    print(game_s + " | " + year + " | " + team + ": SUCCESSFUL")
                except Exception as e: # if error - print out
                    print(game_s + " | " + year + " | " + team + ": " + e)

        if game_type == "1":
            overall_passes.append(year_passes)
            overall_closeness_cntrz.append(year_closeness_cntrz)
            overall_average_contribution_ratio.append(year_average_contribution_ratio)
            overall_average_pass_ratio.append(year_average_pass_ratio)

for i, measure in enumerate(overall_measures):

    overall_results_path = os.path.join("team_analysis", "overall_" + measure + ".csv")

    # DELETE EXISTING CSV
    if os.path.isfile(overall_results_path): # delete previous version of analysis
        os.remove(overall_results_path)

    # WRITE CSV OF 7 YEARS, 30 TEAMS PER ROW
    with open(overall_results_path, 'w', newline='') as overall_file: # stop csv writer inserting blank rows
        try:
            data_table = overall_results[i]
            writer = csv.writer(overall_file)
            writer.writerow(overall_header)
            writer.writerows(data_table)

            print("Historical " + measure.capitalize() + ": SUCCESSFUL")
        except Exception as e: # if error - print out
            print("Historical " + measure.capitalize() + e)
