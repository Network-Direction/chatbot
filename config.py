"""
Loads configuration from a YAML file into a dictionary

Usage:
    from config import GRAPH
    from config import GLOBAL

Authentication:
    N/A - Just needs to be able to read the YAML file

Restrictions:
    Requires the pyyaml module (pip install pyyaml)
    Requires config.yaml to be created and formatted correctly

To Do:
    None

Author:
    Luke Robertson, Richard Chapman - October 2022
"""


import sys
import yaml


# Define the dictionaries we're going to use
GRAPH = {}
GLOBAL = {}
SMTP = {}


# Open the YAML file, and store in the 'config' variable
try:
    f = open('config.yaml')
    try:
        config = yaml.load(f, Loader=yaml.FullLoader)
    except yaml.YAMLError as err:
        print('Error parsing config file, exiting')
        print('Check the YAML formatting at \
            https://yaml-online-parser.appspot.com/')
        print(err)
        sys.exit()
except Exception as e:
    print('Error opening the config file, exiting')
    print(e)
    sys.exit()


# Update our dictionaries with the config
GLOBAL = config['global']
GRAPH = config['graph']
SMTP = config['smtp']
PLUGINS = config['plugins']
