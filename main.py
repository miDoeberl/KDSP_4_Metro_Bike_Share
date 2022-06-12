import map_loader
import map_plotter_dash
import bike_stations
import web_view
import config

if __name__ == "__main__":
    # Get the configuration file
    __config = config.get_config()
    # Responsible for downloading/loading the city street map
    __map_loader = map_loader.MapLoader(__config)
    # Responsible for showing/interacting with the map plot
    __map_plotter = map_plotter_dash.MapPlotter(__config)
    # Responsible for loading the bike station statuses
    __bike_state_loader = bike_stations.StationStatusHandler(__config)
    # Responsible for opening a web browser window to show everything
    __web_view = web_view.WebBrowser()

    # Get the city map
    map_graph = __map_loader.get_map()
    # And show it on an interactive plot
    __map_plotter.plot_map(map_graph, __bike_state_loader, __web_view)