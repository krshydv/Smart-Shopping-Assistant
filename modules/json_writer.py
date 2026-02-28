def write_results_json(graph, path, total_cost, filename):
    with open(filename, 'w') as file:
        file.write("{\n")

        # Nodes
        file.write('  "nodes": [\n')
        nodes = list(graph.graph.keys())
        file.write(',\n'.join([f'    "{n}"' for n in nodes]))
        file.write('\n  ],\n')

        # Edges
        file.write('  "edges": [\n')
        seen = set()
        edge_lines = []
        for from_node in graph.graph:
            for to_node, weight in graph.graph[from_node]:
                key = tuple(sorted((from_node, to_node)))
                if key not in seen:
                    seen.add(key)
                    edge_lines.append(f'    {{"from": "{from_node}", "to": "{to_node}", "weight": {weight}}}')
        file.write(',\n'.join(edge_lines))
        file.write('\n  ],\n')

        # Optimal path
        file.write('  "optimal_path": [\n')
        file.write(',\n'.join([f'    "{n}"' for n in path]))
        file.write('\n  ],\n')

        file.write(f'  "total_cost": {total_cost}\n')
        file.write("}")
