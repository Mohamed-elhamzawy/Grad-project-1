import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.json')

def load_config():
    if not os.path.exists(CONFIG_PATH):
        # Return default config if the file doesn't exist
        return {
            "TEMP_THRESHOLD": 27,
            "HUM_THRESHOLD": 80,
            "SOIL_MOISTURE_THRESHOLD": 4000
        }
    with open(CONFIG_PATH, 'r') as file:
        return json.load(file)

def save_config(config):
    with open(CONFIG_PATH, 'w') as file:
        json.dump(config, file, indent=4)
