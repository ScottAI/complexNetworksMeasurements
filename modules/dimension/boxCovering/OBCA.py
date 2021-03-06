#!/usr/bin/python
# Author: Hernán David Carvajal <carvajal.hernandavid at gmail.com>
# Tested in python-3.4.3

import networkx as nx
import operator
import sys


def obca(g):
    diameter = nx.diameter(g)
    lb_max = diameter + 1

    # Rank the nodes according to their degree
    results = nx.degree_centrality(g)
    nodes = next(zip(*sorted(results.items(), key=operator.itemgetter(1))))
    results = dict()

    results[1] = [[node] for node in g.nodes()]
    for lb in range(2, lb_max):
        covered_frequency = [0] * len(g.nodes())
        boxes = list()

        for i in range(0, len(nodes)):
            node = nodes[i]

            if covered_frequency[i] > 0:
                continue

            box = list(nx.single_source_shortest_path_length(g, node, lb-1).keys())

            # Verify that all paths within the box have the length less then lb
            index = 0
            while True:
                node = box[index]
                j = index+1

                while j < len(box):
                    neighbor = box[j]

                    if nx.shortest_path_length(g, node, neighbor) >= lb:
                        box.remove(neighbor)

                    j += 1

                index += 1
                if index >= len(box):
                    break

            for node in box:
                node_index = nodes.index(node)
                covered_frequency[node_index] += 1

            boxes.append(box)

        for box in boxes:
            redundant_box = True

            for node in box:
                node_index = nodes.index(node)
                if covered_frequency[node_index] == 1:
                    redundant_box = False
                    break

            if redundant_box:
                for node in box:
                    node_index = nodes.index(node)
                    covered_frequency[node_index] -= 1
                boxes.remove(box)

        # print("lb: {}, boxes: {}, cf: {}".format(lb, boxes, covered_frequency))
        results[lb] = boxes

    temp = list()
    temp.append(g.nodes())
    results[lb_max] = temp

    # print(results)
    return results


def number_of_boxes_dict(g):
    results = obca(g)
    nboxes = dict()

    for box_size, boxes in results.items():
        nboxes[box_size] = len(boxes)

    return nboxes


def number_of_boxes(g):
    results = obca(g)
    nboxes = list()

    for box_size, boxes in results.items():
        nboxes.append(len(boxes))

    return nboxes


def test():
    g = nx.Graph()
    g.add_edge(1, 2)
    g.add_edge(1, 4)
    g.add_edge(2, 4)
    g.add_edge(3, 4)
    g.add_edge(5, 3)
    g.add_edge(5, 6)

    obca(g)


if __name__ == "__main__":
    infile = sys.argv[1]
    network = nx.read_gml(infile)

    print(number_of_boxes(network))
