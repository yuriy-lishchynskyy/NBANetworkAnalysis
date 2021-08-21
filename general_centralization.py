# using https://gist.github.com/aldous-rey/e6ee7b0e82e23a686d5440bf3987ee23

def getCentralization(centralities, c_type):

    c_denominator = float(1)

    n_val = float(len(centralities))

    if (c_type == "degree"):
        c_denominator = (n_val - 1) * (n_val - 2)  # pg. 15 of Centrality in Social Networks
    elif (c_type == "close"):
        c_top = (n_val - 1) * (n_val - 2)
        c_bottom = (2 * n_val) - 3
        c_denominator = float(c_top / c_bottom) # pg. 17 of Centrality in Social Networks
    elif (c_type == "between"):
        c_denominator = (n_val - 1) * (n_val - 1) * (n_val - 2) # pg. 16 of Centrality in Social Networks
    elif (c_type == "eigen"):
        c_denominator = ((2**0.5) / 2) * (n_val - 2)

    c_node_max = max(centralities.values())
    c_sorted = sorted(centralities.values(), reverse=True)
    c_numerator = 0

    for value in c_sorted:

        if c_type == "degree":
            c_numerator += (c_node_max * (n_val - 1) - value * (n_val - 1)) # remove normalisation for each value
        else:
            c_numerator += (c_node_max - value)

    network_centrality = float(c_numerator / c_denominator)

    if c_type == "between":
        network_centrality = network_centrality * 2 # pg. 10 of Centrality in Social Networks

    return network_centrality
