import osmnx as ox
import networkx as nx
import copy
from random import sample
n_drivers = 100
equilibrium_steps = 10
c_traffic = 0.1
G = ox.graph_from_place('Baltimore, Maryland, USA', network_type='drive')
starts = sample(G.nodes(), n_drivers)
ends = sample(G.nodes(), n_drivers)
def edge_str(a, b):
    return str(a) + "," + str(b)

for step in range(equilibrium_steps):
    total_cost = 0
    edges_used = {}
    for start, end in zip(starts, ends):
        try:
            path = nx.shortest_path(G_new, start, end, 'length')
            total_cost += nx.shortest_path_length(G_new, start, end, 'length')
            for node_a, node_b in zip(path[:-1], path[1:]):
                cur_edge = edge_str(node_a, node_b)
                if cur_edge in edges_used:
                    edges_used[cur_edge] += 1
                else:
                    edges_used[cur_edge] = 1
        except Exception as e:
            print("Exception", e)
    print(step, total_cost)
    G_new = copy.deepcopy(G)
    for cur_edge in edges_used.keys():
        node_a, node_b = cur_edge.split(",")
        node_a, node_b = int(node_a), int(node_b)
        lanes = 1
        if 'lanes' in G[node_a][node_b][0]:
            lanes = int(G[node_a][node_b][0]['lanes'][0])
        G_new[node_a][node_b][0]['length'] *= (1 + edges_used[cur_edge] * c_traffic / lanes)
