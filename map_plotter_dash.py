import osmnx as ox
import dash
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash import html
import pathlib
import route_finder

app = dash.Dash(prevent_initial_callbacks=True)

SELECT_START_POINT = 0
SELECT_END_POINT = 1
ROUTE_SELECTED = 2

start_location = None
end_location = None
route_state = SELECT_START_POINT
start_bike_station = None
end_bike_station = None

class MapPlotter:

    def __init__(self, __config):
        global config
        config = __config
        self.cache_directory = "data"
        self.cache_dir_path = pathlib.Path(__file__).parent / self.cache_directory

    def plot_map(self, map, station_loader):
        global app, __map, __station_loader
        __map = map
        __station_loader = station_loader

        dicts = []
        station_markers = []
        for station in station_loader.get_station_states().iterrows():
            name_string = station[1]["name"]
            location_string = station[1]["addressStreet"]
            bikes_available_classic = station[1]["classicBikesAvailable"]
            bikes_available_smart = station[1]["smartBikesAvailable"]
            bikes_available_electric = station[1]["electricBikesAvailable"]

            popup_html = [html.B(name_string),
                         html.B(location_string),
                         "Classic bikes: " + str(bikes_available_classic),
                         "Smart bikes: " + str(bikes_available_smart),
                         "Electric bikes: " + str(bikes_available_electric)]

            dicts.append(dict(popup=popup_html, lat=station[1]["location"][0], lon=station[1]["location"][1]))
            station_markers.append(dl.CircleMarker(center=[station[1]["location"][0], station[1]["location"][1]], radius=4, children=dl.Popup([html.Div(line) for line in popup_html])))
        cluster = dl.GeoJSON(id="markers", data=dlx.dicts_to_geojson(dicts), cluster=True, zoomToBoundsOnClick=True)

        city_center = ox.geocode_to_gdf(config["MAP"]["place"]).centroid

        map = dl.Map(children=[dl.TileLayer(), dl.LayerGroup(id="container", children=station_markers)],
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
        global route_state, start_location, end_location, start_bike_station, end_bike_station

        if route_state != ROUTE_SELECTED:
            children.append(dl.Marker(position=click_lat_lng))
        
        if route_state == SELECT_START_POINT:
            if start_location is not None:
                start_location = None
                end_location = None
                start_bike_station = None
                end_bike_station = None

            start_location = click_lat_lng
            route_state = SELECT_END_POINT

            bike_station_locations = route_finder.find_closest_bike_stations(start_location, __station_loader.get_station_states(), config, return_bikes=False)
            start_bike_station = bike_station_locations[0][1].location
            for station in bike_station_locations:
                tooltip = ""
                for index, child in enumerate(children):
                    if type(child) == dict and child["type"] == "CircleMarker" and child["props"]["center"] == [station[1].latitude, station[1].longitude]:
                        tooltip = child["props"]["children"]
                        travel_time = station[0] * 1000 / (float(config["STATIONS"]["walkingVelocity"]) / 3.6) / 60
                        tooltip["props"]["children"].append(html.Div(f"Estimated travel time: {travel_time:.0f} - {travel_time * 2:.1f} min."))
                        break
                children.append(dl.CircleMarker(center=[station[1].latitude, station[1].longitude], color="Limegreen", opacity=1, fillOpacity=0.75, radius=6, children=tooltip))

            bike_station_locations_return = route_finder.find_closest_bike_stations(start_location, __station_loader.get_station_states(), config, return_bikes=True)
            for station in bike_station_locations_return:
                tooltip = ""
                for child in children:
                    if type(child) == dict and child["type"] == "CircleMarker" and child["props"]["center"] == [station[1].latitude, station[1].longitude]:
                        tooltip = child["props"]["children"]
                        travel_time = station[0] * 1000 / (float(config["STATIONS"]["walkingVelocity"]) / 3.6) / 60
                        if len(tooltip["props"]["children"]) < 6:
                            tooltip["props"]["children"].append(html.Div(f"Estimated travel time: {travel_time:.0f} - {travel_time * 2:.1f} min."))
                        tooltip["props"]["children"].append(html.Div(f"Docks available: {station[1].docksAvailable}"))
                        break
                children.append(dl.CircleMarker(center=[station[1].latitude, station[1].longitude], color="Orangered", opacity=1, fillOpacity=1, radius=4, children=tooltip))


            return children
        elif route_state == SELECT_END_POINT:
            end_location = click_lat_lng
            route_state = SELECT_START_POINT

            bike_station_locations_return = route_finder.find_closest_bike_stations(end_location, __station_loader.get_station_states(), config, return_bikes=True)
            end_bike_station = bike_station_locations_return[0][1].location
            for station in bike_station_locations_return:
                tooltip = ""
                for child in children:
                    if type(child) == dict and child["type"] == "CircleMarker" and child["props"]["center"] == [station[1].latitude, station[1].longitude]:
                        tooltip = child["props"]["children"]
                        travel_time = station[0] * 1000 / (float(config["STATIONS"]["walkingVelocity"]) / 3.6) / 60
                        if len(tooltip["props"]["children"]) < 6:
                            tooltip["props"]["children"].append(html.Div(f"Estimated travel time to destination: {travel_time:.0f} - {travel_time * 2:.1f} min."))
                        tooltip["props"]["children"].append(html.Div(f"Docks available: {station[1].docksAvailable}"))
                        break
                children.append(dl.CircleMarker(center=[station[1].latitude, station[1].longitude], color="Orangered", opacity=1, fillOpacity=1, radius=4, children=tooltip))


            route = dl.Polyline(positions=route_finder.get_shortest_route(__map, start_location, start_bike_station), color="hotpink", weight=5)
            children.append(route)
            route = dl.Polyline(positions=route_finder.get_shortest_route(__map, start_bike_station, end_bike_station), weight=5)
            children.append(route)
            route = dl.Polyline(positions=route_finder.get_shortest_route(__map, end_bike_station, end_location), color="hotpink", weight=5)
            children.append(route)

            return children

        return children
