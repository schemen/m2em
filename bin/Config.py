
import configparser
import os

def load_config(location='config.ini'):
    config = {}
    config_reader = configparser.ConfigParser()
    config_reader.optionxform = str
    config_reader.read(location)
    
    for key, value in config_reader.items("CONFIG"):
        if key in os.environ:
            config[key] = os.environ[key]
        else:
            config[key] = value
    
    return config
