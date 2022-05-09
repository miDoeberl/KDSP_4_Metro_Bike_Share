import map_loader
import map_plotter_folium
import map_plotter_dash
import bike_stations

if __name__ == "__main__":
    __map_loader = map_loader.MapLoader()
    __map_plotter = map_plotter_dash.MapPlotter()
    __bike_state_loader = bike_stations.StationStatusHandler()

    map_graph = __map_loader.get_map()
    stations = __bike_state_loader.get_station_states()
    __map_plotter.plot_map(map_graph, stations)