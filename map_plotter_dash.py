import osmnx as ox
import dash
import dash_leaflet as dl
import dash_leaflet.express as dlx
import dash_html_components as html
import pathlib
import route_finder

app = dash.Dash(prevent_initial_callbacks=True)

SELECT_START_POINT = 0
SELECT_END_POINT = 1
ROUTE_SELECTED = 2

start_location = None
end_location = None
route_state = SELECT_START_POINT

class MapPlotter:

    def __init__(self, __config):
        self.config = __config
        self.cache_directory = "data"
        self.cache_dir_path = pathlib.Path(__file__).parent / self.cache_directory

    def plot_map(self, map, stations):
        global app
        global __map
        __map = map

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

        city_center = ox.geocode_to_gdf(self.config["MAP"]["place"]).centroid

        map = dl.Map(children=[dl.TileLayer(), dl.LayerGroup(id="container", children=[]), cluster, route_line],
                            id="map",
                            center=[city_center.y[0], city_center.x[0]],
                            zoom=11,
                            style={'height': '90vh'})

        app.layout = html.Div([
                            map
                            ])

        app.run_server()


    @ app.callback(dash.Output("container", "children"), [dash.Input("map", "click_lat_lng")], [dash.State("container", "children")])
    def add_marker(click_lat_lng, children):
        global route_state, start_location, end_location

        children.append(dl.CircleMarker(center=click_lat_lng))
        
        if route_state == SELECT_START_POINT:
            start_location = click_lat_lng
            route_state = SELECT_END_POINT
            return children
        elif route_state == SELECT_END_POINT:
            end_location = click_lat_lng
            route_state = ROUTE_SELECTED

            route = dl.Polyline(positions=route_finder.get_shortest_route(__map, start_location, end_location))
            children.append(route)

            return children

        return children
