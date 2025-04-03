from simulib.methods.dynamic.dfba.simulator import DynamicFBASimulator
from simulib.methods.dynamic.exceptions import MissingExchangeFluxException, UndefinedVariableException
from tests.extras.extra_dfba import DFBATestCase


import pandas as pd
from sympy import Symbol, symbols


class DFBAProblemGenerationTest(DFBATestCase):
    def test_create_model_object(self):
        dfba_model_object = self.simulator.create_model_object(self.toy_simulator_input)
        odes = self.dynamic_model.odes
        expected_kin_var_names = {r.variable for r in odes}
        dfba_model_kin_var_names = {k.id for k in dfba_model_object.kinetic_variables}
        self.assertEqual(expected_kin_var_names, dfba_model_kin_var_names)

        expected_exch_names = {
            r.exchange_flux_id for r in self.dynamic_model.exchange_fluxes
        }
        dfba_model_exch_names = {k.id for k in dfba_model_object.exchange_fluxes}
        self.assertEqual(expected_exch_names, dfba_model_exch_names)

    def test_create_model_object_with_missing_exchange(self):
        exchange_fluxes = self.toy_simulator_input.dynamic_input.exchange_fluxes
        exchange_fluxes[0].exchange_flux_id = "reaction_not_in_model"  # type: ignore
        self.assertRaises(
            MissingExchangeFluxException,
            self.simulator.create_model_object,
            self.toy_simulator_input,
        )

    def test_create_model_with_unsolved_definitions(self):
        variables = self.toy_simulator_input.dynamic_input.variables
        variables["GPB"] = 3 * Symbol("undefined_symbol")
        self.assertRaises(
            UndefinedVariableException,
            self.simulator.create_model_object,
            self.toy_simulator_input,
        )

    def test_create_model_with_unsolved_initial_conditions(self):
        self.toy_simulator_input.dynamic_input.odes[0].initial_condition = Symbol(
            "not_a_real_symbol"
        )
        self.assertRaises(
            ValueError,
            self.simulator.create_model_object,
            self.toy_simulator_input,
        )

    def test_calculate_variable_definitions_trajectories(self):
        key_1 = "key_1"
        key_2 = "key_2"
        key_3 = "key_3"
        k1, k2 = symbols(f"{key_1} {key_2}")
        concentrations = pd.DataFrame({key_1: [1, 2]})
        trajectories = pd.DataFrame({key_2: [1, 2]})
        variable_definitions = {key_3: k1 + k2}

        new_concentrations = DynamicFBASimulator._DynamicFBASimulator__calculate_variable_definitions_trajectories(
            variable_definitions,
            concentrations,
            trajectories,
        )
        pd.testing.assert_frame_equal(new_concentrations, pd.DataFrame({key_3: [2, 4]}))