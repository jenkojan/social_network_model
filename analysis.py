from collections import Counter
from math import sqrt
import numpy as np

import matplotlib.pyplot as plt
import networkx as nx


def generate_watts_strogatz(n, m, p=0.01, seed=None):
    """
    Generates a Watts-Strogatz graph with n nodes and approximately m edges.
    """
    k = round(2 * m / n)
    return nx.watts_strogatz_graph(n, k, p, seed)


def generate_barabasi_albert(n, m, seed=None):
    """
    Generates a Barabasi-Albert graph with n nodes and approximately m edges.
    """
    if m > (n ** 2) / 4:
        raise ValueError(
            "Cannot generate Barabasi-Albert graph with m > (n**2)/4 edges."
        )
    # calculate BA model m parameter to get close to m edges
    m_ba = round(1 / 2 * (n - sqrt(n ** 2 - 4 * m)))
    # other solution:
    # m_ba = round(1 / 2 * (sqrt(n**2 - 4 * m) + n))
    return nx.barabasi_albert_graph(n, m_ba, seed)


def analyse_graph(G, verbose=False):
    print(nx.info(G)) if verbose else None

    n_components = nx.number_connected_components(G)
    print("Number of connected components:", n_components) if verbose else None
    if n_components > 1:
        component_sizes = [
            len(c) for c in sorted(nx.connected_components(G), key=len, reverse=True)
        ]
        print("Connected component sizes:", component_sizes) if verbose else None
        lcc_percent = 100 * component_sizes[0]/G.number_of_nodes()
        print(f"LCC: {lcc_percent}%") if verbose else None

    avg_c = nx.average_clustering(G)
    print("Average clustering coefficient:", avg_c) if verbose else None
    degree_assortativity = nx.degree_pearson_correlation_coefficient(G)
    print("Degree assortativity:", degree_assortativity) if verbose else None
    if nx.is_connected(G):
        avg_d = nx.average_shortest_path_length(G)
        print("Average distance:", avg_d) if verbose else None
    else:
        avg_distances = [
            nx.average_shortest_path_length(C)
            for C in (G.subgraph(c).copy() for c in nx.connected_components(G))
        ]
        print("Average distances:", avg_distances) if verbose else None

    avg_connectivity = nx.average_degree_connectivity(G)
    print("Average degree connectivity:", avg_connectivity) if verbose else None

    avg_degree = len(G.edges) * 2 / len(G.nodes)
    return avg_c, avg_d, degree_assortativity, avg_degree


def plot_degree_distribution(G):
    n_nodes = G.number_of_nodes()
    degrees, counts = zip(
        *Counter(degree for node, degree in G.degree(G.nodes)).items()
    )
    probabilities = [c / n_nodes for c in counts]
    plt.figure(figsize=(10, 7))
    plt.xscale("log")
    plt.yscale("log")
    plt.xlabel("k")
    plt.ylabel("$p_k$")
    plt.scatter(degrees, probabilities)


def communities(G):
    import networkx.algorithms.community as nxcom
    assert isinstance(G, nx.Graph)
    communities = sorted(nxcom.greedy_modularity_communities(G), key=len, reverse=True)

    modularity = 0
    m = len(G.edges)

    for community in communities:
        k_c = 0
        m_c = 0
        for node in community:
            k_c += G.degree[node]

        for link in G.edges:
            if link[0] in community and link[1] in community:
                m_c += 1

        modularity += (m_c / m) - (k_c / (2 * m))**2

    return modularity