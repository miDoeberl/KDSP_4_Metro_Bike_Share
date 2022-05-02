import osmnx as ox
import folium
import webbrowser
import pathlib
import os

class MapPlotter:

    def __init__(self):
        self.cache_directory = "data"
        self.cache_dir_path = pathlib.Path(__file__).parent / self.cache_directory

    def plot_map(self, map):
        orig = list(map)[0]
        dest = list(map)[-1]
        route = ox.shortest_path(map, orig, dest)
        
        self.folium_map = ox.plot_route_folium(map, route)
        self.add_tile_layers()

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
