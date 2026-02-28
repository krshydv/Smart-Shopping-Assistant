from modules.product_graph import ProductGraph
def load_dataset(path):
    with open(path, 'r') as file:
        content = file.read()
        data = eval(content)  # only safe here because you're using your own dataset
    return data

def delivery_days(delivery_str):
    try:
        parts = delivery_str.split('-')
        return (int(parts[0]) + int(parts[1].split()[0])) / 2
    except:
        return 5  # default fallback

def calculate_weight(p1, p2):
    price_diff = abs(p1['price'] - p2['price'])
    rating_diff = abs(p1['seller_rating'] - p2['seller_rating'])
    delivery_diff = abs(delivery_days(p1['delivery_time']) - delivery_days(p2['delivery_time']))
    return price_diff + rating_diff * 10 + delivery_diff * 2

def build_graph_from_json(path):
    data = load_dataset(path)
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
