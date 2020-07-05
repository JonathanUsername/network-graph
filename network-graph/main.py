import sys
import argparse

from data import get_data, get_csv_data
from graph import NetworkGraph

from random import shuffle


parser = argparse.ArgumentParser()
parser.add_argument(
    "--plot", "-p", action='store_true', help="Use graphviz and matplotlib to display a graphical chart"
)
parser.add_argument("--node_file", help="nodes.csv file to use")
parser.add_argument("--edge_file", help="edges.csv file to use")
parser.add_argument("--frequency_file", help="frequencies.csv file to use")
args = parser.parse_args()

if args.node_file:
    nodes = get_csv_data(args.node_file)
else:
    nodes = get_data("nodes.csv")

if args.edge_file:
    edges = get_csv_data(args.edge_file)
else:
    edges = get_data("edges.csv")

if args.frequency_file:
    frequency_pairs = get_csv_data(args.frequency_file)
else:
    frequency_pairs = get_data("frequencies.csv")

G = NetworkGraph()

for _id, _name in nodes:
    G.add_node(_id, name=_name)

for _from, _to, _weight in edges:
    G.add_edge(_from, _to, weight=_weight)


def assign_frequencies():
    unassigned_edges = []

    for node, data in G.get_nodes_by_priority():
        edges = [i for i in G.edges(node)]

        unavailable_frequency_pairs = []
        for neighbour in G.neighbors(node):
            for edge in G.edges(neighbour):
                frequency = G.get_frequency_and_colour(edge)
                if frequency:
                    unavailable_frequency_pairs.append(frequency)

        available_frequency_pairs = [
            f for f in frequency_pairs if f not in unavailable_frequency_pairs
        ]

        shuffle(available_frequency_pairs)

        while edges:
            edge = edges.pop()

            # We've already assigned a frequency to this edge
            if G.get_frequency(edge):
                continue

            # Oops, run out of frequencies.
            if not available_frequency_pairs:
                connected_node = next((i for i in edge if i != node))
                connected_node_name = G.get_node_name(connected_node)
                print(
                    f"Ran out of available frequencies on node: {data.get('name')}, specifically connecting it to {connected_node_name}.\nWill assign next-best frequency.",
                    file=sys.stderr,
                )
                unassigned_edges.append(edge)
                continue

            frequency, colour = available_frequency_pairs.pop()

            G.set_frequency_and_colour(edge, frequency, colour)

    for edge in unassigned_edges:
        node1, node2 = edge
        other_connected_edges = [
            i for i in list(G.edges(node1)) + list(G.edges(node2)) if i != edge
        ]
        other_connected_edges = G.order_edges_by_weight(other_connected_edges)
        # Get lowest signal frequency already used
        while other_connected_edges:
            other_edge = other_connected_edges.pop()
            frequency, colour = G.get_frequency_and_colour(other_edge)
            if frequency:
                G.set_frequency_and_colour(edge, frequency, colour)


assign_frequencies()

# Debugging
# edge_str = "\n".join([f"{u} {v} {d}" for u, v, d in G.edges(data=True)])
# node_str = "\n".join([f"{n} {d}" for n, d in G.nodes(data=True)])
# print(f"Edges: \n{edge_str}")
# print(f"Nodes: \n{node_str}")

G.print()

if args.plot:
    G.plot()
