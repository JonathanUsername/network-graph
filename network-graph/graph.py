import matplotlib.pyplot as plt
import networkx as nx

from networkx import Graph
from operator import attrgetter, itemgetter

LINE_WEIGHT_MULTIPLIER = 5


class NetworkGraph(Graph):
    def print(self):
        labels = nx.get_node_attributes(self, "name")
        edge_labels = nx.get_edge_attributes(self, "frequency")
        pos = nx.spring_layout(self)
        edges, colours, weights = self.colour_edges(None)  # todo, colourmap
        nx.draw(
            self, pos, edges=edges, edge_color=colours, width=weights, with_labels=False
        )
        nx.draw_networkx_labels(self, pos, labels)
        nx.draw_networkx_edge_labels(self, pos, edge_labels)
        plt.show()

    def colour_edges(self, colourmap):
        edge_data = self.edges(data=True)
        edges = []
        colours = []
        weights = []
        for u, v, d in edge_data:
            edges.append((u, v))
            colours.append(d.get("colour", "red"))
            weight = float(d.get("weight", 0)) * LINE_WEIGHT_MULTIPLIER
            weights.append(weight)

        print(weights)

        return edges, colours, weights

    def compute_priority(self):
        # set priority - connectedness
        connections = {n: len(self.edges(n)) for n in self.nodes()}
        nx.set_node_attributes(self, connections, "connections")

    def get_nodes_by_priority(self):
        self.compute_priority()
        nodes = self.nodes(data=True)
        return sorted(nodes, key=lambda n: n[1]["connections"], reverse=True)

    def set_frequency_and_colour(self, edge, frequency, colour):
        frequencies = {edge: frequency}
        colours = {edge: colour}
        nx.set_edge_attributes(self, colours, "colour")
        nx.set_edge_attributes(self, frequencies, "frequency")

    def get_frequency_and_colour(self, edge):
        e = self.edges[edge]
        f = e.get("frequency")
        c = e.get("colour")
        if f and c:
            # Must be a list, as that's the same as the pairs
            return [f, c]

    def get_frequency(self, edge):
        e = self.edges[edge]
        return e.get("frequency")

    def get_node_name(self, node):
        n = self.nodes[node]
        return n.get("name")

    def order_edges_by_weight(self, edges):
        ordered = sorted(self.edges(edges, data=True), key=lambda n: n[1]["weight"])
        return [i for i, _ in ordered]
