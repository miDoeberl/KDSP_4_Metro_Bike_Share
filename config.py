import configparser

def get_config():
    """
    Returns a dict containing the information from the config.ini file
    """
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config