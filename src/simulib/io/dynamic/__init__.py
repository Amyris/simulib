from typing import Any, Dict

from simulib.entities.dynamic import DynamicModelInput


class DictDynamicModelReaderMixin:
    expected_fields = DynamicModelInput.__fields__.keys()
    """
    Abstract base class that serves as base for all dynamic
    model importers in simulib
    """

    @classmethod
    def import_model_from_dict(cls, dict_: Dict[str, Any]):
        if cls.validate_payload(dict_):
            return DynamicModelInput.parse_obj(dict_)
        else:
            raise KeyError(
                "the supplied keys are not consistent with the expected model fields"
            )

    @classmethod
    def validate_payload(cls, dict_: Dict[str, Any]):
        return set(dict_.keys()).issubset(cls.expected_fields)


from simulib.io.dynamic.importers import (  # noqa: E402
    JSONDynamicModelImporter,
    YAMLDynamicModelImporter,
)

dynamic_model_importers = {
    "json": JSONDynamicModelImporter,
    "yaml": YAMLDynamicModelImporter,
}

__all__ = [
    "JSONDynamicModelImporter",
    "YAMLDynamicModelImporter",
]
