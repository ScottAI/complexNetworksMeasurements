#!/usr/bin/python
# Author: Hernán David Carvajal <carvajal.hernandavid at gmail.com>
# Tested in python-3.4.3

import networkit as nk
import numpy as np
import random as rnd


def choose_color(not_valid_colors, valid_colors):
    """
    This method returns a value selected randomly from the values present in the
    set valid_colors which are not present in the list not_valid_colors.

    If there is no valid colors from the list, then it is returned the maximum
    value of both lists + 1


    Parameters
    -----------
    not_valid_colors: A list of not selectable numbers
    valid_colors: A list of selectable numbers
    """

    possible_values = list(valid_colors - not_valid_colors)

    if possible_values:
        return rnd.choice(possible_values)
    else:
        return max(valid_colors.union(not_valid_colors)) + 1


def greedy_coloring(g):
    """
    Compute the minimal set of boxes to cover a graph given a box length.
    This method uses the box values between [2, network_diameter]

    Parameters
    -------------------
    distances:  Matrix containing all the shortest path lengths between all
                nodes in a graph.
    num_nodes:  Number of nodes in the graph
    diameter:   Diameter of the graph

    References:
    Chaoming Song, Lazaros K Gallos, Shlomo Havlin, and Hernán A Makse.
    How to calculate the fractal dimension of a complex network: the box cov-
    ering algorithm. Journal of Statistical Mechanics: Theory and Experiment,
    2007(03):P03006, 2007.
    http://iopscience.iop.org/1742-5468/2007/03/P03006/
    """
    num_nodes = g.numberOfNodes()
    diameter = int(nk.distance.Diameter.exactDiameter(g))

    c = np.empty((num_nodes+1, diameter+2), dtype=int)
    c.fill(-1)
    # Matrix C will not use the 0 column and 0 row to
    # let the algorithm look very similar to the paper
    # pseudo-code

    nodes = list(range(num_nodes))
    rnd.shuffle(nodes)

    c[nodes[0], :] = 0

    index = 1

    # Algorithm
    for i in nodes[1:-1]:
        # Calculate distances from i to all the other nodes
        bfs = nk.graph.BFS(g, g.nodes().index(i)).run()
        for lb in range(2, diameter+1):
            not_valid_colors = set()
            valid_colors = set()

            for j in nodes[:index]:
                if bfs.distance(j) >= lb:
                    not_valid_colors.add(c[j, lb])
                else:
                    valid_colors.add(c[j, lb])

                c[i, lb] = choose_color(not_valid_colors, valid_colors)
        index += 1

    return c


def box_covering(g, distances=None, num_nodes=None, diameter=None):
    """
    This method computes the boxes required to cover a graph with all the
    possible box sizes.
    If the optional parameters are not passed they are calculated.

    This method returns a list of dictionaries with
    { box_id: subgraph generated by the nodes in this box}


    Parameters
    -------------------
    G:          Networkit graph
    distances:  Matrix containing all the shortest path lengths between all
                nodes in ``G``
    num_nodes:  Number of nodes in the graph
    diameter:   Diameter of the graph

    """

    c = greedy_coloring(g)

    # Creation of boxes by color
    boxes = []
    for LB in range(1, diameter+2):
        box = {}  # each box is a dictionary (color: [nodes])
        for j in range(1, num_nodes+1):
            if LB is 1:
                # Each node is in a different box
                box[j] = box.get(j, [])
                box[j].append(j)
            elif LB == diameter + 1:
                # Every node is in the same box
                box[1] = box.get(1, [])
                box[1].append(j)
            else:
                color = c[j, LB]
                box[color] = box.get(color, [])
                box[color].append(j)

        boxes.append(box)

    return boxes


def number_of_boxes(g):
    """
    This method computes the boxes required to cover a graph with all the
    possible box sizes.
    If the optional parameters are not passed they are calculated.

    Parameters
    -------------------
    G:          Networkit graph

    Returns
    ------------------
    This method returns a dictionary specifying the number of boxes found for
    every box length:   { box_length: number_of_boxes}

    """
    diameter = int(nk.distance.Diameter.exactDiameter(g))
    num_nodes = g.numberOfNodes()
    c = greedy_coloring(g)

    boxes = []
    for lb in range(1, diameter+2):
        if lb is 1:
            # Each node is in a different box
            boxes.append(num_nodes)
        elif lb == diameter + 1:
            # Every node is in the same box
            boxes.append(1)
        else:
            boxes.append(len(np.unique(c[:, lb])) - 1)

    return boxes


def test(G):
    """
    _boxes = box_covering(G)
    for _box in _boxes:
        print(_box)
    """

    if G.isDirected():
        G = G.toUndirected()

    # number_of_boxes(G)
    print(number_of_boxes(G))


if __name__ == "__main__":
    import networkx as nx
    gk = nk.nxadapter.nx2nk(nx.er)
    test(gk)
