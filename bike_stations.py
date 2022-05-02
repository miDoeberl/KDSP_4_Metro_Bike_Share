import json
import urllib.request
from datetime import datetime


class StationStatusHandler:

    def __init__(self):
        self._url = "https://bikeshare.metro.net/stations/json/"
        self._station_states = None
        self._last_update = datetime.fromordinal(1)
        self._station_update_time = 60

    def _load_station_states(self):
        """
        Calls the bikeshare.metro json api to get the current station statuses
        """
        req = urllib.request.Request(self._url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as url:
            data = json.loads(url.read().decode())
            self._station_states = data['features']

    def get_station_states(self, force_refresh=False):
        """
        Returns station statuses that are always younger than `self.station_update_time` seconds
        """
        current_time = datetime.now()
        if (current_time - self._last_update).seconds >= self._station_update_time \
                or self._station_states is None \
                or force_refresh:
            self._last_update = current_time
            self._station_states = self._load_station_states()

        return self._station_states
