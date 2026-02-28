### product_graph.py ###

class ProductGraph:
    def _init_(self):
        self.graph = {}

    def add_connection(self, node1, node2, weight):
        if node1 not in self.graph:
            self.graph[node1] = []
        self.graph[node1].append((node2, weight))
        if node2 not in self.graph:
            self.graph[node2] = []
        self.graph[node2].append((node1, weight))

    def get_neighbors(self, node):
        return self.graph.get(node, [])

    def _repr_(self):
        return f"ProductGraph({self.graph})"


### graph_utils.py ###

def dijkstra(graph, start):
    unvisited = set(graph.graph.keys())
    distances = {node: float('inf') for node in unvisited}
    previous = {node: None for node in unvisited}
    distances[start] = 0

    while unvisited:
        current = min((node for node in unvisited), key=lambda node: distances[node])
        unvisited.remove(current)

        for neighbor, weight in graph.get_neighbors(current):
            new_distance = distances[current] + weight
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = current

    return distances, previous

def get_shortest_path(previous, start, end):
    path = []
    current = end
    while current and current != start:
        path.insert(0, current)
        current = previous[current]
    if current == start:
        path.insert(0, start)
    return path


### dataset_to_graph_from_json.py ###

from modules.product_graph import ProductGraph

def delivery_days(delivery_str):
    try:
        parts = delivery_str.split('-')
        return (int(parts[0]) + int(parts[1].split()[0])) / 2
    except:
        return 5

def calculate_weight(p1, p2):
    price_diff = abs(p1['price'] - p2['price'])
    rating_diff = abs(p1['seller_rating'] - p2['seller_rating'])
    delivery_diff = abs(delivery_days(p1['delivery_time']) - delivery_days(p2['delivery_time']))
    return price_diff + rating_diff * 10 + delivery_diff * 2

def build_graph_from_data(data):
    graph = ProductGraph()
    for i in range(len(data)):
        for j in range(i + 1, len(data)):
            p1 = data[i]
            p2 = data[j]
            node1 = p1["node_id"]
            node2 = p2["node_id"]
            weight = calculate_weight(p1, p2)
            graph.add_connection(node1, node2, weight)
    return graph


### product_filter_and_recommender.py ###

import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def load_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def parse_delivery_time(delivery_str):
    parts = delivery_str.split()
    if len(parts) >= 1:
        range_part = parts[0]
        if '-' in range_part:
            try:
                min_str, max_str = range_part.split('-')
                return int(min_str), int(max_str)
            except:
                return None, None
        else:
            try:
                days = int(range_part)
                return days, days
            except:
                return None, None
    return None, None

def filter_products(data, min_price=None, max_price=None, min_rating=None, min_reviews=None, max_delivery_days=None):
    filtered = []
    for p in data:
        if min_price is not None and p['price'] < min_price:
            continue
        if max_price is not None and p['price'] > max_price:
            continue
        if min_rating is not None and p['seller_rating'] < min_rating:
            continue
        if min_reviews is not None and p['review_count'] < min_reviews:
            continue
        if max_delivery_days is not None:
            min_d, max_d = parse_delivery_time(p['delivery_time'])
            if max_d is not None and max_d > max_delivery_days:
                continue
        filtered.append(p)
    return filtered

def build_feature_matrix(data):
    brands = sorted({p.get('brand', '') for p in data if p.get('brand')})
    ram_vals = []
    prices = []
    for p in data:
        try:
            ram_num = int(''.join(filter(str.isdigit, p.get('RAM', ''))))
        except:
            ram_num = 0
        ram_vals.append(ram_num)
        prices.append(p.get('price', 0))
    ram_min, ram_max = min(ram_vals), max(ram_vals)
    price_min, price_max = min(prices), max(prices)
    X = []
    for p in data:
        brand_vec = [0] * len(brands)
        if p['brand'] in brands:
            brand_vec[brands.index(p['brand'])] = 1
        try:
            ram = int(''.join(filter(str.isdigit, p.get('RAM', ''))))
        except:
            ram = 0
        ram_norm = (ram - ram_min) / (ram_max - ram_min) if ram_max > ram_min else 0
        price = p.get('price', 0)
        price_norm = (price - price_min) / (price_max - price_min) if price_max > price_min else 0
        feature_vec = brand_vec + [ram_norm, price_norm]
        X.append(feature_vec)
    return np.array(X), brands, ram_min, ram_max, price_min, price_max

def recommend_products(data, user_pref, top_n=5):
    X, brands, ram_min, ram_max, price_min, price_max = build_feature_matrix(data)
    brand_vec = [0] * len(brands)
    if 'brand' in user_pref:
        prefs = user_pref['brand'] if isinstance(user_pref['brand'], list) else [user_pref['brand']]
        for b in prefs:
            if b in brands:
                brand_vec[brands.index(b)] = 1
    ram_norm = (int(user_pref['RAM']) - ram_min) / (ram_max - ram_min) if 'RAM' in user_pref and ram_max > ram_min else 0
    if 'price_range' in user_pref:
        min_p, max_p = user_pref['price_range']
        price_mid = (min_p + max_p) / 2
        price_norm = (price_mid - price_min) / (price_max - price_min) if price_max > price_min else 0
    else:
        price_norm = 0
    user_vec = np.array(brand_vec + [ram_norm, price_norm]).reshape(1, -1)
    if np.count_nonzero(user_vec) == 0:
        return []
    sims = cosine_similarity(user_vec, X).flatten()
    top_indices = sims.argsort()[::-1][:top_n]
    return [data[i] for i in top_indices]


### main_filtered.py (dynamic version with error handling) ###

# Get filtering inputs from user
min_price = int(input("Enter minimum price: "))
max_price = int(input("Enter maximum price: "))
min_rating = float(input("Enter minimum seller rating (e.g., 4.0): "))
min_reviews = int(input("Enter minimum number of reviews: "))
max_days = int(input("Enter maximum delivery days: "))

# Load and filter product data
data = load_data("product_data_with_nodeid.json")
filtered = filter_products(data, min_price=min_price, max_price=max_price, min_rating=min_rating, min_reviews=min_reviews, max_delivery_days=max_days)

# Handle case when no product matches filters
if not filtered:
    print("\n❌ No products matched your filters. Please try again with different criteria.")
else:
    # Build graph from filtered products
    graph = build_graph_from_data(filtered)

    # Choose nodes to run Dijkstra
    start = filtered[0]['node_id']
    end = filtered[-1]['node_id']

    # Run Dijkstra
    distances, previous = dijkstra(graph, start)
    path = get_shortest_path(previous, start, end)

    # Output shortest path
    print("\n📦 Shortest Path:", ' -> '.join(path))
    print("💰 Total Cost:", distances[end])

    # Recommendation inputs
    brand_input = input("Enter preferred brands (comma separated): ").split(',')
    ram_input = int(input("Preferred RAM (GB): "))
    price_min_input = int(input("Preferred price min: "))
    price_max_input = int(input("Preferred price max: "))

    preferences = {
        'brand': [b.strip() for b in brand_input],
        'RAM': ram_input,
        'price_range': (price_min_input, price_max_input)
    }

    recommended = recommend_products(data, preferences, top_n=5)
    print("\n🔍 Recommended Products:")
    for p in recommended:
        print(f"- {p['product_name']} | Price: {p['price']} | Brand: {p['brand']} | RAM: {p['RAM']}")