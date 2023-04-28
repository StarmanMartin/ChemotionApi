import requests
from typing import TypeVar

from chemotion_api.collection import RootCollection
from chemotion_api.generic_elements import GenericElements
from chemotion_api.user import User
from chemotion_api.utils import get_default_session_header
from  requests.exceptions import ConnectionError

TInstance = TypeVar("TInstance", bound="Instance")
class Instance:
    def __init__(self, host_url: str):
        self.host_url = host_url.removesuffix('/')
        self._session = requests.Session()
        self._all_elements = None

    def test_connection(self) -> TInstance:
        ping_url = "{}/api/v1/public/ping".format(self.host_url)
        res = requests.get(url=ping_url)
        if res.status_code != 204:
            raise ConnectionError('Could not ping the Chemotion instance: {}'.format(self.host_url))
        return self

    def login(self, user: str, password: str) -> TInstance:
        headers = get_default_session_header()
        payload = {'user[login]': user, 'user[password]': password}
        login_url = "{}/users/sign_in".format(self.host_url)

        res = self._session.post(login_url,
                           headers=headers,
                           data=payload)

        if res.status_code == 200 and not res.url.endswith('sign_in'):
            return self
        elif res.status_code != 200:
            raise ConnectionError('{} -> {}'.format(res.status_code, res.text))
        raise PermissionError('Could not login!!')

    def get_user(self) -> User:
        u = User(self.host_url, self._session)
        u.load()
        return u

    def get_all_collections(self):
        root_col = RootCollection(self.host_url, self._session)
        root_col.set_element_classes(self.all_element_classes)
        root_col.load_collection()
        root_col.load_sync_collection()
        return root_col
    @property
    def all_element_classes(self) -> dict[str: str]:
        if self._all_elements is None:
            self._all_elements = GenericElements.get_all_classes(self.host_url, self._session)
        return self._all_elements
