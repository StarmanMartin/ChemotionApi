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
        return res.text

    def _parse_properties(self) -> dict:
        return {
            'name': self.json_data.get('name'),
            'description': self.json_data.get('description'),
            'boiling_point': self.json_data.get('boiling_point'),
            'melting_point': self.json_data.get('melting_point'),
            'amount_value_in_g': self.json_data.get('real_amount_value'),
            'stereo': self.json_data.get('stereo'),
            'location': self.json_data.get('location'),
            'purity': self.json_data.get('purity'),
            'molarity_in_{}'.format(self.json_data.get('molarity_unit')): self.json_data.get('real_amount_value'),
        }
