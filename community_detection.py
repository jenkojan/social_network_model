
import networkx as nx
import numpy as np


def infomap_detection():
    import infomap
    im = infomap.Infomap()
    path = r'networks/21_6/start'
    path = r'networks/7_6/network_pConn_0.0_pBr_0.48'
    #path = r'facebook_combined.txt'
    G = nx.Graph(nx.read_edgelist(path))

    im.read_file(path)
    im.run()

    print("Modules: ", im.modules)


    # Get communities:
    nodes = set()
    modules = set()
    rd = dict()
    for node_id, module_id in im.modules:
        # print(node_id, module_id)
        nodes.add(node_id)
        modules.add(module_id)
        if module_id in rd.keys():
            rd[module_id].append(node_id)
        else:
            rd[module_id] = [node_id]

    print("MODULES with nodes: ")
    lengths = []
    for el in rd.keys():
        lengths.append(len(rd[el]))
        print(len(rd[el]), rd[el])

    lengths = np.array(lengths)
    print("Number of communities =", len(rd))
    print("Average nodes per community =", lengths.mean())
    print("STD =", lengths.std())


def communities(G):
    import networkx.algorithms.community as nxcom
    communities = sorted(nxcom.greedy_modularity_communities(G), key=len, reverse=True)
    lengths = []

    for el in communities:
        lengths.append(len(list(el)))
        print(len(el), el)

    lengths = np.array(lengths)
    print("Number of communities =", len(communities))
    print("Average nodes per community =", lengths.mean())
    print("STD =", lengths.std())


'''
FACEBOOK:
Number of communities = 13
Average nodes per community = 310.6923076923077
STD = 309.9206808239277

START: 
Number of communities = 89
Average nodes per community = 43.764044943820224
STD = 43.441300307454824

Conn = 0.0, break = 0.48
Number of communities = 13
Average nodes per community = 15.307692307692308
STD = 10.900844112584304
'''

if __name__ == '__main__':
    #infomap_detection()

    #path = r'networks/21_6/start'
    #path = r'networks/7_6/network_pConn_0.0_pBr_0.48'

    path = r'facebook_combined.txt'
    G = nx.Graph(nx.read_edgelist(path))
    communities(G)
