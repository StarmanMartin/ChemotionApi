from chemotion_api.elements.abstract_element import AbstractElement
from chemotion_api.generic_segments import GenericSegments
from chemotion_api.utils import get_default_session_header





class GenericElement(AbstractElement):

    def __init__(self, json_data, generic_segments: GenericSegments, host_url, session):
        super().__init__(json_data, generic_segments, host_url, session)
        self._svg_file = json_data.get('sample_svg_file')

    def load_image(self):
        image_url = "{}/images/samples/{}".format(self._host_url, self._svg_file)
        res = self._session.get(image_url, headers=get_default_session_header())
        return res.text

    def _parse_properties(self) -> dict:
        return {}
