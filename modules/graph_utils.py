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
