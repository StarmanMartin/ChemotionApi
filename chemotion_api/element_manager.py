import json
import uuid

import requests

from chemotion_api.elements.sample import MoleculeManager
from chemotion_api.utils import get_default_session_header
import os.path
from chemotion_api.user import User

from chemotion_api.elements.empty_elements import init_container


class ElementManager:

    def __init__(self, host_url: str, session: requests.Session):
        self._session = session
        self._host_url = host_url
        self._all_classes = None

    @property
    def all_classes(self):
        if self._all_classes is None:
            self._all_classes = self.get_all_classes()
        return self._all_classes

    def get_all_classes(self):
        get_url = "{}/api/v1/generic_elements/klasses.json".format(self._host_url)
        res = self._session.get(get_url, headers=get_default_session_header())
        if res.status_code != 200:
            raise ConnectionError('Counld not get the genetic elements')
        all_classes = {}
        for x in res.json()['klass']:
            all_classes[x['name']] = x
        return all_classes

    def _init_container(self):
        return init_container()


    def _get_user(self):
        u = User(self._host_url, self._session)
        u.load()
        return u


    def _get_short_label(self, type_name):
        u = self._get_user()
        if type_name == 'sample':
            return '{}-{}'.format(u.initials, u.counters[type_name + 's'])
        if type_name == 'reaction':
            return '{}-R{}'.format(u.initials, u.counters[type_name + 's'])
        return '{}-R{}'.format(type_name, u.counters[type_name + 's'])

    def build_new(self, type_name, collection_id):
        class_obj = self.all_classes[type_name]
        data = {}
        if not class_obj['is_generic']:
            json_path = os.path.join(os.path.dirname(__file__), 'elements/empty_elements', type_name + '.json')
            if os.path.exists(json_path):
                with open(json_path, 'r') as f:
                    data = json.loads(f.read())
            if type_name == 'wellplate':
                data['wells'] = []
                for y in range(1, 9):
                    for x in range(1, 13):
                        data['wells'].append({
                            "id": uuid.uuid4().__str__(),
                            "is_new": True,
                            "position": {
                                "x": x,
                                "y": y
                            }

                        })
        else:
            raise NotImplementedError




        data['container'] = self._init_container()
        data['collection_id'] = collection_id
        data['short_label'] = self._get_short_label(type_name)
        return data
    def build_solvent_sample(self, name, collection_id):
        solvent_info = self.get_solvent_list().get(name)
        if solvent_info is None:
            raise KeyError('Solver: "{}" is not available. Run instance.get_solvent_list() to see all valid solver names'.format(name))
        sample_data = self.build_new('sample', collection_id)

        mol = MoleculeManager(self._host_url, self._session).create_molecule_by_smiles(solvent_info['smiles'])

        sample_data['molecule'] = mol
        sample_data['density'] = solvent_info['density']
        sample_data['name'] = 'Solvent: {}'.format(name)
        return sample_data

    @classmethod
    def get_solvent_list(cls):
        json_path = os.path.join(os.path.dirname(__file__), 'elements/empty_elements/solvents.json')
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                return json.loads(f.read())
