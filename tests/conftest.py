import json
import logging
import uuid
from random import random

from chemotion_api import Instance
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

@pytest.fixture(scope='session')
def logged_in_instance():
    instance = Instance(CONFIG['ELN_URL']).test_connection().login(CONFIG['ELN_USER'], CONFIG['ELN_PASS'])
    yield instance
    root = instance.get_root_collection()
    for col_i in reversed(range(len(root.children))):
        if root.children[col_i].label != 'STATIC_TEST':
            root.children[col_i].delete()
    root.save()

@pytest.fixture()
def instance_with_test_samples(logged_in_instance):
    name = uuid.uuid4().__str__()
    root_col = logged_in_instance.get_root_collection()
    root_col.add_collection(name)
    root_col.save()
    main_collection = root_col.get_collection(name)
    sample_ids = []
    for smiles in ['B', 'N', 'C', 'CC', 'CN']:
        s = main_collection.new_sample()
        s.molecule = logged_in_instance.molecule().create_molecule_by_smiles(smiles)
        s.properties['target_amount']['value'] = random()
        s.save()
        sample_ids.append(s.id)

    yield {
        'instance': logged_in_instance,
        'name': name,
        'main_collection': main_collection,
        'sample_ids': sample_ids

    }