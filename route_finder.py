import numpy as np
import osmnx as ox
from math import radians, cos, sin, asin, sqrt


def get_shortest_route(map, start_location, end_location):
    """
    Returns the shortest route between the two given locations in the map
    Locations are given in (lat, long) format
    """

    # Get the nearest map graph nodes for both locations
    start_node, end_node = ox.distance.nearest_nodes(map, *list(zip(reversed(start_location), reversed(end_location))))

    # Call the osmnx api to get the shortest route between them
    route = ox.shortest_path(map, start_node, end_node, cpus=None)

    # Convert the route graph-node-id format to a lat-long list
    locations = []
    for node_id in route:
        node = map.nodes[node_id]
        locations.append([node["y"], node["x"]])

    return locations


def find_closest_bike_stations(location, stations, config, return_bikes = False):
    """
    Returns the closest bike stations to a given location
    @param return_bikes: If the user intent is to return or lend a bike
    """

    distances = list()
    # Calculate the straight-line distance to each bike station
    for entry in stations.iterrows():
        distances.append(haversine(location[0], location[1], entry[1].latitude, entry[1].longitude))

    # get their distance order
    distance_order = np.argsort(distances)

    ordered_stations = []
    # Get the stations ordered by distance
    for index in distance_order:
        station = stations.iloc[index]

        # If the user wants to return bikes, docks have to be available, else bikes have to be available
        if not return_bikes:
            # Check if there are enough bikes and the kiosk is open
            if station.bikesAvailable >= int(config["STATIONS"]["minimumBikesAvailable"]) \
                    and station.kioskPublicStatus == "Active":
                ordered_stations.append((distances[index], station))
        elif return_bikes:
            # Check if there are enough free docks and the kiosk is open
            if station.docksAvailable >= int(config["STATIONS"]["minimumBikesAvailable"]) \
                    and station.kioskPublicStatus == "Active":
                ordered_stations.append((distances[index], station))

    # Return the closest n bike stations ordered by distance
    return ordered_stations[:int(config["STATIONS"]["closestBikeStations"])]


def haversine(lat1, lon1, lat2, lon2):
    """
    Returns distance in kilometers between two lat-long pairs on the earch surface
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers
    return c * r
