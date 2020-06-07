import networkx as nx
import random
import numpy as np
from scipy.stats import gamma
import matplotlib.pyplot as plt
from evolution import *


def siblings_transformation(distr_siblings: dict):
    for i in distr_siblings:
        distr_siblings[i] /= (i + 1)

    total = sum(distr_siblings.values())

    for i in distr_siblings:
        distr_siblings[i] /= total


def married_transformation(distr_married):
    distr_married['married'] /= 2

    s = sum(distr_married.values())

    for key in distr_married:
        distr_married[key] /= s


def cumulative_distribution(distr: dict):
    keys = list(distr.keys())
    keys.sort()

    sum = 0
    for key in keys:
        sum += distr[key]
        distr[key] = sum


def distr_siblings_2_distr_children(distr_siblings: dict, p0: float):
    # p0 is the probability that a couple has no children
    x = p0 / (1 - p0)

    distr_children = {0: x}
    for i in distr_siblings:
        distr_children[i + 1] = distr_siblings[i]

    s = sum(distr_children.values())
    for i in distr_children:
        distr_children[i] /= s

    return distr_children


def membership_dist_2_latent_distr(lat_distr: list, gen_distr: dict):
    gen = np.array([[gen_distr[0]], [gen_distr[1]], [gen_distr[2]]])
    m = np.array([[lat_distr[0][0], lat_distr[1][0], lat_distr[2][0]],
                  [lat_distr[0][1], lat_distr[1][1], lat_distr[2][1]],
                  [lat_distr[0][2], lat_distr[1][2], lat_distr[2][2]]])

    latent_nodes_dist = list(np.transpose(np.dot(np.linalg.inv(m), gen))[0])

    return {0: latent_nodes_dist[0], 1: latent_nodes_dist[1], 2: latent_nodes_dist[2]}


# Each distribution called with cumulative_distribution is modified!

# generation 0 is the oldest generation
distr_gen = {0: 0.3, 1: 0.4, 2: 0.3}
distr_married = {'married': 0.8, 'unmarried': 0.2}
latent_node_membership_distr = [{0: 0.8, 1: 0.15, 2: 0.05},
                                {0: 0.15, 1: 0.7, 2: 0.15},
                                {0: 0.05, 1: 0.15, 2: 0.8}]
dist_latent_nodes = membership_dist_2_latent_distr(latent_node_membership_distr, distr_gen)
cumulative_distribution(distr_gen)
cumulative_distribution(dist_latent_nodes)
married_transformation(distr_married)

distr_siblings = {0: 0.25, 1: 0.25, 2: 0.2, 3: 0.15, 4: 0.1, 5: 0.05}
distr_children = distr_siblings_2_distr_children(distr_siblings, 0.2)

siblings_transformation(distr_siblings)
cumulative_distribution(distr_siblings)
cumulative_distribution(distr_children)

character_distribution = gamma(8)


