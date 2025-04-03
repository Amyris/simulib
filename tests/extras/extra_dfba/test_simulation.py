from simulib.methods.dynamic.dfba.entities import DFBASimulationOptions, DFBASimulationResult, DFBASimulationStatus
from simulib.methods.dynamic.exceptions import UndefinedVariableException
from simulib.utils.expression import ExpressionParser
from tests.extras.extra_dfba import DFBATestCase


from sympy.core.numbers import Float


class DFBASimulationTest(DFBATestCase):
    def setUp(self) -> None:
        super().setUp()
        self.simulation_options = DFBASimulationOptions(
            tstart=0,
            tstop=72,
            tout=2,
            output_fluxes=list(
                self.toy_simulator_input.dynamic_input.exchange_variables
            ),
        )

    def __validate_result(self, result, simulator_input, simulation_options):
        self.assertSetEqual(
            set(result.trajectories.columns) - {"time"},
            set(self.simulation_options.output_fluxes),
        )

        self.assertSetEqual(
            set(result.concentrations.columns) - {"time"},
            set([f.variable for f in simulator_input.dynamic_input.odes]),
        )
        tdiff = simulation_options.tstop - simulation_options.tstart
        self.assertEqual(
            result.concentrations.shape[0], (tdiff // simulation_options.tout) + 1
        )
        self.assertEqual(result.status, DFBASimulationStatus.COMPLETE)
        self.assertEqual(result.report.completion, 1)

    def test_simulate(self):
        result = self.simulator.simulate(
            self.toy_simulator_input, self.simulation_options
        )
        self.__validate_result(
            result, self.toy_simulator_input, self.simulation_options
        )

    def test_simulate_with_valid_but_missing_variables(self):
        ode_to_change = self.toy_simulator_input.dynamic_input.odes[1]
        ode_to_change.rhs_expression = ExpressionParser.parse_expression(
            [
                {"expr": "Biomass * (1/Glucose)", "cond": "Phase = 1"},
                {
                    "expr": [
                        {"expr": "Biomass * (2/Glucose)", "cond": "Pulse > 1"},
                        {"expr": "Biomass * (3/Glucose)", "cond": "Pulse <= 1"},
                    ],
                    "cond": "Phase = 2",
                },
            ]
        )

        # if phase = 2, pulse is required on definitions
        self.toy_simulator_input.dynamic_input.variables["Phase"] = Float(2)  # type: ignore

        self.assertRaises(
            UndefinedVariableException,
            self.simulator.simulate,
            self.toy_simulator_input,
            self.simulation_options,
        )

        # if phase = 1, pulse is not required, so it should simulate even if missing
        self.toy_simulator_input.dynamic_input.variables["Phase"] = Float(1)  # type: ignore
        result = self.simulator.simulate(
            self.toy_simulator_input, self.simulation_options
        )
        self.assertIsInstance(result, DFBASimulationResult)
        self.__validate_result(
            result, self.toy_simulator_input, self.simulation_options
        )