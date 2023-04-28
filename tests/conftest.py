import json
import logging

import pytest

DEFAULT_CONFIG = {
    "ELN_URL": "http://127.0.0.1:3000",
    "ELN_USER": "",
    "ELN_PASS": "",
}

CONFIG = {}

@pytest.fixture(scope="session", autouse=True)
def setup():
    global DEFAULT_CONFIG, CONFIG
    file="config.json"

    with open(file, "r") as jsonfile:
        data = json.load(jsonfile)

    for key, val in DEFAULT_CONFIG.items():
        CONFIG[key] = data.get(key, val)

    logging.info('Config:\n' + '\n'.join(["#\t%s=%s" % (key, val) for key, val in CONFIG.items()]))




@pytest.fixture(scope='session')
def config_login():
    return CONFIG