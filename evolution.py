EVOLUTION_STEPS = 15
P_BREAK = 0.5
P_CONNECT = 0.0001
TRACE = False

import random
from social_network import test_plot
import time
import itertools
import networkx as nx


def evolve(n):
    st = time.time()

    for i in range(EVOLUTION_STEPS):
        print("Starting step:", i) if TRACE else None
        evolution_part_1(n)
        evolution_part_2(n)
        evolution_part_3(n)

        if TRACE:
            print("step " + str(i) + " took " + str(time.time() - st) + " seconds. ")

    end_evolution(n)
    # test_plot(n)
    # analyze_net(n.network)

    # nx.write_edgelist(n.network, 'network_22_5')
    # nx.write_pajek(n.network, 'network_22_5.net')


def evolution_part_1(n):
    print("EVOLUTION_PART_1") if TRACE else None
    '''
     First, each  person  connects  to  some  new  latent  node  with probability pi=Ei/I.  If  a  person  connects  to
      a  new latent node, it remains connected to all the other latent nodes it is connected to.

    '''
    latent_nodes = [item for sublist in n.latent_nodes for item in sublist]
    generations = [0, 1, 2]
    s = 0

    for node in list(n.network.nodes):

        if node in latent_nodes:
            continue

        gen_person = [(index, row.index(node)) for index, row in enumerate(n.generations) if node in row][0][0]
        r = random.random()

        # TODO: Chance ni sorazmeren z evolution steps-i
        if r < n.characters[node] / (EVOLUTION_STEPS):

            s += 1
            latent_candidates = list()
            for _ in range(10):
                gen = random.choice(generations)
                latent_candidates.append((random.choice(n.latent_nodes[gen]), gen))

            best_latent = n._choose_best_latent(gen_person, latent_candidates)
            n.network.add_edge(node, best_latent)

    print('new latent {}'.format(s)) if TRACE else None


def evolution_part_2(n):
    print("EVOLUTION_PART_2") if TRACE else None
    '''
     Each person who is connected to more than one latent node struggles to keep in touch with the people  they  know
     through  other  latent  nodes. So people with multiple latent neighbors break a connection to each person whom
     they are connected to through one of the latent nodes with some probability p_break, universal to all people.
    '''
    s = 0
    latent_nodes = [item for sublist in n.latent_nodes for item in sublist]
    for node in list(n.network.nodes):
        if node in latent_nodes:
            continue

        neighbors = list(n.network.neighbors(node))
        latent_neighbours = list(set(neighbors).intersection(set(list(latent_nodes))))

        if len(latent_neighbours) > 1:
            # TODO: this could be dynamic based on number of latent_neighbours
            r = random.random()
            for latent_node in latent_neighbours:
                for neighbor in n.network.neighbors(latent_node):
                    if r < P_BREAK:
                        s += 1
                        n.not_friends.add((node, neighbor))

    print('broken {}'.format(s)) if TRACE else None


def evolution_part_3(n):
    print("EVOLUTION_PART_3") if TRACE else None
    '''
    The third part of each iteration is connecting mutual friends. Each person goes through all pairs of its
    unconnected neighbors and connects them with probability p_connect, again universal to all people.
    '''
    latent_nodes = [item for sublist in n.latent_nodes for item in sublist]
    s = 0
    for node in list(n.network.nodes):

        if node in latent_nodes:
            continue

        neighbors = set(n.network.neighbors(node))
        latent_neighbours = list(set(neighbors).intersection(set(list(latent_nodes))))

        for latent in latent_neighbours:
            neighbors.remove(latent)

            for neighbor in n.network.neighbors(latent):
                if neighbor == node:
                    continue
                neighbors.add(neighbor)

        # neighbors is now a set of all human neighbors (either actual or connected through a latent node)
        neighbors = list(neighbors)

        possible_connections = len(neighbors) * (len(neighbors) - 1) / 2
        actual_connections = int(P_CONNECT * possible_connections)
        s += actual_connections

        for i in range(actual_connections):
            n1 = random.choice(neighbors)
            n2 = random.choice(neighbors)

            if n1 != n2:
                n.network.add_edge(n1, n2)

        '''
        r = random.random()
        r1 = random.random()
        for latent_node in latent_neighbours:
            latents_neighbours = n.network.neighbors(latent_node)
            for neighbor in latents_neighbours:
                #TODO: še dodaten probability če se poveže z njegovimi prijatelji namesto da se z vsakim?
                neighbors_neighbors = list(n.network.neighbors(neighbor))
                if r1 > P_MAKE_FRIEND:
                    continue
                for neighbors_neighbor in neighbors_neighbors:
                    if r < P_CONNECT and neighbors_neighbor not in latent_nodes:
                        n.network.add_edge(node, neighbors_neighbor)

        '''
    print('Connected {}'.format(s)) if TRACE else None


def end_evolution(n):
    latent_nodes = [item for sublist in n.latent_nodes for item in sublist]
    for latent_node in latent_nodes:
        neighbors = list(n.network.neighbors(latent_node))
        combinations = list(itertools.combinations(neighbors, 2))
        for combination in combinations:
            if combination[0] not in latent_nodes and \
                    combination[1] not in latent_nodes and \
                    (combination[0], combination[1]) not in n.not_friends and \
                    (combination[1], combination[0]) not in n.not_friends:
                n.network.add_edge(combination[0], combination[1])

        n.network.remove_node(latent_node)


def analyze_net(G):
    print("Analysis:")
    avg_k = nx.average_degree_connectivity(G)
    print("Average degree:", avg_k)
    avg_c = nx.average_clustering(G)
    print("Average clustering coefficient:", avg_c)
    avg_d = nx.average_shortest_path_length(G)
    print("Average distance:", avg_d)


if __name__ == '__main__':
    print("EVOLUTION")
