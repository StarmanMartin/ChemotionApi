import uuid


def add_to_dict(obj: dict, key: str, val: any) -> str:
    origen_key = key
    idx = 0
    while key in obj:
        key = "{}({})".format(origen_key, idx)
        idx += 1

    obj[key] = val
    return key


def parse_generic_field(field: dict) -> dict[str, any]:
    sub_fields = field.get('sub_fields')
    if type(sub_fields) is list and len(sub_fields) > 0:
        field_mapping = {'__field': field.get('field')}
        field_vals = None
        if field.get('type') == 'input-group':
            field_vals = []
            for sub_field in sub_fields:
                temp_sub_field = parse_generic_field(sub_field)
                field_vals.append(temp_sub_field.get('values'))

        elif field.get('type') == 'table':
            value_list = field.get('sub_values', [])
            field_vals = [{} for x in value_list]
            for sub_field in sub_fields:
                add_to_dict(field_mapping, sub_field.get('col_name'), sub_field.get('id'))
                for (idx, value) in enumerate(value_list):
                    add_to_dict(field_vals[idx], sub_field.get('col_name'), value[sub_field.get('id')])

        return {'values': field_vals, 'obj_mapping': field_mapping}
    elif field.get('type') == 'system-defined':
        return {'values': {'value': field.get('value'), 'unit': field.get('value_system')},
                'obj_mapping': field.get('id', field.get('field'))}
    elif field.get('type') == 'drag_element':
        return {'values': {'value': field.get('value')}, 'obj_mapping': field.get('id', field.get('field'))}
    return {'values': field.get('value'), 'obj_mapping': field.get('id', field.get('field'))}


def parse_generic_layer(layer: dict) -> dict[str, dict]:
    temp_layer = {}
    temp_id_layer = {'__key': layer.get('key')}
    fields = layer.get('fields', [])
    fields.sort(key=lambda x: x.get('position'))
    for field in fields:
        temp_field = parse_generic_field(field)
        field_name = field.get('label') if len(field.get('label')) > 0 else field.get('field')
        key = add_to_dict(temp_layer, field_name, temp_field.get('values'))
        temp_id_layer[key] = temp_field.get('obj_mapping')

    return {'values': temp_layer, 'obj_mapping': temp_id_layer}


def parse_generic_object_json(segment_json_data: dict) -> dict:
    temp_segment = {}
    temp_id_segment = {'__id': segment_json_data.get('id')}
    layers = list(segment_json_data.get('properties', {}).get('layers', {}).values())
    layers.sort(key=lambda x: x.get('position'))
    for layer in layers:
        temp_layer = parse_generic_layer(layer)
        layer_name = layer.get('label') if len(layer.get('label')) > 0 else layer.get('key')
        key = add_to_dict(temp_segment, layer_name, temp_layer.get('values'))
        temp_id_segment[key] = temp_layer.get('obj_mapping')
    return {'values': temp_segment, 'obj_mapping': temp_id_segment}


def clean_generic_field(field_obj: dict, values: any, field_mapping: dict | str = None) -> dict[str, any]:
    sub_fields = field_obj.get('sub_fields')
    if type(sub_fields) is list and len(sub_fields) > 0:
        if field_obj.get('type') == 'input-group':
            for (idx, val) in enumerate(values):
                clean_generic_field(sub_fields[idx], val)

        elif field_obj.get('type') == 'table':
            value_list = field_obj.get('sub_values', [])
            while len(value_list) < len(values):
                value_list.append({'id': uuid.uuid4().__str__()})
            for (k,v) in enumerate(values):
                for (k1,v1) in v.items():
                    value_list[k][field_mapping[k1]] = v1

    elif field_obj.get('type') == 'system-defined':
        field_obj['value'] = values['value']
        field_obj['value_system'] = values['unit']
    elif field_obj.get('type') == 'drag_element':
        field_obj['value'] = values['value']
    else:
        field_obj['value'] = values
    return field_obj


def clean_generic_object_json(segment_json_data: dict, values: dict, mapping: dict):
    for (k, v) in values.items():
        layer_mapping = mapping.get(k, {})
        layer_key = layer_mapping.get('__key')
        for (value_name, value_ob) in v.items():
            field_mapping = layer_mapping.get(value_name)
            field_key = ''
            if type(field_mapping) is str:
                field_key = field_mapping
            elif type(field_mapping) is dict:
                field_key = field_mapping.get('__field')
            fields = segment_json_data.get('properties').get('layers').get(layer_key).get('fields')
            field_obj = next((x for x in fields if x.get('field') == field_key), None)
            clean_generic_field(field_obj, value_ob, field_mapping)
