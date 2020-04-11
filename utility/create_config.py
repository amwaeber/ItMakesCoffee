import os
from configparser import ConfigParser


def write_config():
    project_path = os.path.join(os.path.dirname(__file__), '..')
    config_path = os.path.join(project_path, 'config.ini')

    config = ConfigParser()

    config['globals'] = {'progname': 'ItMakesCoffee',
                         'progversion': '2020.04.11.01'
                         }

    config['paths'] = {'icons': os.path.join(project_path, 'icons')
                       }

    with open(config_path, 'w') as f:
        config.write(f)
