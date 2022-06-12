import os
import osmnx as ox
import dash
import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash import html
import pathlib
import route_finder
from threading import Lock

app = dash.Dash(prevent_initial_callbacks=True)

SELECT_START_POINT = 0
SELECT_END_POINT = 1

start_location = None
end_location = None
route_state = SELECT_START_POINT
start_bike_station = None
end_bike_station = None

mutex = Lock()

class MapPlotter:
    """
    Plots the city map and allows interactions with it
    """

    def __init__(self, __config):
        global config
        config = __config

    def plot_map(self, map, station_loader, web_view):
        """
        Blocking function that shows the map
        """
        global app, __map, __station_loader
        __map = map
        __station_loader = station_loader

        station_markers = []
        # Get the current bike station states and iterate them
        for station in station_loader.get_station_states().iterrows():
            # Get a stations important information, ...
            name_string = station[1]["name"]
            location_string = station[1]["addressStreet"]
            bikes_available_classic = station[1]["classicBikesAvailable"]
            bikes_available_smart = station[1]["smartBikesAvailable"]
            bikes_available_electric = station[1]["electricBikesAvailable"]

            # ... create a html object from it, ...
            popup_html = [html.B(name_string),
                         html.B(location_string),
                         "Classic bikes: " + str(bikes_available_classic),
                         "Smart bikes: " + str(bikes_available_smart),
                         "Electric bikes: " + str(bikes_available_electric)]

            # ... and add it to a station marker as a popup
            # Create a clickable station marker at the current stations location
            station_markers.append(dl.CircleMarker(center=[station[1]["location"][0], station[1]["location"][1]], radius=4, children=dl.Popup([html.Div(line) for line in popup_html])))

        # Get the city center from its name, so the map doesn't load in a random place
        city_center = ox.geocode_to_gdf(config["MAP"]["place"]).centroid

        # Create the map object which can be viewed on the webpage
        map = dl.Map(children=[dl.TileLayer(), dl.LayerGroup(id="container", children=station_markers)],
                            id="map",
                            center=[city_center.y[0], city_center.x[0]],
                            zoom=11,
                            style={'height': '95vh', 'width': '100%', 'margin': 'none', "z-index": 0})

        # Specify the page layout
        app.layout = html.Div([
                            html.Button(id="quit", children="Stop Server", style={"z-index": 5, "float": "right"}),
                            map
                            ])

        # Open the webpage with a delay of one second, ...
        web_view.open_map_site(delay=1)
        # And start the server. The webpage call is before this, because run_server() is a blocking function call
        app.run_server()


    @app.callback(dash.Output("map", "zoom"), [dash.Input("quit", 'n_clicks')])
    def stop_server(n):
        """
        Callback function for the exit button, which stops the server
        """
        os._exit(0)


    @ app.callback(dash.Output("container", "children"), [dash.Input("map", "click_lat_lng")], [dash.State("container", "children")])
    def add_marker(click_lat_lng, children):
        """
        Callback function if the map is clicked
        """
        # Allow only a single concurrent execution of this function
        mutex.acquire()
        global route_state, start_location, end_location, start_bike_station, end_bike_station

        # Add a marker at the last clicked position
        children.append(dl.Marker(position=click_lat_lng))
        
        # If the current objective is to select a starting position
        if route_state == SELECT_START_POINT:
            # Clear any previously selected/added markers
            if start_location is not None:
                start_location = None
                end_location = None
                start_bike_station = None
                end_bike_station = None
                for i in reversed(range(len(children[:-1]))):
                    child = children[i]
                    if isinstance(child, dl.Marker) or \
                       child["type"] == "CircleMarker" and "color" in child["props"] or \
                       child["type"] == "Polyline" or \
                       child["type"] == "Marker":
                        del children[i]

            # Set the starting location to the click location
            start_location = click_lat_lng
            # and make the objective to select an end point
            route_state = SELECT_END_POINT

            # Find the closest bike stations to the clicked point where bikes are available
            bike_station_locations = route_finder.find_closest_bike_stations(start_location, __station_loader.get_station_states(), config, return_bikes=False)
            # Select the closest one as the bike station that will to be visited
            start_bike_station = bike_station_locations[0][1].location
            # Add estimated travel times based on straight line distance to the popups of the closest bike stations
            for station in bike_station_locations:
                tooltip = ""
                for child in children:
                    if type(child) == dict and child["type"] == "CircleMarker" and child["props"]["center"] == [station[1].latitude, station[1].longitude]:
                        tooltip = child["props"]["children"]
                        travel_time = station[0] * 1000 / (float(config["STATIONS"]["walkingVelocity"]) / 3.6) / 60
                        tooltip["props"]["children"].append(html.Div(f"Estimated travel time: {travel_time:.0f} - {travel_time * 2:.1f} min."))
                        break
                # Make the closest bike station markers green
                children.append(dl.CircleMarker(center=[station[1].latitude, station[1].longitude], color="Limegreen", opacity=1, fillOpacity=0.75, radius=6, children=tooltip))

            # Find the closest bike stations to the clicked point where bikes can be returned
            bike_station_locations_return = route_finder.find_closest_bike_stations(start_location, __station_loader.get_station_states(), config, return_bikes=True)
            # Add estimated travel times based on straight line distance to the popups of the closest bike stations
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
                # Make the closest bike station markers orange-red
                children.append(dl.CircleMarker(center=[station[1].latitude, station[1].longitude], color="Orangered", opacity=1, fillOpacity=1, radius=4, children=tooltip))

        # If the current objective is to select a starting position
        elif route_state == SELECT_END_POINT:
            # Set the starting location to the click location
            end_location = click_lat_lng
            # and make the objective to select another starting point
            route_state = SELECT_START_POINT

            # Find the closest bike stations to the clicked point where bikes can be returned
            bike_station_locations_return = route_finder.find_closest_bike_stations(end_location, __station_loader.get_station_states(), config, return_bikes=True)
            # Select the closest one as the bike station that will to be visited
            end_bike_station = bike_station_locations_return[0][1].location
            # Add estimated travel times to destination based on straight line distance to the popups of the closest bike stations
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

            # Add the routes from start to first bike station, first to second bike station, and second bike station to destination to the map
            route = dl.Polyline(positions=route_finder.get_shortest_route(__map, start_location, start_bike_station), color="hotpink", weight=5)
            children.append(route)
            route = dl.Polyline(positions=route_finder.get_shortest_route(__map, start_bike_station, end_bike_station), weight=5)
            children.append(route)
            route = dl.Polyline(positions=route_finder.get_shortest_route(__map, end_bike_station, end_location), color="hotpink", weight=5)
            children.append(route)

        # Allow the next callback function to execute
        mutex.release()
        return children
