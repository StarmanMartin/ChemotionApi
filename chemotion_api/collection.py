import json
import os
from typing import Iterable, TypeVar

import requests

from chemotion_api.elements import ElementSet, AbstractElement
from chemotion_api.utils import get_default_session_header, get_json_session_header

TAbstractCollection = TypeVar("TAbstractCollection", bound="AbstractCollection")
TRootCollection = TypeVar("TRootCollection", bound="RootCollection")


class AbstractCollection:
    children: list[TAbstractCollection]
    label: str = None
    _parent: TAbstractCollection = None
    id: int = None

    def __init__(self):
        self.children = []

    def __str__(self) -> str:
        return self.get_path()

    def __iter__(self):
        yield ('collections', self.children)

    def set_children(self, children: list[dict]):
        if children is None:
            self.children = []
            return

        for child in children:
            self.children.append(Collection(child))

        self._update_relations()

    def _update_relations(self):
        for child in self.children:
            child._parent = self
            child._update_relations()

    def to_json(self) -> dict:
        return {'children': [x.to_json() for x in self.children]}

    def find(self, label: str = None, **kwargs) -> list[TAbstractCollection]:
        results: list[AbstractCollection] = []
        kwargs['label'] = label
        hit = True
        for (key, val) in kwargs.items():
            if getattr(self, key) != val:
                hit = False
                break
        if hit:
            results.append(self)
        for x in self.children:
            results += x.find()
        return results

    def get_path(self) -> str:
        abs_path = []
        col = self
        while col._parent is not None:
            abs_path.append(col.label)
            col = col._parent
        abs_path.append('')
        abs_path.reverse()
        return '/'.join(abs_path)

    def get_root(self) -> TRootCollection:
        col = self
        while col._parent is not None:
            col = col._parent
        return col

    def get_samples(self) -> ElementSet:
        root = self.get_root()
        e = ElementSet(root._host_url, root._session, root._element_classes.get('sample'), self.id)
        e.load_elements()
        return e

    def get_sample(self, id) -> AbstractElement:
        root = self.get_root()
        e = ElementSet(root._host_url, root._session, root._element_classes.get('sample'), self.id)
        return e.load_element(id)

    def get_reactions(self) -> ElementSet:
        root = self.get_root()
        e = ElementSet(root._host_url, root._session, root._element_classes.get('reaction'), self.id)
        e.load_elements()
        return e

    def get_reaction(self, id) -> AbstractElement:
        root = self.get_root()
        e = ElementSet(root._host_url, root._session, root._element_classes.get('reaction'), self.id)
        return e.load_element(id)


class Collection(AbstractCollection):
    permission_level: int = None
    reaction_detail_level: int = None
    sample_detail_level: int = None
    screen_detail_level: int = None
    wellplate_detail_level: int = None
    element_detail_level: int = None
    sync_collections_users: dict = None
    is_locked: bool = None
    is_shared: bool = None
    is_synchronized: bool = None

    collection_json: dict = None

    def __init__(self, collection_json: dict):
        super().__init__()
        self.collection_json = collection_json
        self.set_children(collection_json.get('children', []))
        if 'children' in collection_json: del collection_json['children']

        for (key, val) in collection_json.items():
            if hasattr(self, key):
                setattr(self, key, val)

    def __iter__(self):
        for (key, val) in self.collection_json.items():
            if hasattr(self, key):
                val = getattr(self, key)
            yield (key, val)

    def to_json(self):
        as_dict = dict(self)
        return super().to_json() | as_dict

    def move(self, dest):
        abs_path = self.get_path()
        dest = os.path.abspath(os.path.join(os.path.dirname(abs_path), dest))
        self.get_root().move(abs_path, dest)


class RootSyncCollection(AbstractCollection):

    def __init__(self):
        super().__init__()
        self.label = 'sync_root'

    def to_json(self):
        as_dict = dict(self)
        return super().to_json() | as_dict


class RootCollection(AbstractCollection):
    sync_root: RootSyncCollection = None
    all: dict = None
    _element_classes: dict = {}

    def __init__(self, host_url: str, session: requests.Session):
        super().__init__()
        self._host_url = host_url
        self._session = session
        self.label = 'root'


    def set_element_classes(self, element_classes):
        self._element_classes = element_classes
    def load_collection(self):
        collection_url = '{}/api/v1/collections/roots.json'.format(self._host_url)

        res = self._session.get(collection_url,
                                headers=get_default_session_header())
        collections = json.loads(res.content)
        self.all = self._load_all_collection()['collection']
        self.id = self.all['id']
        self.set_children(collections['collections'])

    def _load_all_collection(self):
        collection_url = '{}/api/v1/collections/all'.format(self._host_url)

        res = self._session.get(collection_url,
                                headers=get_default_session_header())
        return json.loads(res.content)

    def load_sync_collection(self):
        collection_url = '{}/api/v1/syncCollections/sync_remote_roots'.format(self._host_url)

        res = self._session.get(collection_url,
                                headers=get_default_session_header())
        collections = json.loads(res.content)
        self.sync_root = RootSyncCollection()
        self.sync_root.set_children(collections['syncCollections'])

    def save(self):
        collection_url = '{}/api/v1/collections'.format(self._host_url)
        payload = self.to_json()
        payload['deleted_ids'] = []
        res = self._session.patch(collection_url,
                            headers=get_json_session_header(),
                            data=json.dumps(payload))
        if res.status_code != 200:
            raise ConnectionError('Saving collection error')


    def get_collection(self, col_path: str | list[str]) -> TAbstractCollection | None:
        col_path = self._prepare_path(col_path)
        current_pos = self
        for col_label in self._prepare_path(col_path):
            current_pos = next((x for x in current_pos.children if x.label == col_label), None)
            if current_pos is None:
                raise ModuleNotFoundError("'{}' Collection Not Found".format('/'.join(col_path)))
        return current_pos



    def move(self, src: str | list[str], dest: str | list[str]):
        prepared_src = self._prepare_path(src)
        src_col = self.get_collection(prepared_src)
        idx = next((i for (i, x) in enumerate(src_col._parent.children) if x.label == prepared_src[-1]), None)
        dest_col = self.get_collection(dest)

        src_col._parent.children.pop(idx)
        dest_col.children.append(src_col)
        self._update_relations()

    def to_json(self) -> dict:
        return {'collections': super().to_json()['children']}

    def _prepare_path(self, col_path: str | list[str]) -> list[str]:
        if type(col_path) == str:
            col_path = col_path.strip('/').split('/')
        return col_path
