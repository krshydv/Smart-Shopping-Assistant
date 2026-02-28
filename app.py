from flask import Flask, request, jsonify, render_template
# Import necessary modules for your application logic
from modules.dataset_to_graph_from_json import build_graph_from_json
from modules.graph_utils import dijkstra, get_shortest_path
from modules.json_writer import write_results_json # This import seems unused in the provided routes
from modules.product_filter_and_recommender import load_data, filter_products, recommend_products

# Initialize the Flask app, specifying the templates folder
# The 'templates' folder must exist in the same directory as this app.py file
app = Flask(__name__, template_folder="templates")

# Define the path to your dataset.
# Ensure this file exists at 'data/product_data_with_nodeid.json' relative to app.py
DATASET_PATH = "data/product_data_with_nodeid.json"

# This route serves your main HTML page (the frontend UI)
@app.route("/")
def home():
    """
    Renders the index.html template when the root URL is accessed.
    This serves your main web application interface.
    """
    return render_template("index.html")

@app.route("/filter", methods=["POST"])
def filter_products_route():
    """
    Filters products based on criteria received in the POST request.
    It loads all product data, applies the filters, and returns
    the filtered list as a JSON response.
    """
    data = request.json
    try:
        # Assuming load_data, filter_products are defined in modules.product_filter_and_recommender
        all_data = load_data(DATASET_PATH)
        filtered = filter_products(
            all_data,
            min_price=data.get("min_price"),
            max_price=data.get("max_price"),
            min_rating=data.get("min_rating"),
            min_reviews=data.get("min_reviews"),
            max_delivery_days=data.get("max_delivery_days")
        )
        return jsonify(filtered)
    except Exception as e:
        # Catch any exceptions during filtering and return an error message
        return jsonify({"error": f"Error filtering products: {str(e)}"}), 500

@app.route("/recommend", methods=["POST"])
def recommend_products_route():
    """
    Recommends products based on user preferences received in the POST request.
    It loads all product data, applies recommendation logic, and returns
    a list of recommended products as a JSON response.
    """
    prefs = request.json
    try:
        # Assuming load_data, recommend_products are defined in modules.product_filter_and_recommender
        all_data = load_data(DATASET_PATH)
        recs = recommend_products(all_data, prefs, top_n=5)
        return jsonify(recs)
    except Exception as e:
        # Catch any exceptions during recommendation and return an error message
        return jsonify({"error": f"Error recommending products: {str(e)}"}), 500

@app.route("/shortest-path", methods=["POST"])
def shortest_path():
    """
    Calculates the shortest path between two product nodes in a graph.
    It builds a graph from the dataset, uses Dijkstra's algorithm,
    and returns the path and total cost as a JSON response.
    Assumes 'start' and 'end' node IDs are provided in the request JSON.
    """
    data = request.json
    
    # Ensure 'start' and 'end' keys are present in the request data
    start_node = data.get("start")
    end_node = data.get("end")

    if not start_node or not end_node:
        return jsonify({"error": "Missing 'start' or 'end' node in request"}), 400

    try:
        # Assuming build_graph_from_json, dijkstra, get_shortest_path are defined in respective modules
        graph = build_graph_from_json(DATASET_PATH)
        distances, previous = dijkstra(graph, start_node)
        path = get_shortest_path(previous, start_node, end_node)
        
        # Check if a path was found
        total_cost = distances.get(end_node)
        if path is None or total_cost is None:
            return jsonify({"path": [], "total_cost": "N/A", "message": "No path found between specified nodes"}), 404

        return jsonify({
            "path": path,
            "total_cost": total_cost
        })
    except Exception as e:
        # Catch any exceptions during shortest path calculation and return an error message
        return jsonify({"error": f"Error calculating shortest path: {str(e)}"}), 500

@app.route("/search", methods=["POST"])
def search_product():
    try:
        data = request.json
        query = data.get("query", "").lower()

        all_data = load_data(DATASET_PATH)

        # Match against product name, brand, or category
        matched = [
            p for p in all_data
            if query in p.get("product_name", "").lower()
            or query in p.get("brand", "").lower()
            or query in p.get("category", "").lower()
        ]

        return jsonify(matched)
    except Exception as e:
        return jsonify({"error": f"Error searching product: {str(e)}"}), 500

if __name__ == "__main__":
    try:
        # Run the Flask application in debug mode for development.
        # This automatically reloads the server on code changes and provides a debugger.
        app.run(debug=True)
    except Exception as e:
        print(f"Failed to start Flask application: {e}")
        print("Please ensure all required Python packages are installed (e.g., Flask, numpy, scikit-learn).")
        print("Also, check if your 'modules' directory and the 'data' directory with 'product_data_with_nodeid.json' exist and are accessible.")
