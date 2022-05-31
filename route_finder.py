import numpy as np
import pandas as pd
import osmnx as ox
import networkx as nx
from math import radians, cos, sin, asin, sqrt


def get_shortest_route(map, start_location, end_location):
    start_node = ox.get_nearest_node(map, tuple(start_location), method='haversine')
    end_node = ox.get_nearest_node(map, tuple(end_location), method='haversine')
    route = ox.shortest_path(map, start_node, end_node, cpus=None)
    locations = []
    for node_id in route:
        node = map.nodes[node_id]
        locations.append([node["y"], node["x"]])

    return locations


def find_closest_bike_stations(location, stations, config, return_bikes = False):
    distances = list()
    for entry in stations.iterrows():
        distances.append(haversine(location[0], location[1], entry[1].latitude, entry[1].longitude))
    distance_order = np.argsort(distances)

    ordered_stations = []
    for index in distance_order:
        station = stations.iloc[index]
        if not return_bikes:
            if station.bikesAvailable >= int(config["STATIONS"]["minimumBikesAvailable"]) \
                    and station.kioskPublicStatus == "Active":
                ordered_stations.append((distances[index], station))
        elif return_bikes:
            if station.docksAvailable >= int(config["STATIONS"]["minimumBikesAvailable"]) \
                    and station.kioskPublicStatus == "Active":
                ordered_stations.append((distances[index], station))

    return ordered_stations[:int(config["STATIONS"]["closestBikeStations"])]


def haversine(lat1, lon1, lat2, lon2):
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r
