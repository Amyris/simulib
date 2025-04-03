from json import loads as json_load_string

from yaml import safe_load as yaml_loads

from simulib.io import TextModelImporter
from simulib.io.dynamic import DictDynamicModelReaderMixin


class JSONDynamicModelImporter(TextModelImporter, DictDynamicModelReaderMixin):
    @classmethod
    def import_model_from_object(cls, obj: str):
        return cls.import_model_from_dict(json_load_string(obj))


class YAMLDynamicModelImporter(TextModelImporter, DictDynamicModelReaderMixin):
    @classmethod
    def import_model_from_object(cls, obj: str):
        return cls.import_model_from_dict(yaml_loads(obj))
