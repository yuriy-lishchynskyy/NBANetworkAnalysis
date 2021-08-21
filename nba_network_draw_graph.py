import networkx as nx
import os.path
import matplotlib.pyplot as plt

# INPUT ANALYSIS YEAR
year = input("Please enter year (minimum 2013-14): \n")
team = input("Please enter team (e.g. GSW): \n")
game_type = input("Please enter game type (1 = regular season, 2 = playoffs): \n")

if game_type == "1":
    game_s = "Regular Season"
    file_s = ""
else:
    game_s = "Playoffs"
    file_s = " playoffs"

edgelist_path = os.path.join(year + file_s, "edge_list_" + team + ".txt")

# READ TEAM EDGELIST
file = open(edgelist_path, 'r')
G_team = nx.read_weighted_edgelist(file, nodetype=str, create_using=nx.DiGraph())
file.close()

# DRAW GRAPH
plt.figure(figsize=(8, 8))
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

nx.draw_networkx_labels(G_team, pos=pos_labels, font_size=10, font_color='red') # redraw the labels at their new position.

edge_labels = dict([((u, v,), int(d['weight'])) for u, v, d in G_team.edges(data=True)]) # set edge labels as weights
nx.draw_networkx_edge_labels(G_team, pos, edge_labels=edge_labels, label_pos=0.125, font_size=8, font_color='blue') # draw edge weights
plt.text(-1.0, 1.0, "TEAM: {0}\nYEAR: {1}".format(team, year))
plt.text(-1.0, -1.05, "Value adjacent to node = \nNo. of passes received from teammate")

plt.show()
