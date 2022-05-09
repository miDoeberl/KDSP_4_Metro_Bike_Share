import osmnx as ox
import dash
import dash_leaflet as dl
import dash_leaflet.express as dlx
import pathlib
import requests


class MapPlotter:

    def __init__(self):
        self.cache_directory = "data"
        self.cache_dir_path = pathlib.Path(__file__).parent / self.cache_directory

    def plot_map(self, map, stations):
        app = dash.Dash()

        dummy_orig = list(map)[0]
        dummy_dest = list(map)[-1]
        route = ox.shortest_path(map, dummy_orig, dummy_dest)
        locations = []
        for node_id in route:
            node = map.nodes[node_id]
            locations.append([node["y"], node["x"]])

        route_line = dl.Polyline(positions=locations)


        dicts = []
        for station in stations.iterrows():
            name_string = station[1]["name"]
            location_string = station[1]["addressStreet"]
            bikes_available_classic = station[1]["classicBikesAvailable"]
            bikes_available_smart = station[1]["smartBikesAvailable"]
            bikes_available_electric = station[1]["electricBikesAvailable"]
                            
            popup_html = name_string + "<br>" \
                + location_string + "<br>" \
                + "Classic bikes: " + str(bikes_available_classic) + "<br>" \
                + "Smart bikes: " + str(bikes_available_smart) + "<br>" \
                + "Electric bikes: " + str(bikes_available_electric)

            dicts.append(dict(popup=popup_html, lat=station[1]["location"][0], lon=station[1]["location"][1]))
        cluster = dl.GeoJSON(id="markers", data=dlx.dicts_to_geojson(dicts), cluster=True, zoomToBoundsOnClick=True)

        app.layout = dl.Map(children=[dl.TileLayer()] + [cluster] + [route_line],
                            style={'width': '1000px', 'height': '500px'})

        app.run_server()
