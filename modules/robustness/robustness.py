#!/usr/bin/python
# Author: Hernán David Carvajal <carvajal.hernandavid at gmail.com>
# Tested in python-3.4.3


import operator
import random as rnd
import networkit as nk
import networkx as nx
import pylab
import numpy as np
import time

centrality = {
    "degree": nk.centrality.DegreeCentrality,
    "closeness": nk.centrality.Closeness,
    "betweenness": nk.centrality.Betweenness,
    "eigenvector": nk.centrality.EigenvectorCentrality,
    "random": None
}


def average_path_length():
    None


def average_shortest_path_lengthNK(g):
    """
    TODO - Specify that this method also works with disconnected networks

    """
    n = g.numberOfNodes()
    avg = 0.0

    for node in g.nodes():
        bfs = nk.graph.BFS(g, node).run()
        avg = sum(filter(lambda a: a != sys.float_info.max, bfs.getDistances()))

    return avg / (n*(n-1))


def largest_component_size(g):
    return len(sorted(nx.connected_components(g), key=len, reverse=True)[0])


def largest_component_sizeNK(g):
    components_size = nk.properties.components(nk.nx2nk(G))[1]
    return sorted(components_size.items(), key=operator.itemgetter(1), reverse=True)[0][1]

comparative_measures = {
    "component_size": largest_component_size # ,
    # "path_length": average_path_length
}


def calculateNK(g, strategy="degree", measure="component_size", sequential=True):
    """
    This method calculates the robustness index of the network by removing the
    nodes from the network and comparing the size of the largest component in
    the network to the number of nodes removed.

    Params
    ---------
    g:          networkx graph
    sequential: when false the ranking is updated each time a node is removed.
    strategy:   The strategy used to remove the nodes

    Return
    ----------
    vertices_removed: A list with the fraction of vertices removed
    comparative_measure_values:   A list with the comparative measure values
                          (i.e. component size or avg path length) given a
                          fraction of the network removed
    robustness_index: The robustness index value
    """
    vertices_removed = []
    comparative_measure_values = []
    n = len(g.nodes())
    r = 0.0
    rank = ranking(g, strategy)
    vertices_removed.append(0)
    comparative_measure_values.append(comparative_measures[measure](g)/n)

    for i in range(1, n):
        g.remove_node(rank.pop(0))
        comparative_value = comparative_measures[measure](g)
        r +=  comparative_value / n

        # print("vr: {}, cs: {}".format(i/n, largest_component_size(g)/n))
        vertices_removed.append(i / n)
        comparative_measure_values.append(comparative_value / n)

        if not sequential:
            rank = ranking(g, strategy)

    return vertices_removed, comparative_measure_values, (r / n)


def calculate(g, strategy="degree", measure="component_size", sequential=True):
    """
    This method calculates the robustness index of the network by removing the
    nodes from the network and comparing the size of the largest component in
    the network to the number of nodes removed.

    Params
    ---------
    g:          networkx graph
    sequential: when false the ranking is updated each time a node is removed.
    strategy:   The strategy used to remove the nodes

    Return
    ----------
    vertices_removed: A list with the fraction of vertices removed
    comparative_measure_values:   A list with the comparative measure values
                          (i.e. component size or avg path length) given a
                          fraction of the network removed
    robustness_index: The robustness index value
    """
    # Use networkx graph instead of networkit
    if type(g) is nk.Graph:
        g = nk.nk2nx(g)

    vertices_removed = []
    comparative_measure_values = []
    n = len(g.nodes())
    r = 0.0
    rank = ranking(g, strategy)
    vertices_removed.append(0)
    comparative_measure_values.append(comparative_measures[measure](g)/n)

    for i in range(1, n):
        print("----------------------------------------------")
        print(g.nodes())
        print(rank)
        print("Sequential: ", sequential)
        print("Measure: ", measure)
        print("----------------------------------------------")
        g.remove_node(rank.pop(0))
        comparative_value = comparative_measures[measure](g)
        r +=  comparative_value / n

        # print("vr: {}, cs: {}".format(i/n, largest_component_size(g)/n))
        vertices_removed.append(i / n)
        comparative_measure_values.append(comparative_value / n)

        if not sequential:
            rank = ranking(g, strategy)

    return vertices_removed, comparative_measure_values, (r / n)


def ranking(gx, measure="degree", reverse=False):
    """
    This method ranks the nodes of the graph from largest to smallest according
    to a given centrality measure

    Parameters
    -----------
    gx: A networkx graph
    measure: the centrality measure used to rank the nodes, the possible values
        are those present in the 'centrality' dictionary. Degree is the default
    reverse: if is set to true, the rank is ordered from smallest to largest.
             The default value is False

    Returns
    -----------
    A list of nodes ranked according to the centrality measure
    """
    # The networkx graph is converted to a networkit graph because that library
    # is more efficient calculating the centrality measures
    g = nk.nx2nk(gx)

    if measure is "random":
        nodes = g.nodes()
        rnd.shuffle(nodes)
        return nodes

    centrality_measure = centrality[measure](g).run()
    results = centrality_measure.ranking()
    results.sort(key=operator.itemgetter(1), reverse=not reverse)

    return [x[0] for x in results]


def plot_robustness_analysis(g, debug=True):
    """
    Compute the robustness analisys on a network and plot the results

    Params
    ---------
    g: Networkit graph
    """

    for name, comparative_measure in comparative_measures.items():
        for sequential_analysis in [False, True]:
            current_time = time.strftime("%d-%m-%Y_%H%M%S")
            file_name = g.getName() + "_robustness_" + name + "_"
            file_name += "simultaneous" if sequential_analysis else "sequential"
            file_name += "_" + current_time
            print(file_name)
            if debug:
                file_results = open(file_name + ".results", 'a')

            pylab.figure(1, dpi=500)
            pylab.xlabel(r"Fraction of vertices removed ($\rho$)")
            pylab.ylabel(r"Fractional size of largest component ($\sigma$)")

            # Color generator
            color = iter(pylab.cm.rainbow(np.linspace(0, 1, len(centrality.keys()))))

            for strategy in centrality.keys():
                vertices_removed, component_size, r_index = calculate(g, strategy, name, sequential_analysis)
                label = "%s ($R = %4.3f$)" % (strategy, r_index)
                pylab.plot(vertices_removed, component_size, label=label, c=next(color), alpha=0.6, linewidth=2.0)

                if debug:
                    print("{} {}".format(strategy, r_index), file=file_results)

            pylab.legend(loc="upper right", shadow=False)
            pylab.savefig(file_name + ".pdf", format="pdf")
            pylab.close(1)

    if debug:
        file_results.close()

if __name__ == "__main__":
    # graph = nx.read_graph6("football.graph6")
    # graph = nx.erdos_renyi_graph(100, 1)


    erg = nk.generators.ErdosRenyiGenerator(10, 0.3, False)
    graph = erg.generate()

    plot_robustness_analysis(graph)
