import json

import requests

from chemotion_api.generic_segments import GenericSegments
from chemotion_api.utils import add_to_dict, get_json_session_header, parse_generic_object_json, \
    clean_generic_object_json


class Dataset:
    def __init__(self):
        pass #ToDo Implement Analyses-Dataset Management

class Analyses:
    def __init__(self, data):
        self.id = data.get('id')
        self._data = data

    def to_josn(self):
        return self._data


class AbstractElement:
    def __init__(self, json_data, generic_segments: GenericSegments, host_url: str, session: requests.Session):
        self.generic_segments = generic_segments
        self._host_url = host_url
        self._session = session
        self.json_data = json_data

        self.id = json_data.get('id')
        self._properties: dict = self._parse_properties()
        self._analyses: list[dict] = self._parse_analyses()
        segment_temp = self._parse_segments()
        self._segments_mapping = segment_temp.get('obj_mapping')
        self.segments = segment_temp.get('values')
        add_to_dict(self.segments, 'Properties', self._properties)
        add_to_dict(self.segments, 'Analyses', self._properties)

    def save(self):
        data = self.clean_data()
        res = self._session.put(url=self.save_url(), data=json.dumps(data), headers=get_json_session_header())
        if res.status_code != 200:
            raise ConnectionError('{} -> '.format(res.status_code, res.text))

    def clean_data(self):
        self._clean_segments_data()
        return self.json_data

    def save_url(self):
        return "{}/api/v1/{}s/{}".format(self._host_url, self.json_data.get('type'), self.id)

    def _parse_properties(self) -> dict:
        raise NotImplemented

    def _parse_analyses(self) -> list:
        analyses_list = []
        for analyses in self.json_data.get('container', {}).get('children', [{}])[0].get('children', []):
            analyses_list.append(Analyses(analyses))
        return analyses_list

    def _clean_analyses_data(self):
        res_list = self.json_data.get('container', {}).get('children', [{}])[0].get('children', [])
        for (idx, analyses) in enumerate(res_list):
            analyses_obj: list[Analyses] = [item for (index, item) in enumerate(self._analyses) if item.id == analyses.id]
            if len(analyses_obj) == 1:
                new_data = analyses_obj[0].to_josn()
                for (key, item) in analyses.item():
                    if key in new_data:
                        res_list[idx][key] = new_data

        return res_list

    def _parse_segments(self) -> dict[str: dict]:
        results: dict[str: dict] = {}
        results_mapping: dict[str: dict] = {}
        for segment in self.json_data.get('segments', []):
            a = [x for x in self.generic_segments.all_classes if x['id'] == segment['segment_klass_id']]
            temp_segment = parse_generic_object_json(segment)
            key = add_to_dict(results, a[0].get('label', 'no_label'),  temp_segment.get('values'))
            results_mapping[key] = temp_segment.get('obj_mapping')
        return {'values': results, 'obj_mapping': results_mapping}

    def _clean_segments_data(self):
        res_list = self.json_data.get('segments', [])
        for (seg_key, segment_mapping) in self._segments_mapping.items():
            list_idx = next(i for (i,x) in enumerate(res_list) if x.get('id') == segment_mapping['__id'])
            clean_generic_object_json(res_list[list_idx], self.segments[seg_key], segment_mapping)