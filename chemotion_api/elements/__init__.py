import json

from chemotion_api.elements.abstract_element import AbstractElement
from chemotion_api.elements.generic_element import GenericElement
from chemotion_api.elements.reaction import Reaction
from chemotion_api.elements.sample import Sample
from chemotion_api.elements.wellplate import Wellplate
from chemotion_api.generic_segments import GenericSegments
from chemotion_api.utils import get_default_session_header
import requests

class ElementSet(list):
    def __init__(self, host_url: str, session: requests.Session, element_type: dict, collection_id: int):
        super().__init__()
        self._host_url = host_url
        self._session = session
        self._element_type = element_type
        self._collection_id = collection_id

    def load_elements(self, get_elements=50):
        page = 1
        max_page = 1
        segments = GenericSegments(self._host_url, self._session)
        while page <= max_page:
            payload = {'collection_id': self._collection_id,
                       'page': page,
                       'per_page': get_elements,
                       'filter_created_at': False,
                       'product_only': False,
                       'el_type': self._element_type['name']}
            res = self._session.get(self._get_url() + '.json',
                                    headers=get_default_session_header(),
                                    data=payload)
            try:
                max_page = int(res.headers.get('X-Total-Pages', 1))
            except:
                pass
            page += 1
            elements = res.json().get(self._get_result_key() + 's', [])
            for element in elements:
                self.append(Sample(element, segments, self._host_url, self._session))

    def load_element(self, id=50) -> AbstractElement:
        segments = GenericSegments(self._host_url, self._session)
        payload = {}
        res = self._session.get("{}/{}.json".format(self._get_url(), id),
                                headers=get_default_session_header(),
                                data=payload)

        element = res.json()[self._get_result_key()]
        s = Sample(element, segments, self._host_url, self._session)
        self.append(s)
        return s

    def _get_result_key(self):
        if self._element_type['is_generic']:
            return 'generic_element'
        elif self._element_type['name'] == 'sample':
            return 'sample'
        elif self._element_type['name'] == 'reaction':
            return 'reaction'
        elif self._element_type['name'] == 'wellplate':
            return 'wellplate'
        elif self._element_type['name'] == 'research_plan':
            return 'research_plan'

        raise TypeError('Generic type "{}" cannot be found'.format(self._element_type['name']))

    def _get_element_class(self):
        if self._element_type['is_generic']:
            return GenericElement
        elif self._element_type['name'] == 'sample':
            return Sample
        elif self._element_type['name'] == 'reaction':
            return Reaction
        elif self._element_type['name'] == 'wellplate':
            return Wellplate
        elif self._element_type['name'] == 'research_plan':
            return 'research_plan'

        raise TypeError('Generic type "{}" cannot be found'.format(self._element_type['name']))

    def _get_url(self):
        if self._element_type['is_generic']:
            return '%s/api/v1/generic_elements' % self._host_url
        elif self._element_type['name'] == 'sample':
            return '%s/api/v1/samples' % self._host_url
        elif self._element_type['name'] == 'reactions':
            return '%s/api/v1/reactions' % self._host_url
        elif self._element_type['name'] == 'wellplates':
            return '%s/api/v1/wellplates' % self._host_url
        elif self._element_type['name'] == 'research_plans':
            return '%s/api/v1/research_plans' % self._host_url

        raise TypeError('Generic type "{}" cannot be found'.format(self._element_type['name']))
