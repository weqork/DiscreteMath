import pandas as pd
import networkx as nx
import itertools

# Загрузка графа из Excel
file_path = "excel.xlsx"
df = pd.read_excel(file_path, index_col=0)
G = nx.from_pandas_adjacency(df)

# Установка весов ребрам (если отсутствуют или NaN, устанавливаем 0)
for u, v, data in G.edges(data=True):
    if 'weight' not in data or data['weight'] is None or pd.isna(data['weight']):
        data['weight'] = 0

# Компоненты вершинной двусвязности (блоки) и точки сочленения
blocks = list(nx.biconnected_components(G))
articulation_points = set(nx.articulation_points(G))
BCT = nx.Graph()
for ap in articulation_points:
    BCT.add_node(ap, type='AP')
for i, block in enumerate(blocks):
    block_id = f'B{i}'
    BCT.add_node(block_id, type='Block', members=block)
    for v in block:
        if v in articulation_points:
            BCT.add_edge(v, block_id)

print("\nБлоки:", blocks)
print("\nТочки сочленения:", articulation_points)
print("\nBCT (ребра):", list(BCT.edges(data=True)))

# Основные характеристики графа
num_nodes = G.number_of_nodes()  # Количество вершин
num_edges = G.number_of_edges()  # Количество ребер
degrees = dict(G.degree())
min_deg = min(degrees.values())  # Минимальная степень
max_deg = max(degrees.values())  # Максимальная степень

# Если граф связный, вычисляем радиус, диаметр и центр, иначе для наибольшей компоненты связности
if nx.is_connected(G):
    rad = nx.radius(G)
    diam = nx.diameter(G)
    center = nx.center(G)
else:
    largest_cc = max(nx.connected_components(G), key=len)
    G_largest = G.subgraph(largest_cc)
    rad = nx.radius(G_largest)
    diam = nx.diameter(G_largest)
    center = nx.center(G_largest)

print("\nОсновные характеристики графа:")
print("Количество вершин:", num_nodes, "(+ 5 изолированных)")
print("Количество ребер:", num_edges)
print("Минимальная степень:", min_deg)
print("Максимальная степень:", max_deg)
print("Радиус:", rad)
print("Диаметр:", diam)
print("Центр:", center)


# Поиск мостов (алгоритм Тарджана)
def find_bridges(G):
    visited = {v: False for v in G.nodes()}
    disc, low, parent = {}, {}, {v: None for v in G.nodes()}
    bridges = []
    time = [0]

    def dfs(u):
        visited[u] = True
        disc[u] = time[0]
        low[u] = time[0]
        time[0] += 1
        for v in G.neighbors(u):
            if not visited[v]:
                parent[v] = u
                dfs(v)
                low[u] = min(low[u], low[v])
                if low[v] > disc[u]:
                    bridges.append((u, v))
            elif v != parent[u]:
                low[u] = min(low[u], disc[v])

    for vertex in G.nodes():
        if not visited[vertex]:
            dfs(vertex)
    return bridges


bridges = find_bridges(G)
print("\nМосты:", bridges)

# 2-реберосвязные компоненты и построение Bridge Tree
H = G.copy()
H.remove_edges_from(bridges)
components = list(nx.connected_components(H))
print("\n2-реберосвязные компоненты:", components)
comp_map = {}
for comp_id, comp in enumerate(components):
    for v in comp:
        comp_map[v] = comp_id
T = nx.Graph()
T.add_nodes_from(range(len(components)))
for u, v in bridges:
    cu, cv = comp_map[u], comp_map[v]
    if cu != cv:
        T.add_edge(cu, cv)
print("\nBridge Tree - Вершины:", list(T.nodes()), "Рёбра:", list(T.edges()))

# Нахождение минимального остовного дерева
T_mst = nx.minimum_spanning_tree(G, weight='weight')
print("\nMST (ребра):", list(T_mst.edges(data=True)))


# Код Прюфера для дерева T_mst
def prufer_code(T):
    T_copy = T.copy()
    prufer = []
    while T_copy.number_of_nodes() > 2:
        leaves = [node for node in T_copy.nodes() if T_copy.degree(node) == 1]
        leaf = min(leaves)
        neighbor = list(T_copy.neighbors(leaf))[0]
        prufer.append(neighbor)
        T_copy.remove_node(leaf)
    return prufer


# Бинарный код дерева (DFS: "1" при спуске, "0" при подъёме)
def binary_code_tree(T):
    root = min(T.nodes())
    code = []

    def dfs(u, parent):
        for v in sorted(T.neighbors(u)):
            if v == parent:
                continue
            code.append("1")
            dfs(v, u)
            code.append("0")

    dfs(root, None)
    return "".join(code)


prufer = prufer_code(T_mst)
binary_str = binary_code_tree(T_mst)
print("\nКод Прюфера:", prufer)
print("\nБинарный код:", binary_str)
