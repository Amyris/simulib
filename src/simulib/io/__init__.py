from abc import ABC, abstractmethod
from typing import Any, Callable, Dict

from simulib.io.utils import read_text_file


class ModelImporter(ABC):
    file_read_mode: str
    """
        Abstract base class that serves as base for all model importers
        in simulib
    """

    @classmethod
    @abstractmethod
    def import_model_from_object(cls, object: Any, *args, **kwargs):
        pass

    @classmethod
    @abstractmethod
    def import_model_from_file(cls, filepath: str, *args, **kwargs):
        pass


class TextModelImporter(ModelImporter):
    text_to_dict_func: Callable[[str], Dict[str, Any]]

    @classmethod
    def import_model_from_file(cls, filepath: str, *args, **kwargs):
        return cls.import_model_from_object(read_text_file(filepath))
