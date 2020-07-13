# libraries
import json
import networkx as nx
from random import random
from random import randrange
from datetime import datetime
from collections import deque

# open data
with open('/home/noe/Università/in_corso/Algoritmi/APAD-project/dati/dati-json/dpc-covid19-ita-province.json') as f:
    d = json.load(f)

today = d[len(d)-1].get("data")
begin = len(d)-1
while d[begin].get("data") == today:
    begin -= 1
newd = d[begin:]

# print(newd)
# print(len(d))

# preparing data to build the graph
lats = {}
longs = {}
for record in newd:                                             # for each observation
    if record['lat'] != 0:                                      # drop the wrong observation (lat or long = 0)
        lats[record['sigla_provincia']] = record['lat']         # store the name of the city and it latitude
        longs[record['sigla_provincia']] = record['long']       # and longitude in two dictionaries: lats e longs

# sort the list of cities by its latitude
prov_sort = sorted(lats, key=lats.get)

def graph_builder(node_list_sort, lat, long, dist_max, weight=False):
    """It build a graph nodes are cities contained in node_list_sort
    two cities are linked if their lats and longs are nearer than dist_max.
    node_list_sort: list of cities sorted by latitudes
    lat: dictionary where each node (key) is associated to its latitude
    long: dictionary where each node (key) is associated to its longitude
    if weight=True the edges are weighted with the Euclidean distance between the cities
    """
    G = nx.Graph()
    dist = {}
    i = 0
    j = 1
    while i <= (len(node_list_sort)-1):
        G.add_node(node_list_sort[i], lat=lat[node_list_sort[i]], long=long[node_list_sort[i]])
        if j <= (len(node_list_sort)-1) and abs(lat[node_list_sort[i]] - lat[node_list_sort[j]]) < dist_max:
            if abs(long[node_list_sort[i]] - long[node_list_sort[j]]) < dist_max:
                G.add_edge(node_list_sort[i], node_list_sort[j])
                if weight:
                    lat_diff = (lat[node_list_sort[i]] - lat[node_list_sort[j]])**2
                    long_diff = (long[node_list_sort[i]] - long[node_list_sort[j]])**2
                    dist[node_list_sort[i], node_list_sort[j]] = (lat_diff + long_diff)**(1/2)
                    nx.set_edge_attributes(G, dist, 'distance')
                j += 1
            else:
                j += 1
        else:
            i += 1
            j = i + 1
    return G


P = graph_builder(prov_sort, lats, longs, dist_max=0.8)
# print(P.nodes.data())
# print(P.edges())
# print(len(P.edges()))

def generate_x():
    """Random generator for latitude
    """
    while True:
        r = randrange(30, 49)
        eps = random()
        yield r+eps

def generate_y():
    """Random generator for longitude
    """
    while True:
        r = randrange(10, 19)
        eps = random()
        yield r+eps

def random_graph(n):
    """It build:
    - a list of nodes with length n;
    - a dictionary where each node (key) is associated to a random latitude;
    - a dictionary where each node (key) is associated to a random longitude;
    The function exploits two generator for latitude and longitude
    """
    node_list = []
    lat = {}
    long = {}
    x = generate_x()
    y = generate_y()
    for i in range(n):
        node_list.append(i)
        lat[i] = next(x)
        long[i] = next(y)
    return node_list, lat, long


rand_nodes, rand_lat, rand_long = random_graph(2000)

rand_graph1 = graph_builder(sorted(rand_lat, key=rand_lat.get), rand_lat, rand_long, dist_max=0.8)
# print(len(rand_graph1.edges()))

R = graph_builder(prov_sort, lats, longs, dist_max=0.08)
# print(len(R.edges()))

rand_graph2 = graph_builder(sorted(rand_lat, key=rand_lat.get), rand_lat, rand_long, dist_max=0.08)
# print(len(rand_graph2.edges()))

P_weight = graph_builder(prov_sort, lats, longs, dist_max=0.8, weight=True)
# print(nx.get_edge_attributes(P_weight, 'distance'))
R_weight = graph_builder(prov_sort, lats, longs, dist_max=0.08, weight=True)
# print(nx.get_edge_attributes(R_weight, 'distance'))

# nx.draw_random(P, with_labels=True)
# plt.savefig("/home/noe/Università/in_corso/Algoritmi/APAD-project/mygraph.png")

# counting triangles
def sorted_degree(G):
    """Given a graph G, it calculates the degree for each node
    and it returns a list of nodes sorted by degree
    """
    nodes = list(G.nodes())
    deg = {}
    for n in nodes:
        deg[n] = len(G[n])
    return deg, sorted(deg, key=deg.get)

# print(sorted_degree(P))

def passes(v, w, degree):
    """Check if the degree of v is less than the degree of w
    if are equal check which node is smaller alphabetically
    """
    return degree[v] < degree[w] or (degree[v] == degree[w] and v < w)
# print(sort_deg, degree)

def triangles_discover(G):
    """Given a graph G, this function returns the list of triangles
    """
    degree, sort_deg = sorted_degree(G)
    triangles = []
    for node in sort_deg:
        near = list(G.neighbors(node))
        if len(near) > 1:
            for i in range(len(near)-1):
                if passes(node, near[i], degree):
                    for j in range(i+1, len(near)):
                        if passes(node, near[j], degree) and near[j] in G.neighbors(near[i]):
                                triangles.append((node, near[i], near[j]))
    return triangles


triangles_list = triangles_discover(P)
print(triangles_list)
triangles_count = len(triangles_discover(P))
print(triangles_count)

start = datetime.now()
triangles_discover(P)
print(datetime.now() - start)

start = datetime.now()
sum(nx.triangles(P).values())/3
print(datetime.now() - start)

# TOY EXAMPLE
g = nx.complete_graph(5)
# nx.draw_circular(g, with_labels=True)
# plt.savefig("/home/noe/Università/in_corso/Algoritmi/APAD-project/toy_count_triangle.png")

# print(g.nodes())
start = datetime.now()
triangles_discover(g)
print(datetime.now() - start)

start = datetime.now()
sum(nx.triangles(g).values())/3
print(datetime.now() - start)

def ecc(graph, start):
    """Given a graph and a vertex v of the graph, it returns the eccentricity
    of v
    """
    if start in P.graph['largest_cc']:
        queue = deque([start])
        level = {start: 0}
        while queue:
            v = queue.popleft()
            for n in graph[v]:
                if n not in level:
                    queue.append(n)
                    level[n] = level[v] + 1
        maxlev = max(level.values())
        return maxlev
    else:
        return float('inf')


P.graph['largest_cc'] = max(nx.connected_components(P), key=len)
p = nx.subgraph(P, P.graph['largest_cc'])
R.graph['largest_cc'] = max(nx.connected_components(R), key=len)
r = nx.subgraph(R, R.graph['largest_cc'])

nx.set_node_attributes(p, None, "eccentricity")
nx.set_node_attributes(r, None, "eccentricity")

for node in list(p.nodes()):
    p.nodes[node]["eccentricity"] = ecc(graph=p, start=node)

for node in list(r.nodes()):
    r.nodes[node]["eccentricity"] = ecc(graph=r, start=node)










