import sys
import argparse

from data import get_data, get_csv_data
from graph import NetworkGraph

from random import shuffle


class AvailableFrequenciesExhausted(Exception):
    def __init__(self, edge):
        self.edge = edge


parser = argparse.ArgumentParser()
parser.add_argument(
    "--plot",
    "-p",
    action="store_true",
    help="Use graphviz and matplotlib to display a graphical chart",
)
parser.add_argument(
    "--verbose",
    "-v",
    action="store_true",
    help="Print debugging info and decision making",
)
parser.add_argument("--node_file", help="nodes.csv file to use")
parser.add_argument("--edge_file", help="edges.csv file to use")
parser.add_argument("--frequency_file", help="frequencies.csv file to use")
parser.add_argument("--out_file", "-o", help=".fig file to save")
parser.add_argument('--json_file', help="json file for d3 export")
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


def log_debug(msg):
    if args.verbose:
        print(msg, file=sys.stderr)


def assign_frequency_to_edge(edge, available_frequency_pairs):
    # We've already assigned a frequency to this edge
    if G.get_frequency(edge):
        return

    # Oops, run out of frequencies.
    if not available_frequency_pairs:
        raise AvailableFrequenciesExhausted(edge)

    frequency, colour = available_frequency_pairs.pop()
    G.set_frequency_and_colour(edge, frequency, colour)


def get_unavailable_frequencies_for_node(node):
    unavailable_frequency_pairs = []
    for edge in G.edges(node):
        frequency_and_colour = G.get_frequency_and_colour(edge)
        if frequency_and_colour:
            unavailable_frequency_pairs.append(frequency_and_colour)
    return unavailable_frequency_pairs


# What frequencies are not used by any neighbours of this node
def get_available_frequency_pairs_for_node(node):
    unavailable_frequency_pairs = []
    for neighbour in G.neighbors(node):
        unavailable_frequency_pairs += get_unavailable_frequencies_for_node(neighbour)

    available_frequency_pairs = [
        f for f in frequency_pairs if f not in unavailable_frequency_pairs
    ]
    return available_frequency_pairs


# What frequencies are not used by either node connected to this edge
def get_available_frequency_pairs_for_edge(edge):
    node1, node2 = edge
    unavailable_frequency_pairs = get_unavailable_frequencies_for_node(
        node1
    ) + get_unavailable_frequencies_for_node(node2)

    available_frequency_pairs = [
        f for f in frequency_pairs if f not in unavailable_frequency_pairs
    ]
    return available_frequency_pairs


def assign_frequencies():
    unassigned_edges = []

    for node, data in G.get_nodes_by_priority():
        edges = [i for i in G.edges(node)]

        available_frequency_pairs = get_available_frequency_pairs_for_node(node)

        shuffle(available_frequency_pairs)

        for edge in edges:
            try:
                assign_frequency_to_edge(edge, available_frequency_pairs)
            except AvailableFrequenciesExhausted as failed:
                unassigned_edges.append(failed.edge)

    for edge in unassigned_edges:
        # May have been assigned the other direction
        if G.get_frequency_and_colour(edge):
            continue

        # Try assigning any that aren't used by the connected nodes
        try:
            available_frequency_pairs = get_available_frequency_pairs_for_edge(edge)
            assign_frequency_to_edge(edge, available_frequency_pairs)
            continue
        except AvailableFrequenciesExhausted:
            pass

        #  Get the next best frequency - that with lowest weight
        node1, node2 = edge
        other_connected_edges = [
            i for i in list(G.edges(node1)) + list(G.edges(node2)) if i != edge
        ]
        other_connected_edges = G.order_edges_by_weight(other_connected_edges)

        log_debug(
            f"Deciding for connection between {G.get_node_name(node1)} and {G.get_node_name(node2)}"
        )
        log_debug(f"Available:")
        for other_edge in other_connected_edges:
            u, v = other_edge
            name1 = G.nodes[u]["name"]
            name2 = G.nodes[v]["name"]
            weight = G.edges[other_edge]["weight"]
            log_debug(f"{name1} to {name2} = {weight}")

        # Get lowest signal frequency already used
        for other_edge in other_connected_edges:
            if G.edges_equal(edge, other_edge):
                continue
            G.edges[other_edge]["weight"]
            frequency_and_colour = G.get_frequency_and_colour(other_edge)
            if frequency_and_colour:
                G.set_frequency_and_colour(edge, *frequency_and_colour)
                log_debug(f"Chose {G.edges[other_edge]['weight']}")
                break


assign_frequencies()

# Debugging
# edge_str = "\n".join([f"{u} {v} {d}" for u, v, d in G.edges(data=True)])
# node_str = "\n".join([f"{n} {d}" for n, d in G.nodes(data=True)])
# print(f"Edges: \n{edge_str}")
# print(f"Nodes: \n{node_str}")

G.print()

if args.plot:
    G.show()

if args.out_file:
    G.save(args.out_file)

if args.json_file:
    G.json(args.json_file)