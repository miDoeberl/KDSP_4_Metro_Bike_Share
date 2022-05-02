from datetime import datetime
import osmnx as ox
import pathlib
import os

from sklearn.utils import shuffle

# ox.config(use_cache=True, log_console=True)
# G = ox.graph_from_place('Schmidmühlen, BY, Germany', network_type='drive')
# print(G.__dir__())
# orig = list(G)[0]
# dest = list(G)[-1]
# route = ox.shortest_path(G, orig, dest)
# fig, ax = ox.plot_graph_route(G, route, route_linewidth=6, node_size=0, bgcolor='k')


class MapLoader():

    def __init__(self):
        ox.config(use_cache=True, log_console=True)
        self.cache_directory = "data"
        self.cache_dir_path = pathlib.Path(__file__).parent / self.cache_directory
        self.date_str_format = "%m-%d-%Y-%H-%M-%S"
        self.map_update_time = 86400  # [s]

        self.place = "Los Angeles, CA, USA"
        #self.place = "Schmidmühlen, BY, Germany"
        self.network_type = "drive"
        self.network_graph = None

    def get_map(self):
        # Check if a map was already loaded
        if self.network_graph is None:
            # If not, check if there is a cached map
            self.network_graph = self._possibly_get_cached_map()
            # If not, load it from the overpass api and store it for later
            if self.network_graph is None:
                self._load_map_from_overpass()
                self._cache_map()

        return self.network_graph

    def _load_map_from_overpass(self):
        self.network_graph = ox.graph_from_place(self.place, network_type=self.network_type)

    def _cache_map(self):
        if not os.path.isdir(self.cache_dir_path):
            os.mkdir(self.cache_dir_path)

        if self.network_graph is not None:
            file_path = self.cache_dir_path / ("map_cache_" + datetime.now().strftime(self.date_str_format) + ".graphml")
            ox.save_graphml(self.network_graph, file_path)

    def _possibly_get_cached_map(self):
        if not os.path.isdir(self.cache_dir_path):
            return None

        cached_maps = os.listdir(self.cache_dir_path)

        closest_filename = None
        closest_date = datetime.fromordinal(1)
        for filename in cached_maps:
            date_str = filename.replace("map_cache_", "")
            date_str = date_str.replace(".graphml", "")
            try:
                date = datetime.strptime(date_str, self.date_str_format)
            except ValueError:
                # If the filename does not follow the naming convention of map_cache_<date_format>.osm, ignore the file
                continue

            if date > closest_date:
                closest_date = date
                closest_filename = filename

        map = None
        if closest_filename is not None and (datetime.now() - closest_date).seconds <= self.map_update_time:
            map = ox.load_graphml(str(self.cache_dir_path / closest_filename))

        return map


if __name__ == "__main__":
    loader = MapLoader()
    test1 = loader.get_map()
    print("loaded first map!")
    test2 = loader.get_map()
    print("loaded second map!")
    # print("")
