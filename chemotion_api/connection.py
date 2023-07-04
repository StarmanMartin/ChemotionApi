import json

import requests



class Connection(requests.Session):
    def __init__(self, host_url: str, verify_ssl: bool = True):
        super().__init__()
        self._host_url = host_url.strip('/')
        self._verify = verify_ssl


    @property
    def host_url(self):
        return self._host_url

    def get(self, url_path: str = '', **kwargs) -> requests.Response:
        return self._send_request('get', url_path, self.get_default_session_header(), kwargs)

    def post(self, url_path: str = '', **kwargs) -> requests.Response:
        return self._send_request('post', url_path, self.get_json_session_header(), kwargs)

    def patch(self, url_path: str = '', **kwargs) -> requests.Response:
        return self._send_request('patch', url_path, self.get_json_session_header(), kwargs)

    def put(self, url_path: str = '', **kwargs) -> requests.Response:
        return self._send_request('put', url_path, self.get_json_session_header(), kwargs)

    def _send_request(self, method: str, url_path: str, default_header: dict, kwargs: dict) -> requests.Response:
        kwargs['verify'] = kwargs.get('verify', self._verify)
        kwargs['url'] = kwargs.get('url', f"{self._host_url}/{url_path.lstrip('/')}")
        kwargs['headers'] = kwargs.get('headers', default_header)
        if 'data' in kwargs and not isinstance(kwargs['data'], str) and kwargs['headers'].get('Content-Type') == 'application/json':
            kwargs['data'] = json.dumps(kwargs.get('data', {}))
        return getattr(super(), method)(**kwargs)
    @classmethod
    def get_default_session_header(cls) -> dict[str, str]:
        return {'User-Agent': 'Mozilla/5.0'}

    @classmethod
    def get_json_session_header(cls) -> dict[str, str]:
        header = cls.get_default_session_header()
        header['Content-Type'] = 'application/json'
        return header