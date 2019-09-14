import osmnx as ox
import networkx as nx
import copy
from random import sample
n_drivers = 200
equilibrium_steps = 20
c_traffic = 0.1
G = ox.graph_from_place('Baltimore, Maryland, USA', network_type='drive')
starts = sample(G.nodes(), n_drivers)
cached = {}
ends = sample(G.nodes(), n_drivers)
def edge_str(a, b):
    return str(a) + "," + str(b)

def original_length(node_a, node_b):
    cur_edge = edge_str(node_a, node_b)
    if cur_edge not in cached:
        cached[cur_edge] = G[node_a][node_b][0]['length']
    return cached[cur_edge]

edges_used = {}
driver_path = [[] for _ in range(n_drivers)]
G_new = copy.deepcopy(G)
for step in range(equilibrium_steps):
    total_cost = 0
    for driver_id, (start, end) in enumerate(zip(starts, ends)):
        try:
            path = nx.shortest_path(G_new, start, end, 'length')
            total_cost += nx.shortest_path_length(G_new, start, end, 'length')
        except Exception as e:
            path = []
        for node_a, node_b in zip(path[:-1], path[1:]):
            cur_edge = edge_str(node_a, node_b)
            if cur_edge in edges_used:
                edges_used[cur_edge] += 1
            else:
                edges_used[cur_edge] = 1
        if len(driver_path[driver_id]) > 0:
            for node_a, node_b in zip(driver_path[driver_id][:-1], driver_path[driver_id][1:]):
                cur_edge = edge_str(node_a, node_b)
                edges_used[cur_edge] -= 1
        driver_path[driver_id] = path
        for cur_edge in edges_used.keys():
            node_a, node_b = (int(node) for node in cur_edge.split(","))
            lanes = 1
            if 'lanes' in G[node_a][node_b][0]:
                lanes = int(G[node_a][node_b][0]['lanes'][0])
            G_new[node_a][node_b][0]['length'] =  original_length(node_a, node_b) * (1 + edges_used[cur_edge] * c_traffic / lanes)
    print(step, total_cost)
