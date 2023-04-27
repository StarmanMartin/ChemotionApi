from chemotion_api.elements.abstract_element import AbstractElement
from chemotion_api.generic_segments import GenericSegments


class Sample(AbstractElement):

    def __init__(self, json_data, generic_segments: GenericSegments, host_url, session):
        super().__init__(json_data, generic_segments, host_url, session)

    def _parse_properties(self) -> dict:
        return {}
