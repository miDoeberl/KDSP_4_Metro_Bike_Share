import geocoder


class UserLocationInfo:

    def __init__(self):
        self._location = None
        self._manual_position_set = False

    def _get_ip_location(self):
        location = geocoder.ip("me")
        if not location.error and not self._manual_position_set:
            self._location = location.latlng

        return self._location

    def set_location(self, latitude, longitude):
        self._location = [latitude, longitude]
        self._manual_position_set = True

    def get_location(self):
        if self._location is None:
            self._get_ip_location()

        return self._location
