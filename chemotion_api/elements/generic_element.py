from chemotion_api.elements.abstract_element import AbstractElement
from chemotion_api.generic_segments import GenericSegments
from chemotion_api.utils import get_default_session_header





class GenericElement(AbstractElement):

    def _set_json_data(self, json_data):
        super()._set_json_data(json_data)
        self._svg_file = json_data.get('sample_svg_file')

    def load_image(self):
        image_url = "{}/images/samples/{}".format(self._host_url, self._svg_file)
        res = self._session.get(image_url, headers=get_default_session_header())
        return res.text

    def _parse_properties(self) -> dict:
        return {}
