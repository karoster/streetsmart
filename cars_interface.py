import osmnx as ox
import networkx as nx
import copy
from random import sample
import os
import pickle
n_drivers = 200
equilibrium_steps = 20
c_traffic = 0.1

OUT_FILE = './harbor.txt'

G = ox.graph_from_address('Inner Harbor Baltimore, Maryland, USA', network_type='drive')
with open(OUT_FILE, 'w') as f:
    f.write('')

with open(OUT_FILE, 'w+') as f:

    f.write('{}\n'.format(len(G.nodes())))

    nodes_to_index = {n : i for i, n in enumerate(G.nodes())}


    for a, b in G.edges():
        lanes = 1
        if 'lanes' in G[a][b][0]:
            lanes = G[a][b][0]['lanes']
        if isinstance(lanes, list):
            lanes = int(lanes[0])
        f.write('{} {} {} {}\n'.format(nodes_to_index[a], nodes_to_index[b], G[a][b][0]['length'], lanes))
