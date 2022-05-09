import osmnx as ox
import folium
import webbrowser
import pathlib
import os
from folium.plugins import MousePosition


class MapPlotter:

    def __init__(self):
        self.cache_directory = "data"
        self.cache_dir_path = pathlib.Path(__file__).parent / self.cache_directory

    def plot_map(self, map, stations):
        orig = list(map)[0]
        dest = list(map)[-1]
        route = ox.shortest_path(map, orig, dest)

        self.folium_map = ox.plot_route_folium(map, route)
        self.add_tile_layers()

        formatter = "function(num) {return L.Util.formatNum(num, 3) + ' º ';};"
        MousePosition(
        position="topright",
        separator=" | ",
        empty_string="NaN",
        lng_first=True,
        num_digits=20,
        prefix="Coordinates:",
        lat_formatter=formatter,
        lng_formatter=formatter,
        ).add_to(self.folium_map)


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

            iframe = folium.IFrame(popup_html)
            popup = folium.Popup(iframe, min_width=250, max_width=500)
            folium.Marker(station[1]["location"], popup=popup).add_to(self.folium_map)
            
            # Show number of bikes on top of marker
            # folium.Marker(station[1]["location"], icon=folium.features.DivIcon(
            # icon_size=(150,36),
            # icon_anchor=(7,40),
            # html='<div style="font-size: 18pt; color : black">' + str(station[1]["bikesAvailable"]) + '</div>',
            # )).add_to(self.folium_map)


        if not os.path.isdir(self.cache_dir_path):
            os.mkdir(self.cache_dir_path)

        self.folium_map.save(str(self.cache_dir_path / "folium.html"))
        webbrowser.open_new(str(self.cache_dir_path / "folium.html"))

    def add_tile_layers(self):
        folium.TileLayer("openstreetmap").add_to(self.folium_map)
        folium.TileLayer('stamenterrain').add_to(self.folium_map)
        folium.TileLayer('stamentoner').add_to(self.folium_map)
        folium.TileLayer('stamenwatercolor').add_to(self.folium_map)
        folium.TileLayer('cartodbpositron').add_to(self.folium_map)
        folium.TileLayer('cartodbdark_matter').add_to(self.folium_map)
        folium.LayerControl().add_to(self.folium_map)
