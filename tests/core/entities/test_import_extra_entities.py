from unittest import TestCase


class ExtraEntityImportTestCase(TestCase):
    def test_import_dfba_entities(self):
        from simulib.methods.dynamic.dfba.entities import (
            DFBAProblemVariableType,
            DFBASimulationInput,
            DFBASimulationOptions,
            DFBASimulationResult,
        )

        for class_ in [
            DFBASimulationInput,
            DFBAProblemVariableType,
            DFBASimulationResult,
            DFBASimulationOptions,
        ]:
            self.assertIsNotNone(class_)
            self.assertIsInstance(class_, type)
