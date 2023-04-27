import json
import logging

DEFAULT_CONFIG = {
    "ELN_URL": "http://127.0.0.1:3000",
    "ELN_USER": "",
    "ELN_PASS": "",
    "ELN_ELEMENT": "",
    "ELN_ELEMENT_SELECT_FIELD": "id",
    "ELN_COLLECTION_NAME": "all"
}

CONFIG = {}


def load_config(file="config.json"):
    global DEFAULT_CONFIG, CONFIG
    with open(file, "r") as jsonfile:
        data = json.load(jsonfile)

    for key, val in DEFAULT_CONFIG.items():
        CONFIG[key] = data.get(key, val)

    logging.info('Config:\n' + '\n'.join(["#\t%s=%s" % (key, val) for key, val in CONFIG.items()]))