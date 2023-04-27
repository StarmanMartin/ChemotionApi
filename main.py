import json
import logging
import random

from chemotion_api import Instance
from utils import load_config, CONFIG





if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s->%(message)s',  filename='ElnFetcher.log', encoding='utf-8', level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())


    instance = Instance('http://193.196.38.77/').test_connection().login('tet', '12342234')
    user = instance.get_user()


    col = instance.get_all_collections()
    samples = col.get_collection('/Martins').get_samples()
    sample = col.get_collection('/Martins').get_sample(2812)
    sample.segments['Properties']['boiling_point'] = 55
    sample.segments['Properties']['name'] = "Test Sample API"
    with open('sample_o.json', 'w+') as f:
        f.write(json.dumps(sample.json_data))

    sample.segments['Enzyme methods data']['Additional information on the enzyme']['Tissue'] = 'Test'
    sample.segments['Enzyme methods data']['Assay conditions']['Buffer'].append(sample.segments['Enzyme methods data']['Assay conditions']['Buffer'][0].copy())
    sample.segments['Enzyme methods data']['Assay conditions']['Buffer'][-1]['Concentration']['value'] = int(random.random() * 500)
    sample.save()

    col.get_collection('/External Collections/SPP Test Reactions/Test Collection Manuel Tsotsalas')

    col.move('/Martins/Inner Martins', '/External Collections/SPP Test Reactions/Test Collection Manuel Tsotsalas')

    a = col.get_collection('/External Collections/SPP Test Reactions/Test Collection Manuel Tsotsalas/Inner Martins')
    a.label += ' 2'
    col.save()

    a.move('../../../Martins')
    a = col.get_collection('/Martins/Inner Martins 2')
    a.label = 'Inner Martins'
    col.save()