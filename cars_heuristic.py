import osmnx as ox
import networkx as nx
import copy
import os
import pickle
import igraph as ig
from random import sample
import matplotlib.cm as cm
import matplotlib.colors as colors
from tqdm import tqdm
import numpy as np
import math

n_drivers = 1000
equilibrium_steps = 5
c_traffic = 0.1
weight = 'length'

# MAP_NAME='./map.pkl'
MAP_NAME='./downtown_map.pkl'
# Load the map from OpenStreetMap if not already saved
def load_map(name):
    if os.path.exists(name):
        G = pickle.load(open(name, 'rb'))
    else:
        G = ox.graph_from_address('Inner Harbor Baltimore, Maryland, USA', network_type='drive')
        pickle.dump(G, open(name, 'wb'))
    return G

G = load_map(MAP_NAME)

# Select the start and end points of the cars
starts = np.random.choice(G.nodes(), n_drivers, replace=True)
ends = np.random.choice(G.nodes(), n_drivers, replace=True)

def edge_str(a, b):
    return str(a) + "," + str(b)

cached = {}
def original_length(node_a, node_b):
    cur_edge = edge_str(node_a, node_b)
    if cur_edge not in cached:
        cached[cur_edge] = int(G[node_a][node_b][0]['length'])
    return cached[cur_edge]

def cost(node_a, node_b, count):
    return max(original_length(node_a, node_b) * (1 + count * c_traffic / lanes) * count, 0)

# Optimal run
edges_used_opt = {}
driver_path = [[] for _ in range(n_drivers)]
G_opt = copy.deepcopy(G)
G_temp = copy.deepcopy(G)
previous_cost = math.inf
for step in range(equilibrium_steps):
    total_cost = 0
    for driver_id in tqdm(range(n_drivers)):
        saved_edges = copy.deepcopy(edges_used_opt)
        start, end = starts[driver_id], ends[driver_id]
        try:
            path = nx.shortest_path(G_opt, start, end, 'length')
            if str(driver_path[driver_id]) == str(path):
                continue
        except Exception as e:
            path = []
        for node_a, node_b in zip(path[:-1], path[1:]):
            cur_edge = edge_str(node_a, node_b)
            if cur_edge in edges_used_opt:
                edges_used_opt[cur_edge] += 1
            else:
                edges_used_opt[cur_edge] = 1
        if len(driver_path[driver_id]) > 0:
            for node_a, node_b in zip(driver_path[driver_id][:-1], driver_path[driver_id][1:]):
                cur_edge = edge_str(node_a, node_b)
                edges_used_opt[cur_edge] -= 1
        old_path = driver_path[driver_id]
        driver_path[driver_id] = path
        total_cost = 0
        for cur_edge in edges_used_opt.keys():
            node_a, node_b = (int(node) for node in cur_edge.split(","))
            lanes = 1
            if 'lanes' in G[node_a][node_b][0]:
                lanes = int(G[node_a][node_b][0]['lanes'][0])
            G_opt[node_a][node_b][0]['length'] = original_length(node_a, node_b) * (1 + (1 + step / equilibrium_steps) * edges_used_opt[cur_edge] * c_traffic / lanes)
            G_temp[node_a][node_b][0]['length'] = original_length(node_a, node_b) * (1 + edges_used_opt[cur_edge] * c_traffic / lanes)
            total_cost += cost(node_a, node_b, edges_used_opt[cur_edge] - 1)
        if step > 0:
            if total_cost < previous_cost:
                previous_cost = total_cost
            else:
                driver_path[driver_id] = old_path
                total_cost = previous_cost
                edges_used_opt = saved_edges

    ev = [G_temp[node_a][node_b][0]['length'] / G[node_a][node_b][0]['length'] for node_a, node_b in G.edges()]
    norm = colors.Normalize(vmin=min(ev)*0.8, vmax=max(ev))
    cmap = cm.ScalarMappable(norm=norm, cmap=cm.inferno)
    ec = [cmap.to_rgba(cl) for cl in ev]
    fig, ax = ox.plot_graph(G, bgcolor='k', axis_off=True, node_size=0, edge_color=ec,
        edge_linewidth=1.5, edge_alpha=1, save=True, show=False, filename=str(step) + "cars_optimal")
    print(step, total_cost / n_drivers)

