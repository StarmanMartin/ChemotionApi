from __future__ import print_function, unicode_literals
import requests
import json


class ApiFetcher:
    _session = None
    token = None

    ELN_URL = None
    ELN_USER = None
    ELN_PASS = None
    ELN_ELEMENT = None
    ELN_ELEMENT_SELECT_FIELD = None
    ELN_COLLECTION_NAME = None

    def __init__(self, ELN_URL, ELN_USER, ELN_PASS, ELN_ELEMENT, ELN_ELEMENT_SELECT_FIELD, ELN_COLLECTION_NAME):
        self.ELN_URL = ELN_URL
        self.ELN_USER = ELN_USER
        self.ELN_PASS = ELN_PASS
        self.ELN_ELEMENT = ELN_ELEMENT
        self.ELN_ELEMENT_SELECT_FIELD = ELN_ELEMENT_SELECT_FIELD
        self.ELN_COLLECTION_NAME = ELN_COLLECTION_NAME

    @property
    def session(self):
        if self._session is not None:
            return self._session

        headers = {'User-Agent': 'Mozilla/5.0'}
        payload = {'user[login]': self.ELN_USER, 'user[password]': self.ELN_PASS}

        session = requests.Session()
        res = session.post('%s/users/sign_in' % self.ELN_URL.removesuffix('/'),
                           headers=headers,
                           data=payload)

        if res.status_code == 200:
            self._session = session
            return self._session
        raise PermissionError('Could not login!!')

    def get_collections(self):

        headers = {'User-Agent': 'Mozilla/5.0'}
        # res = self.session.get('%s/api/v1/syncCollections/sync_remote_roots' % self.ELN_URL.removesuffix('/'),
        res = self.session.get('%s/api/v1/collections/roots.json' % self.ELN_URL.removesuffix('/'),
                               headers=headers,
                               data={})
        collections = json.loads(res.content)
        filtered_collections = []
        for col in collections['collections']:
            filtered_collections += self._filter_collection(col)

        return filtered_collections

    def get_elements(self, collection_list):
        print('Enter element %s:' % self.ELN_ELEMENT_SELECT_FIELD)
        elm_name = str(input())

        headers = {'User-Agent': 'Mozilla/5.0'}

        for col in collection_list:
            page = 1
            max_page = 1
            while page <= max_page :
                payload = {'collection_id': col['id'],
                           'page': page,
                           'per_page': 100,
                           'filter_created_at': False,
                           'product_only': False,
                           'el_type': self.ELN_ELEMENT}
                res = self.session.get('%s/api/v1/generic_elements.json' % self.ELN_URL.removesuffix('/'),
                                       headers=headers,
                                       data=payload)
                try:
                    max_page = int(res.headers.get('X-Total-Pages', 1))
                except:
                    pass

                elements = json.loads(res.content).get('generic_elements', [])
                try:
                    idx = [str(elem.get(self.ELN_ELEMENT_SELECT_FIELD, '')) for elem in elements].index(elm_name)
                    return elements[idx]
                except:
                    page += 1

        return None

