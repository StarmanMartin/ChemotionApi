import typing

import requests
from typing import TypeVar

from chemotion_api.collection import RootCollection
from chemotion_api.element_manager import ElementManager
from chemotion_api.user import User
from chemotion_api.utils import get_default_session_header
from  requests.exceptions import ConnectionError

from chemotion_api.elements import AbstractElement, ElementSet, Wellplate, Sample, Reaction
from chemotion_api.elements.sample import MoleculeManager

TInstance = TypeVar("TInstance", bound="Instance")
class Instance:
    def __init__(self, host_url: str):
        self.host_url = host_url.removesuffix('/')
        self._session = requests.Session()
        self._root_col = None
        self.element_manager = ElementManager(host_url, self._session)

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

    def get_root_collection(self, reload=True) -> RootCollection:
        if reload or self._root_col is None:
            self._root_col = RootCollection(self.host_url, self._session)
            self._root_col.set_element_manager(self.element_manager)
            self._root_col.load_collection()
            self._root_col.load_sync_collection()
        return self._root_col

    @property
    def all_element_classes(self) -> dict[str: str]:
        return self.element_manager.all_classes

    def get_reaction(self, id) -> Reaction:
        e = ElementSet(self.host_url, self._session, self.all_element_classes.get('reaction'))
        return typing.cast(Reaction, e.load_element(id))

    def get_wellplate(self, id) -> Wellplate:
        e = ElementSet(self.host_url, self._session, self.all_element_classes.get('wellplate'))
        return typing.cast(Wellplate, e.load_element(id))

    def get_research_plan(self, id) -> AbstractElement:
        e = ElementSet(self.host_url, self._session, self.all_element_classes.get('research_plan'))
        return e.load_element(id)

    def get_sample(self, id) -> Sample:
        e = ElementSet(self.host_url, self._session, self.all_element_classes.get('sample'))
        return typing.cast(Sample, e.load_element(id))

    def molecule(self):
        return MoleculeManager(self.host_url, self._session)

    def get_solvent_list(self):
        return list(ElementManager.get_solvent_list().keys())
