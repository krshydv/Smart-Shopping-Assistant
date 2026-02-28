class ProductGraph:
    def __init__(self):
        # Using a dictionary to store adjacency list:
        # { node_id: [(neighbor_node_id, weight), ...], ... }
        self.graph = {}

    def add_connection(self, node1, node2, weight):
        # Add connection node1 -> node2
        if node1 not in self.graph:
            self.graph[node1] = []
        self.graph[node1].append((node2, weight))

        # Add connection node2 -> node1 (undirected graph)
        if node2 not in self.graph:
            self.graph[node2] = []
        self.graph[node2].append((node1, weight))

    def get_neighbors(self, node):
        return self.graph.get(node, [])

    def __repr__(self):
        return f"ProductGraph({self.graph})"
