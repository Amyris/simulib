from json import JSONDecodeError
from os.path import join as joinpath

from yaml.parser import ParserError

from tests.core.fixtures.dynamic.entities.model import IMPORT_TEST_MODEL


def importpath(path):
    return joinpath(joinpath("resources", "test", "models"), path)


def write_str_to_example_dict(file_dict):
    str_example_dict = {}
    for key, (file, mdl, exc) in file_dict.items():
        with open(file, "r") as f:
            str_example_dict[key] = (f.read(), mdl, exc)
    return str_example_dict


JSON_FILE_EXAMPLE_DICT = {
    "test1_valid": (
        importpath(joinpath("json", "model_valid.json")),
        IMPORT_TEST_MODEL,
        None,
    ),
    "test2_malformed": (
        importpath(joinpath("json", "model_malformed.json")),
        None,
        JSONDecodeError,
    ),
    "test3_bad_payload": (
        importpath(joinpath("json", "model_bad_payload.json")),
        None,
        KeyError,
    ),
}

JSON_STR_EXAMPLE_DICT = write_str_to_example_dict(JSON_FILE_EXAMPLE_DICT)

YAML_FILE_EXAMPLE_DICT = {
    "test1_valid": (
        importpath(joinpath("yaml", "model_valid.yaml")),
        IMPORT_TEST_MODEL,
        None,
    ),
    "test2_malformed": (
        importpath(joinpath("yaml", "model_malformed.yaml")),
        None,
        ParserError,
    ),
    "test3_bad_payload": (
        importpath(joinpath("yaml", "model_bad_payload.yaml")),
        None,
        KeyError,
    ),
}

YAML_STR_EXAMPLE_DICT = write_str_to_example_dict(YAML_FILE_EXAMPLE_DICT)
