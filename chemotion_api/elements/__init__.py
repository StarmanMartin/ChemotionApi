import json

from chemotion_api.elements.abstract_element import AbstractElement
from chemotion_api.elements.generic_element import GenericElement
from chemotion_api.elements.sample import Sample
from chemotion_api.elements.reaction import Reaction
from chemotion_api.elements.wellplate import Wellplate
from chemotion_api.generic_segments import GenericSegments
from chemotion_api.utils import get_default_session_header
import requests

class ElementSet(list):
    def __init__(self, host_url: str, session: requests.Session, element_type: dict, collection_id: int = None):
        super().__init__()
        self._host_url = host_url
        self._session = session
        self._element_type = element_type
        self._collection_id = collection_id
        self._page = 1
        self.max_page = 1
        self._per_page = 10

    @property
    def page(self):
        return self._page


    @page.setter
    def page(self, page: int):
        self._set_page(page)
    def _set_page(self, page: int) -> bool:
        if page > 0 and page <= self.max_page:
            self._page = page
            self.load_elements()
            return True
        return False

    def iter_pages(self):
        self._page = 0
        while self._set_page(self.page + 1):
            yield self.next_page()

    def next_page(self):
        self._set_page(self.page + 1)
        return self
    def prev_page(self):
        self._set_page(self.page - 1)
        return self

    def load_elements(self, per_page=None):
        if per_page is not None:
            self._per_page = per_page
        if self._collection_id is None:
            raise ValueError('load_elements only works if collection_id is set!')

        segments = GenericSegments(self._host_url, self._session)
        payload = {'collection_id': self._collection_id,
                   'page': self.page,
                   'per_page': self._per_page,
                   'filter_created_at': False,
                   'product_only': False,
                   'el_type': self._element_type['name']}
        res = self._session.get(self._get_url() + '.json',
                                headers=get_default_session_header(),
                                data=payload)
        if res.status_code != 200:
            raise ConnectionError('{} -> {}'.format(res.status_code, res.text))

        try:
            self.max_page = int(res.headers.get('X-Total-Pages', 1))
        except:
            pass
        self.clear()
        elements = res.json().get(self._get_result_key() + 's', [])
        for json_data in elements:
            self.append(self._get_element_class()(segments, self._host_url, self._session, json_data=json_data))

    def load_element(self, id: int) -> AbstractElement:
        segments = GenericSegments(self._host_url, self._session)
        s = self._get_element_class()(segments, self._host_url, self._session, id=id, element_type=self._element_type['name'])
        self.append(s)
        return s

    def new_element(self, json_data: dict) -> AbstractElement:
        segments = GenericSegments(self._host_url, self._session)
        s = self._get_element_class()(segments, self._host_url, self._session, json_data=json_data)
        self.append(s)
        return s

    def _get_element_class(self) -> AbstractElement.__class__:
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

    def _get_result_key(self):
        return AbstractElement.get_response_key(self._element_type['name'])

    def _get_url(self):
        return AbstractElement.get_url(self._element_type['name'], self._host_url)
