import map_loader
import map_plotter

if __name__ == "__main__":
    __map_loader = map_loader.MapLoader()
    __map_plotter = map_plotter.MapPlotter()

    map = __map_loader.get_map()
    __map_plotter.plot_map(map)