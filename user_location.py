import geocoder


class UserLocationInfo:
    """
    Gets and stores the current user location
    This class is currently unused, as the user can just click on where he wants to start
    """

    def __init__(self):
        self._location = None
        self._manual_position_set = False

    def _get_ip_location(self):
        """
        Estimate the user location based on the ip address
        """
        location = geocoder.ip("me")
        if not location.error and not self._manual_position_set:
            self._location = location.latlng

        return self._location

    def set_location(self, latitude, longitude):
        """
        Manually set the user location
        """
        self._location = [latitude, longitude]
        self._manual_position_set = True

    def get_location(self):
        """
        Return the ip address location estimate, or the manually set one if it is set 
        """
        if self._location is None:
            self._get_ip_location()

        return self._location
