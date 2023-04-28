import re

from chemotion_api.elements.abstract_element import AbstractElement
from chemotion_api.generic_segments import GenericSegments
from chemotion_api.utils import get_default_session_header


class Molecule(dict):
    def __init__(self, data):
        super().__init__()
        self._data = data
        for (key, entry) in data.items():
            self[key] = entry

    @classmethod
    def load_molecule(self, host_url, session, inchikey):
        raise NotImplemented


class Sample(AbstractElement):

    def __init__(self, json_data, generic_segments: GenericSegments, host_url, session):
        super().__init__(json_data, generic_segments, host_url, session)
        self.molecule = Molecule(json_data.get('molecule'))
        self._svg_file = json_data.get('sample_svg_file')

    def load_image(self):
        image_url = "{}/images/samples/{}".format(self._host_url, self._svg_file)
        res = self._session.get(image_url, headers=get_default_session_header())
        if res.status_code != 200:
            raise ConnectionRefusedError('{} -> {}'.format(res.status_code, res.text))
        return res.text

    def _parse_properties(self) -> dict:
        melting_range = re.split('\.{2,3}', self.json_data.get('melting_point'))
        boiling_range = re.split('\.{2,3}', self.json_data.get('boiling_point'))
        return {
            'name': self.json_data.get('name'),
            'description': self.json_data.get('description'),
            'boiling_point_lowerbound': int(boiling_range[0]) if boiling_range[0].isdigit() else None,
            'boiling_point_upperbound': int(boiling_range[1]) if boiling_range[1].isdigit() else None,
            'melting_point_lowerbound': int(melting_range[0]) if melting_range[0].isdigit() else None,
            'melting_point_upperbound': int(melting_range[1]) if melting_range[1].isdigit() else None,
            'amount_value_in_g': self.json_data.get('real_amount_value'),
            'stereo': self.json_data.get('stereo'),
            'location': self.json_data.get('location'),
            'purity': self.json_data.get('purity'),
            'molarity': {'unit': format(self.json_data.get('molarity_unit')), 'value': self.json_data.get('molarity_value')}
        }

    def _clean_properties_data(self):
        self.json_data['name'] = self.properties.get('name')
        self.json_data['description'] = self.properties.get('description')
        self.json_data['boiling_point_lowerbound'] = self.properties.get('boiling_point_lowerbound')
        self.json_data['boiling_point_upperbound'] = self.properties.get('boiling_point_upperbound')
        self.json_data['melting_point_lowerbound'] = self.properties.get('melting_point_lowerbound')
        self.json_data['melting_point_upperbound'] = self.properties.get('melting_point_upperbound')
        self.json_data['real_amount_value'] = self.properties.get('amount_value_in_g')
        self.json_data['stereo'] = self.properties.get('stereo')
        self.json_data['location'] = self.properties.get('location')
        self.json_data['purity'] = self.properties.get('purity')
        self.json_data['molarity_unit'] = self.properties.get('molarity').get('unit')
        self.json_data['molarity_value'] = self.properties.get('molarity').get('value')

