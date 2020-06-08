import os
import networkx as nx
from evolution import analyze_net
import matplotlib.pyplot as plt
from analysis import plot_degree_distribution
#G = nx.MultiGraph.to_undirected(nx.read_pajek('network_22_5.net'))

def test_saved():
    from os import listdir
    from os.path import isfile, join
    onlyfiles = [f for f in listdir('networks/26_5/') if isfile(join('networks/26_5/', f))]
    print(onlyfiles)
    for n in onlyfiles:

        G = nx.Graph(nx.read_edgelist('networks/26_5/'+n))
        #plt.title(n)
        #nx.draw(G)
        plot_degree_distribution(G)


        print("NETWORK: ", n)
        for g in nx.connected_component_subgraphs(G):
            print(g.number_of_nodes(), nx.average_shortest_path_length(g))

        try:
            print(analyze_net(G, 0))
        except Exception:
            pass
        print("______________________________________")
        #print(G.number_of_nodes()


if __name__ == '__main__':
    test_saved()