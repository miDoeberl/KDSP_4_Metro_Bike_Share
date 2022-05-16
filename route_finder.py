import osmnx as ox

def get_shortest_route(map, start_location, end_location):
    start_node = ox.get_nearest_node(map, tuple(start_location), method='haversine')
    end_node = ox.get_nearest_node(map, tuple(end_location), method='haversine')
    route = ox.shortest_path(map, start_node, end_node)
    locations = []
    for node_id in route:
        node = map.nodes[node_id]
        locations.append([node["y"], node["x"]])

    return locations