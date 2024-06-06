import dataclasses
import re
import json

# This file is mostly useful to convert between naming styles during
# serialization and deserialization. In DynamoDb we tend to use camelCase,
# and in Python we tend to use snake_case. These methods allow to convert
# serialized json objects between Python and C# styles.

# Based on https://stackoverflow.com/a/17156414/706456

camel_pat = re.compile(r'([A-Z])')
under_pat = re.compile(r'_([a-z])')


def convert_json(d, convert):
    new_d = {}
    for k, v in d.items():
        new_d[convert(k)] = convert_json(
            v, convert) if isinstance(v, dict) else v
    return new_d


def convert_load(*args, **kwargs):
    json_obj = json.loads(*args, **kwargs)
    return convert_json(json_obj, camel_to_underscore)


def convert_dump(*args, **kwargs):
    args = (convert_json(args[0], underscore_to_camel),) + args[1:]
    return json.dumps(*args, **kwargs)


def camel_to_underscore(name):
    return camel_pat.sub(lambda x: '_' + x.group(1).lower(), name)


def underscore_to_camel(name):
    return under_pat.sub(lambda x: x.group(1).upper(), name)


def dataclass_from_dict(cls, d):
    # Based on https://stackoverflow.com/a/54769644/706456
    try:
        types = {f.name: f.type for f in dataclasses.fields(cls)}
        return cls(**{f: dataclass_from_dict(types[f], d[f].value())
                      for f in d})
    except Exception:
        return d  # Not a dataclass field
