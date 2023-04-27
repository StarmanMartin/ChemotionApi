from chemotion_api.utils import get_default_session_header


class GenericElements:
    @classmethod
    def get_all_classes(cls, host_url, session):
        get_url = "{}/api/v1/generic_elements/klasses.json".format(host_url)
        res = session.get(get_url, headers=get_default_session_header())
        if res.status_code != 200:
            raise ConnectionError('Counld not get the genetic elements')
        all_classes = {}
        for x in res.json()['klass']:
            all_classes[x['name']] = x
        return all_classes
