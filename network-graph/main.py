from data import get_data
from graph import NetworkGraph

from random import shuffle


class FrequenciesExhaustedError(Exception):
    pass


nodes = get_data("nodes.csv")
edges = get_data("edges.csv")
frequencies = get_data("frequencies.csv")

G = NetworkGraph()

for _id, _name in nodes:
    G.add_node(_id, name=_name)

for _from, _to, _weight in edges:
    G.add_edge(_from, _to, weight=_weight)

# Assign the frequencies
for node, data in G.get_nodes_by_priority():
    edges = [i for i in G.edges(node)]

    unavailable_frequencies = []
    for neighbour in G.neighbors(node):
        for edge in G.edges(neighbour):
            frequency = G.get_frequency_and_colour(edge)
            if frequency:
                unavailable_frequencies.append(frequency)

    available_frequencies = [f for f in frequencies if f not in unavailable_frequencies]

    shuffle(available_frequencies)

    while len(edges):
        edge = edges.pop()

        # We've already assigned a frequency to this edge
        if G.get_frequency(edge):
            continue

        # Oops, run out of frequencies. NB: This might happen because this algorithm is naive, could re-run optimistically here?
        if not available_frequencies:
            connected_node = next((i for i in edge if i != node))
            connected_node_name = G.get_node_name(connected_node)
            raise FrequenciesExhaustedError(
                f"Ran out of available frequencies on node: {data.get('name')}, specifically connecting it to {connected_node_name}"
            )

        frequency = available_frequencies.pop()

        G.set_frequency(edge, frequency)

# Debugging
edge_str = "\n".join([f"{u} {v} {d}" for u, v, d in G.edges(data=True)])
node_str = "\n".join([f"{n} {d}" for n, d in G.nodes(data=True)])
print(f"Edges: \n{edge_str}")
print(f"Nodes: \n{node_str}")

G.print()
