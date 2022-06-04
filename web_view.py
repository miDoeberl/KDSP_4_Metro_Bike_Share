import os
import webbrowser
from threading import Timer

class WebBrowser:
    
    def __init__(self):
        pass

    def open_map_site(self, delay=0):
        # If a delay in opening the site is wanted, call this function again in x seconds
        if delay != 0:
            t = Timer(delay, self.open_map_site, [0])
            t.start()
        else:
            # Redirect stdout stream to /dev/null because the webbrowser module keeps
            # printing the zen of python on every page load....
            savout = os.dup(1)
            os.close(1)
            os.open(os.devnull, os.O_RDWR)
            webbrowser.open_new("http://127.0.0.1:8050")
            os.dup2(savout, 1)

if __name__ == "__main__":
    browser = WebBrowser()
    browser.open_map_site()