class Network:
    def __init__(self, n, m):
        self.n = n
        # m is the number of people in an average latent node
        self.m = int(n / m)

        self.network = nx.Graph()

        self.latent_nodes = [[], [], []]
        self.generations = [[], [], []]
        self.characters = {}
        self.not_friends = list()

        self._distribute_people_into_generations()
        self._distribute_latent_into_generations()
        self._give_people_character()

        self._connect_siblings(generation=0)
        couples = self._connect_couples(generation=0)
        self._connect_parent_2_child(couples, parent_generation=0)

        self._connect_orphan_siblings(generation=1)
        couples = self._connect_couples(generation=1)
        self._connect_parent_2_child(couples, parent_generation=1)

        self._connect_orphan_siblings(generation=2)

        self._triad_closure()
        #self._triad_closure()

        self._connect_people_2_latent()

    def _distribute_people_into_generations(self):
        for i in range(self.n):
            self.network.add_node(i)

            r = random.random()
            for generation in range(len(distr_gen)):
                if r < distr_gen[generation]:
                    self.generations[generation].append(i)
                    break

    def _connect_siblings(self, generation):
        new = list(self.generations[generation])
        old = list()

        for person in self.generations[generation]:
            if person in old:
                continue

            old.append(person)
            new.remove(person)

            try:
                # Decide how many siblings a person has
                r = random.random()
                for num in range(len(distr_siblings)):
                    if r < distr_siblings[num]:
                        siblings = [person]
                        for _ in range(num):
                            sibling = random.choice(new)
                            old.append(sibling)
                            new.remove(sibling)
                            siblings.append(sibling)

                        for i in range(len(siblings)):
                            for j in range(i + 1, len(siblings)):
                                self.network.add_edge(siblings[i], siblings[j])

                        break

            except IndexError:
                # No more 'unprocessed' people. Not a problem, it means that only one group of siblings is smaller than
                # what the distribution demands
                return

    def _connect_couples(self, generation):
        new = list(self.generations[generation])
        old = list()
        couples = []

        for person in self.generations[generation]:
            if person in old:
                continue

            old.append(person)
            new.remove(person)

            try:
                # Decide whether the person is married
                r = random.random()
                if r < distr_married['married']:
                    partner = random.choice(new)

                    # Try to connect to a non-sibling five times. After that give up. Let there be incest xD
                    for _ in range(5):
                        if partner not in self.network.neighbors(person):
                            break
                        partner = random.choice(new)

                    old.append(partner)
                    new.remove(partner)

                    self.network.add_edge(person, partner)
                    couples.append((person, partner))

            except IndexError:
                # No more 'unprocessed' people. Not a problem, only one person who wanted to get married cannot
                return couples

        return couples

    def _connect_parent_2_child(self, couples, parent_generation):
        new = list(self.generations[parent_generation + 1])
        old = []

        i_coup = 0
        for couple in couples:
            i_coup += 1
            r = random.random()

            number_of_children = 0
            for num in range(len(distr_children)):
                if r < distr_children[num]:
                    number_of_children = num
                    break

            children = []
            for _ in range(number_of_children):
                try:
                    child = random.choice(new)
                except IndexError:
                    # No more unprcessed children. A bit of a problem, since it means potentially multiple couples
                    # who wanted to have children could not.
                    print('{}% of couples in the {} generation did not get the chance to have children. '
                          'Consider changing the relevant distributions.'
                          .format(round(100 * (len(couples) - i_coup) / len(couples), 2), parent_generation))
                    return

                new.remove(child)
                old.append(child)
                children.append(child)

            for parent in couple:
                for child in children:
                    self.network.add_edge(parent, child)

            for i in range(len(children)):
                for j in range(i + 1, len(children)):
                    self.network.add_edge(children[i], children[j])

    def _connect_orphan_siblings(self, generation):
        new = [node for node in self.generations[generation] if self.network.degree[node] == 0]
        old = list()

        print('{}% of the {} generation are orphans. Consider changing the relevant distributions if too high.'
              .format(round(100 * len(new) / len(self.generations[generation]), 2), generation))

        for person in list(new):
            if person in old:
                continue

            old.append(person)
            new.remove(person)

            try:
                # Decide how many siblings a person has
                r = random.random()
                for num in range(len(distr_siblings)):
                    if r < distr_siblings[num]:
                        siblings = [person]
                        for _ in range(num):
                            sibling = random.choice(new)
                            old.append(sibling)
                            new.remove(sibling)
                            siblings.append(sibling)

                        for i in range(len(siblings)):
                            for j in range(i + 1, len(siblings)):
                                self.network.add_edge(siblings[i], siblings[j])

                        break

            except IndexError:
                # No more 'unprocessed' people. Not a problem, only one group of orphan siblings is too small.
                return

    def _triad_closure(self):
        old_network = self.network.copy()

        for person in old_network:
            for neighbor in old_network.neighbors(person):
                self.network.add_edge(person, neighbor)

    def _distribute_latent_into_generations(self):
        for i in range(self.n, self.n + self.m):
            self.network.add_node(i)

            r = random.random()
            for generation in range(len(dist_latent_nodes)):
                if r < dist_latent_nodes[generation]:
                    self.latent_nodes[generation].append(i)
                    break

    def _connect_people_2_latent(self):
        generations = [0, 1, 2]
        new = []

        for generation in self.generations:
            new.append(list(generation))

        while sum([len(g) for g in new]) > 0:
            # First, pick a person
            person_gen = random.choice(generations)
            try:
                person = random.choice(new[person_gen])
            except IndexError:
                continue

            new[person_gen].remove(person)

            # Now, pick 10 latent nodes at random. See where the distribution error would be least after addition and
            # choose that latent node. The distribution error is the sum of abs(true_dist - expected_dist)
            latent_candidates = []
            for _ in range(10):
                gen = random.choice(generations)
                latent_candidates.append((random.choice(self.latent_nodes[gen]), gen))

            latent = self._choose_best_latent(person_gen, latent_candidates)

            self.network.add_edge(person, latent)

    def _choose_best_latent(self, person_gen, latent_candidates):
        errors = []

        for node, gen in latent_candidates:
            expected_distribution = latent_node_membership_distr[gen]

            actual_distribution = {0: 0, 1: 0, 2: 0}
            for person in self.network.neighbors(node):
                for i in range(len(self.generations)):
                    if person in self.generations[i]:
                        actual_distribution[i] += 1

            actual_distribution[person_gen] += 1

            s = sum(actual_distribution.values())

            error = 0
            for key in actual_distribution:
                actual_distribution[key] /= s

                error += abs(actual_distribution[key] - expected_distribution[key])

            # Penalty for large groups
            error += 2 * s / self.n

            errors.append(error)

        min_error = min(errors)

        for i in range(len(errors)):
            if errors[i] == min_error:
                return latent_candidates[i][0]

    def _give_people_character(self):
        for person in self.network:
            self.characters[person] = character_distribution.rvs(size=1)[0]

    def degree_sequence(self):
        degrees = {}

        for node, degree in self.network.degree:
            if degree not in degrees:
                degrees[degree] = 0

            degrees[degree] += 1

        return degrees


def test_plot(n):
    import copy
    G = copy.copy(n.network)
    isolates = list(nx.isolates(G))
    # print(isolates)
    G.remove_nodes_from(isolates)
    # print(G)
    nx.draw(G)
    plt.show()


if __name__ == '__main__':
    population = 1000
    n = Network(population, 30)

    '''

    s = 0
    nds = 0
    for gen in n.latent_nodes:
        for node in gen:
            print(n.network.degree[node])
            s += n.network.degree[node]
            nds += 1

    print(s, nds)

    pk = n.degree_sequence()

    for i in range(100):
        try:
            print('{}: {}'.format(i, round(100 * pk[i] / population, 2)))
        except KeyError:
            pass
    '''

    plot = False
    if plot:
        test_plot(n)
    evolve(n)

