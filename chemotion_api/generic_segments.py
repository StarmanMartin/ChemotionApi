from chemotion_api.utils import get_default_session_header
import uuid

class GenericSegments:
    def __init__(self,host_url, session):
        self._host_url = host_url
        self._session = session
        self._segments = None

    @property
    def all_classes(self):
        if self._segments is None:
            get_url = "{}/api/v1/segments/klasses.json".format(self._host_url)
            res = self._session.get(get_url, headers=get_default_session_header())
            if res.status_code != 200:
                raise ConnectionError('{} -> {}'.format(res.status_code, res.text))
            self._segments = res.json().get('klass', [])

        return self._segments

    @classmethod
    def new_session(cls, base_segment: dict) -> dict:
        a = {
            'segment_klass_id': base_segment['id'],
            'klassType': 'Segment',
            'is_new': True,
            'id': uuid.uuid4().__str__()
        }
        a['properties'] = base_segment.get('properties_release', {}).copy()

        return a