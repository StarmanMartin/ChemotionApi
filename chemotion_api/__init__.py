import typing

from typing import TypeVar

from chemotion_api.collection import RootCollection
from chemotion_api.element_manager import ElementManager
from chemotion_api.user import User
from requests.exceptions import ConnectionError

from chemotion_api.elements import ElementSet, Wellplate, Sample, Reaction, GenericElement, ResearchPlan
from chemotion_api.elements.sample import MoleculeManager
from chemotion_api.connection import Connection

TInstance = TypeVar("TInstance", bound="Instance")


class Instance:
    """ The instance object is the core object of the Chemotion API. In order for the API to work,
    a connection to a Chmotion (server-)iEBUG http://193.196.38.77:80 "GET /api/v1/collections/roots.json HTTP/1.1" 401 28
FAILED                                                                   [ 16%]
test_collection.py:63 (test_get_create_collection)
logged_in_instance = <chemotion_api.Instance object at 0x7f3cc1a05e40>

    def test_get_creanstance must first be established.
    an Instance object manges such a connection. To initializes an instance it needs
     the host URL of the chemotion server as a string.

    :param host_url: URL for the new :class:`Request` object

    Usage::

    >>> from chemotion_api import Instance
    >>> from  requests.exceptions import ConnectionError as CE
    >>> import logging
    >>> try:
    >>>     s = Instance('http(d)://xxx.xxx.xxx').test_connection().login('<USER>', "<PASSWORD>")
    >>> except CE as e:
    >>>     logging.error(f"A connection to Chemotion ({s.host_url}) cannot be established")


    """

    def __init__(self, host_url: str):
        self._con = Connection(host_url)
        self._root_col = None
        self.element_manager = ElementManager(self._con)

    @property
    def host_url(self):
        return self._con.host_url

    def test_connection(self) -> TInstance:
        """
        This test_connection methode simply test if the connection to a chemotion instance can be established.
        The instance does not need to be logged in to use this methode.

        :return: the instance self

        :raises ConnectionError (requests.exceptions.ConnectionError) if the connection cannot be established.
        """
        ping_url = "/api/v1/public/ping"
        res = self._con.get(url_path=ping_url)
        if res.status_code != 204:
            raise ConnectionError('Could not ping the Chemotion instance: {}'.format(self.host_url))
        return self

    def login(self, user: str, password: str) -> TInstance:
        """
        This login methode allows you to log in to a chemotion instance.
        Hence, you need a valid chemotion user (abbreviation name or e-mail)

        :param user: abbreviation name or e-mail of a chemotion user
        :param password: The password of the user

        :return: the instance self

        :raise ConnectionError (requests.exceptions.ConnectionError) if the logging was not successful.
        """

        payload = {'user[login]': user, 'user[password]': password}
        login_url = "/users/sign_in"

        res = self._con.post(url_path=login_url,
                             headers=Connection.get_default_session_header(),
                             data=payload)

        if res.status_code == 200 and not res.url.endswith('sign_in'):
            return self
        elif res.status_code != 200:
            raise ConnectionError('{} -> {}'.format(res.status_code, res.text))
        raise PermissionError('Could not login!!')

    def get_user(self) -> User:
        """
        This get_user methode initializes a new User object. The user object allows you to fetch and edit user data.

        :return: a new User instance

        :raise PermissionError: if the userdata cannot be fetched. Make sure that you are logged in.
        """
        u = User(self._con)
        u.load()
        return u

    def get_root_collection(self, reload=True) -> RootCollection:
        if reload or self._root_col is None:
            self._root_col = RootCollection(self._con)
            self._root_col.set_element_manager(self.element_manager)
            self._root_col.load_collection()
            self._root_col.load_sync_collection()
        return self._root_col

    @property
    def all_element_classes(self) -> dict[str, dict[str, str]]:
        """
        This all_element_classes fetches all information about all elements such as
         Sample, Reaction, Wellplate and Research plan and all generic elements

        :return: a dictionary which contains all information about all elements

        :raise RequestException: (requests.exceptions.RequestException) if the information cannot be fetched. Make sure that your connection is active and you are logged in.
        """
        return self.element_manager.all_classes

    def get_reaction(self, id: int) -> Reaction:
        """
        Fetches data of one Reaction object from the Chemotion server.
        It automatically parses the data into a Python-Reaction-Object. However, you need to know the correct internally used ID
        of the Reaction to be able to fetch it. Other methods to get Elements from Chemotion
        are accessible via the Collection objects

        :param id: The Database ID of the desired Element
        :return: a Reacton object

         :raises RequestException: (requests.exceptions.RequestException) if the information cannot be fetched. Make sure that your connection is active and you are logged in.
        """
        e = ElementSet(self._con, self.all_element_classes.get('reaction'))
        return typing.cast(Reaction, e.load_element(id))

    def get_wellplate(self, id: int) -> Wellplate:
        """
        Fetches data of one Wellplate object from the Chemotion server.
        It automatically parses the data into a Python-Wellplate-Object. However, you need to know the correct internally used ID
        of the Wellplate to be able to fetch it. Other methods to get Elements from Chemotion
        are accessible via the Collection objects

        :param id: The Database ID of the desired Element
        :return: a Reacton object

         :raises RequestException: (requests.exceptions.RequestException) if the information cannot be fetched. Make sure that your connection is active and you are logged in.
        """
        e = ElementSet(self._con, self.all_element_classes.get('wellplate'))
        return typing.cast(Wellplate, e.load_element(id))

    def get_research_plan(self, id: int) -> ResearchPlan:
        """
        Fetches data of one Research Plan object from the Chemotion server.
        It automatically parses the data into a Python-ResearchPlan-Object. However, you need to know the correct internally used ID
        of the Research Plan to be able to fetch it. Other methods to get Elements from Chemotion
        are accessible via the Collection objects

        :param id: The Database ID of the desired Element
        :return: a ResearchPlan object

         :raises RequestException: (requests.exceptions.RequestException) if the information cannot be fetched. Make sure that your connection is active and you are logged in.
        """
        e = ElementSet(self._con, self.all_element_classes.get('research_plan'))
        return typing.cast(ResearchPlan, e.load_element(id))

    def get_sample(self, id: int) -> Sample:
        """
        Fetches data of one Sample object from the Chemotion server.
        It automatically parses the data into a Python-Sample-Object. However, you need to know the correct internally used ID
        of the Sample to be able to fetch it. Other methods to get Elements from Chemotion
        are accessible via the Collection objects

        :param id: The Database ID of the desired Element
        :return: a Sample object

         :raises RequestException: (requests.exceptions.RequestException) if the information cannot be fetched. Make sure that your connection is active and you are logged in.
        """
        e = ElementSet(self._con, self.all_element_classes.get('sample'))
        return typing.cast(Sample, e.load_element(id))

    def get_generic_by_name(self, name: str, id: int) -> GenericElement:
        """
        Fetches data of one Generic object from the Chemotion server. Which generic element type
        It automatically parses the data into a Python-Generic-Object. However, you need to know the correct internally used ID
        of the Generic element to be able to fetch it. Other methods to get Elements from Chemotion
        are accessible via the Collection objects

        :param name: The name of the Genetic Element
        :param id: The Database ID of the desired Element
        :return: a Sample object

         :raises RequestException: (requests.exceptions.RequestException) if the information cannot be fetched. Make sure that your connection is active and you are logged in.
        """
        elem = self.all_element_classes.get(name)
        if elem is None:
            raise ValueError(f'Could not find a generic element under the name: "{name}"')
        e = ElementSet(self._con, elem)
        return typing.cast(GenericElement, e.load_element(id))

    def get_generic_by_label(self, label, id) -> GenericElement:
        for (elem_name, elem) in self.all_element_classes.items():
            if elem['label'] == label:
                return self.get_generic_by_name(elem_name, id)
        raise ValueError(f'Could not find a generic element with the label: "{label}"')

    def molecule(self):
        return MoleculeManager(self._con)

    def get_solvent_list(self):
        return list(ElementManager.get_solvent_list().keys())
