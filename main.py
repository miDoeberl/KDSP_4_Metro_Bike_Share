import map_loader
import map_plotter_folium
import map_plotter_dash
import bike_stations
import config

if __name__ == "__main__":
    __config = config.get_config()
    __map_loader = map_loader.MapLoader(__config)
    __map_plotter = map_plotter_dash.MapPlotter(__config)
    __bike_state_loader = bike_stations.StationStatusHandler()

    map_graph = __map_loader.get_map()
    __map_plotter.plot_map(map_graph, __bike_state_loader)