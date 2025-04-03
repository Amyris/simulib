from typing import Any, Dict, Tuple, Type
from unittest import TestCase

from simulib.entities.dynamic import DynamicModelInput
from simulib.io import ModelImporter
from simulib.io.dynamic import JSONDynamicModelImporter, YAMLDynamicModelImporter
from tests.core.fixtures.dynamic.inputs.importers import (
    JSON_FILE_EXAMPLE_DICT,
    JSON_STR_EXAMPLE_DICT,
    YAML_FILE_EXAMPLE_DICT,
    YAML_STR_EXAMPLE_DICT,
)

ImporterTestExampleDict = Dict[str, Tuple[Any, DynamicModelInput, Type[Exception]]]


class BaseTestClasses:
    class ImporterTestCase(TestCase):
        importer_class_type = ModelImporter
        obj_example_dict = {}
        file_example_dict = {}

        @property
        def importer_class(self) -> Type[ModelImporter]:
            return self.importer_class_type

        @property
        def obj_examples(self) -> ImporterTestExampleDict:
            return self.obj_example_dict

        @property
        def file_examples(self) -> ImporterTestExampleDict:
            return self.file_example_dict

        def call_with_temporary_file(self, func, path):
            with open(path, "w") as _:
                return func(path)

        def call_importer_tests(self, import_func, example_dict):
            for test_name, (
                test_input,
                expected_model,
                exception,
            ) in example_dict.items():
                with self.subTest(name=test_name, expected_exception=exception):
                    if not exception:
                        parsed_model = import_func(test_input)
                        self.compare_odes(parsed_model, expected_model)
                        self.assertEqual(
                            parsed_model.variables,
                            expected_model.variables,
                        )
                        self.assertEqual(
                            parsed_model.initial_conditions,
                            expected_model.initial_conditions,
                        )
                    else:
                        self.assertRaises(exception, import_func, test_input)

        def compare_odes(self, parsed_model, expected_model):
            for parsed_flux, expected_flux in zip(
                parsed_model.odes, expected_model.odes
            ):
                with self.subTest(expected_flux_name=expected_flux.variable):
                    self.assertEqual(parsed_flux, expected_flux)

        def test_object_importer(self):
            self.call_importer_tests(
                import_func=self.importer_class.import_model_from_object,
                example_dict=self.obj_examples,
            )

        def test_file_importer(self):
            self.call_importer_tests(
                import_func=self.importer_class.import_model_from_file,
                example_dict=self.file_examples,
            )


class JSONImporterTestCase(BaseTestClasses.ImporterTestCase):
    importer_class_type = JSONDynamicModelImporter
    obj_example_dict = JSON_STR_EXAMPLE_DICT
    file_example_dict = JSON_FILE_EXAMPLE_DICT


class YAMLImporterTestCase(BaseTestClasses.ImporterTestCase):
    importer_class_type = YAMLDynamicModelImporter
    obj_example_dict = YAML_STR_EXAMPLE_DICT
    file_example_dict = YAML_FILE_EXAMPLE_DICT
