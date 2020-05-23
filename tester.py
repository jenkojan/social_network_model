import networkx as nx
from evolution import analyze_net
#G = nx.MultiGraph.to_undirected(nx.read_pajek('network_22_5.net'))
G = nx.Graph(nx.read_edgelist('network_22_5'))

analyze_net(G)