# True run
edges_used_new = {}
driver_path = [[] for _ in range(n_drivers)]
G_new = copy.deepcopy(G)
previous_cost = math.inf
for step in range(equilibrium_steps):
    for driver_id in tqdm(range(n_drivers)):
        start, end = starts[driver_id], ends[driver_id]
        try:
            path = nx.shortest_path(G_new, start, end, 'length')
            if str(driver_path[driver_id]) == str(path):
                continue
        except Exception as e:
            path = []
        for node_a, node_b in zip(path[:-1], path[1:]):
            cur_edge = edge_str(node_a, node_b)
            if cur_edge in edges_used_new:
                edges_used_new[cur_edge] += 1
            else:
                edges_used_new[cur_edge] = 1
        if len(driver_path[driver_id]) > 0:
            for node_a, node_b in zip(driver_path[driver_id][:-1], driver_path[driver_id][1:]):
                cur_edge = edge_str(node_a, node_b)
                edges_used_new[cur_edge] -= 1
        old_path = driver_path[driver_id]
        driver_path[driver_id] = path
        total_cost = 0
        for cur_edge in edges_used_new.keys():
            node_a, node_b = (int(node) for node in cur_edge.split(","))
            lanes = 1
            if 'lanes' in G[node_a][node_b][0]:
                lanes = int(G[node_a][node_b][0]['lanes'][0])
            G_new[node_a][node_b][0]['length'] = original_length(node_a, node_b) * (1 + edges_used_new[cur_edge] * c_traffic / lanes)
            total_cost += cost(node_a, node_b, edges_used_new[cur_edge] - 1)

    ev = [G_new[node_a][node_b][0]['length'] / G[node_a][node_b][0]['length'] for node_a, node_b in G.edges()]
    norm = colors.Normalize(vmin=min(ev)*0.8, vmax=max(ev))
    cmap = cm.ScalarMappable(norm=norm, cmap=cm.inferno)
    ec = [cmap.to_rgba(cl) for cl in ev]
    fig, ax = ox.plot_graph(G, bgcolor='k', axis_off=True, node_size=0, edge_color=ec,
        edge_linewidth=1.5, edge_alpha=1, save=True, show=False, filename=str(step) + "cars")
    print(step, total_cost / n_drivers)

ev = [G_new[node_a][node_b][0]['length'] - G_temp[node_a][node_b][0]['length'] for node_a, node_b in G.edges()]
for _, (node_to_remove_a, node_to_remove_b) in sorted(zip(ev, G.edges()), reverse=True):
    stored_length = G[node_to_remove_a][node_to_remove_b][0]['length']
    G[node_to_remove_a][node_to_remove_b][0]['length'] = math.inf

    # Yet another greedy run
    edges_used_new = {}
    driver_path = [[] for _ in range(n_drivers)]
    G_new = copy.deepcopy(G)
    previous_cost = math.inf
    for step in range(equilibrium_steps):
        for driver_id in tqdm(range(n_drivers)):
            start, end = starts[driver_id], ends[driver_id]
            try:
                path = nx.shortest_path(G_new, start, end, 'length')
                if str(driver_path[driver_id]) == str(path):
                    continue
            except Exception as e:
                path = []
            for node_a, node_b in zip(path[:-1], path[1:]):
                cur_edge = edge_str(node_a, node_b)
                if cur_edge in edges_used_new:
                    edges_used_new[cur_edge] += 1
                else:
                    edges_used_new[cur_edge] = 1
            if len(driver_path[driver_id]) > 0:
                for node_a, node_b in zip(driver_path[driver_id][:-1], driver_path[driver_id][1:]):
                    cur_edge = edge_str(node_a, node_b)
                    edges_used_new[cur_edge] -= 1
            old_path = driver_path[driver_id]
            driver_path[driver_id] = path
            total_cost = 0
            for cur_edge in edges_used_new.keys():
                node_a, node_b = (int(node) for node in cur_edge.split(","))
                lanes = 1
                if 'lanes' in G[node_a][node_b][0]:
                    lanes = int(G[node_a][node_b][0]['lanes'][0])
                G_new[node_a][node_b][0]['length'] = original_length(node_a, node_b) * (1 + edges_used_new[cur_edge] * c_traffic / lanes)
                total_cost += cost(node_a, node_b, edges_used_new[cur_edge] - 1)

        ev = [G_new[node_a][node_b][0]['length'] / G[node_a][node_b][0]['length'] for node_a, node_b in G.edges()]
        norm = colors.Normalize(vmin=min(ev)*0.8, vmax=max(ev))
        cmap = cm.ScalarMappable(norm=norm, cmap=cm.inferno)
        ec = [cmap.to_rgba(cl) for cl in ev]
        fig, ax = ox.plot_graph(G, bgcolor='k', axis_off=True, node_size=0, edge_color=ec,
            edge_linewidth=1.5, edge_alpha=1, save=True, show=False, filename=str(step) + "cars_removed")
        print(step, total_cost / n_drivers)
    G[node_to_remove_a][node_to_remove_b][0]['length'] = stored_length



norm = colors.Normalize(vmin=min(ev)*0.8, vmax=max(ev))
cmap = cm.ScalarMappable(norm=norm, cmap=cm.inferno)
ec = [cmap.to_rgba(cl) for cl in ev]
fig, ax = ox.plot_graph(G, bgcolor='k', axis_off=True, node_size=0, edge_color=ec,
    edge_linewidth=1.5, edge_alpha=1, save=True, show=False, filename="diff_cars")
