from datetime import datetime
import osmnx as ox
import pathlib
import os
import pickle

class MapLoader():
    """
    Downloads the city street maps and caches them for later use
    """

    def __init__(self, __config):
        ox.config(use_cache=False, log_console=True)
        # relative directory where the map caches will be saved
        self.cache_directory = "data"
        # absolute path where map caches will be saved
        self.cache_dir_path = pathlib.Path(__file__).parent / self.cache_directory
        # Time format used in the cache file names
        self.date_str_format = "%m-%d-%Y-%H-%M-%S"
        # Time the map cache is valid in seconds
        self.map_update_time = int(__config["MAP"]["updateTime"])

        # City the map should be from
        self.place = __config["MAP"]["place"]
        # If the street map should consist of drivable/bikeable/walkable routes
        self.network_type = "bike" # "drive", "bike", "walk"
        # Placeholder object for the map
        self.network_graph = None

    def get_map(self):
        """
        Returns a city street map in networkx.diGraph format
        """
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
        """
        Downloads the city street map from the osmnx api
        This can take very long as the map sizes can be multiple hundred MB
        """
        self.network_graph = ox.graph_from_place(self.place, network_type=self.network_type, simplify=False)

    def _cache_map(self):
        """
        Saves the map in a pickle object so it can be loaded in at a later time
        """
        # Check if the cache directory exists, if not create it
        if not os.path.isdir(self.cache_dir_path):
            os.mkdir(self.cache_dir_path)

        # If a map is downloaded
        if self.network_graph is not None:
            # Create a valid file path
            location_prefix = self.place.replace(" ", "").replace(",", "_")
            file_path = self.cache_dir_path / ("map_cache_" + location_prefix + "_" +
                                               datetime.now().strftime(self.date_str_format) + ".pickle")
            
            # The osmnx api provides functions to save/load maps, but they are not used here because they are very slow
            #ox.save_graphml(self.network_graph, file_path)
            
            # Save the map in a pickle object
            with open(file_path, "wb") as file:
                pickle.dump(self.network_graph, file)

    def _possibly_get_cached_map(self):
        """
        Checks if previously cached maps exists and returns the newest one
        """

        # If the cache directory does not exist, there are no cached maps
        if not os.path.isdir(self.cache_dir_path):
            return None

        # Get all filenames in the cache directory
        cached_maps = os.listdir(self.cache_dir_path)

        closest_filename = None
        closest_date = datetime.fromordinal(1)
        # Check all files in the cache directory
        for filename in cached_maps:
            # Get the date from their filename
            date_str = filename.replace("map_cache_", "")
            date_str = date_str.replace(self.place.replace(" ", "").replace(",", "_") + "_", "")
            date_str = date_str.replace(".pickle", "")

            # Convert it to a date object
            try:
                date = datetime.strptime(date_str, self.date_str_format)
            except ValueError:
                # If the filename does not follow the naming convention of map_cache_<date_format>.osm, ignore the file
                # as it is not a map cache
                continue

            # If it is the newest cache, save the filename
            if date > closest_date:
                closest_date = date
                closest_filename = filename

        map = None
        # If the cache is younger than the cache invalidation time
        if closest_filename is not None and (datetime.now() - closest_date).seconds <= self.map_update_time:
            
            # osmnx load/save functions are not used here because they are very slow (>20s for loading a map of LA)
            # map = ox.load_graphml(str(self.cache_dir_path / closest_filename))
            
            # Load it
            with open(str(self.cache_dir_path / closest_filename), "rb") as file:
                map = pickle.load(file)

        return map


if __name__ == "__main__":
    loader = MapLoader()
    test1 = loader.get_map()
    print("loaded first map!")
    test2 = loader.get_map()
    print("loaded second map!")
    # print("")
