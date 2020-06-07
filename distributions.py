from scipy.stats import gamma
import numpy as np


def membership_dist_2_latent_distr(lat_distr: list, gen_distr: dict):
    gen = np.array([[gen_distr[0]], [gen_distr[1]], [gen_distr[2]]])
    m = np.array([[lat_distr[0][0], lat_distr[1][0], lat_distr[2][0]],
                  [lat_distr[0][1], lat_distr[1][1], lat_distr[2][1]],
                  [lat_distr[0][2], lat_distr[1][2], lat_distr[2][2]]])

    latent_nodes_dist = list(np.transpose(np.dot(np.linalg.inv(m), gen))[0])

    return {0: latent_nodes_dist[0], 1: latent_nodes_dist[1], 2: latent_nodes_dist[2]}


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


# Modifies distr!
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


gen = {0: 0.3, 1: 0.4, 2: 0.3}

# GB stats, 2015
# https://www.ons.gov.uk/peoplepopulationandcommunity/populationandmigration/populationestimates/bulletins/populationestimatesbymaritalstatusandlivingarrangements/2002to2015#things-you-need-to-know
married = {'married': 0.8, 'unmarried': 0.2}
latent_node_membership = [{0: 0.8, 1: 0.15, 2: 0.05},
                          {0: 0.15, 1: 0.7, 2: 0.15},
                          {0: 0.05, 1: 0.15, 2: 0.8}]

# Derive the latent_nodes distribution
latent_nodes = membership_dist_2_latent_distr(latent_node_membership, gen)

# Change the distributions to cumulative distributions (more useful for the model)
cumulative_distribution(gen)
cumulative_distribution(latent_nodes)
married_transformation(married)

# USA stats, 2019
# https://www.statista.com/statistics/183790/number-of-families-in-the-us-by-number-of-children/
# 0 means no siblings, only child.
siblings = {0: 0.25, 1: 0.25, 2: 0.2, 3: 0.15, 4: 0.1, 5: 0.05}
children = distr_siblings_2_distr_children(siblings, 0.2)

# Change the distributions to cumulative distributions (more useful for the model)
siblings_transformation(siblings)
cumulative_distribution(siblings)
cumulative_distribution(children)

character = gamma(8)

