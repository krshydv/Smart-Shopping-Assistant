from modules.dataset_to_graph_from_json import build_graph_from_json
from modules.graph_utils import dijkstra, get_shortest_path
from modules.json_writer import write_results_json

def main():
    path = "data/product_data_with_nodeid.json"
    graph = build_graph_from_json(path)

    start = "Amazon_Amazon_Laptop_Model_1"
    end = "Flipkart_Flipkart_Mobile_Model_28"

    distances, previous = dijkstra(graph, start)
    shortest_path = get_shortest_path(previous, start, end)

    print("Shortest path:", ' -> '.join(shortest_path))
    print("Total cost:", distances[end])

    write_results_json(graph, shortest_path, distances[end], "results/results.json")

if __name__ == "__main__":
    main()
