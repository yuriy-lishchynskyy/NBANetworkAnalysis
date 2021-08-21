import networkx as nx
import os.path
import matplotlib.pyplot as plt
import general_data as dg

# INPUT ANALYSIS YEAR
season_types = ["1", "2"] # 1 = regular, 2 = playoffs
years = dg.years
teams = dg.team_list

print("EXPORTING GRAPHS TO PNG\n")

for season_type in season_types:

    total_ex = 0
    success = 0
    fail = 0

    if season_type == "1":
        edge_s = ""
        output_s = "regular"
    else:
        edge_s = " playoffs"
        output_s = "playoffs"

    for year in years:
        for team in teams:

            total_ex += 1

            try:
                edgelist_path = os.path.join(year + edge_s, "edge_list_" + team + ".txt")
                output_path = os.path.join("team_graphs", output_s, year + "_" + team + "_graph.png")

                # IF FILE EXISTS ALREADY
                if os.path.isfile(output_path):
                    # os.remove(output_path)
                    print("{0} | {1} | {2} | Already Exists".format(output_s.capitalize(), year, team))
                    success += 1
                    continue

                # READ TEAM EDGELIST
                file = open(edgelist_path, 'r')
                G_team = nx.read_weighted_edgelist(file, nodetype=str, create_using=nx.DiGraph())
                file.close()

                # DRAW GRAPH
                plt.figure(figsize=(15, 10))
                pos = nx.circular_layout(G_team) # prepare circular arrangement of nodes
                nx.draw_circular(G_team, with_labels=False, connectionstyle='arc3, rad = 0.03', node_size=25, node_color="black", arrowsize=6)

                label_ratio = 1.0 / 10.0
                pos_labels = {}

                for aNode in G_team.nodes(): # shift node labels outwards so dont overlap with nodes/edges

                    x, y = pos[aNode] # Get the node's position from the layout

                    N = G_team[aNode] # Get the node's neighbourhood
                    # Find the centroid of the neighbourhood. The centroid is the average of the Neighbourhood's node's x and y coordinates respectively.
                    cx = sum(map(lambda x: pos[x][0], N)) / len(pos)
                    cy = sum(map(lambda x: pos[x][1], N)) / len(pos)
                    # Get the centroid's 'direction' or 'slope'. That is, the direction TOWARDS the centroid FROM aNode.
                    slopeY = (y - cy)
                    slopeX = (x - cx)
                    # Position the label at some distance along this line. Here, the label is positioned at about 1/10th of the distance.
                    pos_labels[aNode] = (x + slopeX * label_ratio, y + slopeY * label_ratio)

                nx.draw_networkx_labels(G_team, pos=pos_labels, font_size=10, font_color='red', font_weight='bold') # redraw the labels at their new position.

                edge_labels = dict([((u, v,), int(d['weight'])) for u, v, d in G_team.edges(data=True)]) # set edge labels as weights
                nx.draw_networkx_edge_labels(G_team, pos, edge_labels=edge_labels, label_pos=0.125, font_size=8, font_color='blue') # draw edge weights
                plt.text(-1.0, 1.0, "TEAM: {0}\nYEAR: {1}".format(team, year))
                plt.text(-1.0, -1.05, "Value adjacent to node = \nNo. of passes received from teammate")

                # EXPORT TO PNG
                plt.savefig(output_path)

                # CLEAR FIGURES
                plt.clf()
                plt.close()

                print("{0} | {1} | {2} | Exported".format(output_s.capitalize(), year, team))
                success += 1
            except FileNotFoundError:
                fail += 1
                continue

    print("Total Exported: {0}/{1}\n".format(success, total_ex))
