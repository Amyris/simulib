from unittest.mock import patch

import pandas as pd

from simulib.methods.dynamic.dfba.entities import (
    DFBASimulationOptions,
    DFBASimulationStatus,
)
from tests.extras.extra_dfba import DFBATestCase


class DFBAStatusTest(DFBATestCase):
    def setUp(self) -> None:
        super().setUp()
        self.simulation_options = DFBASimulationOptions(
            tstart=0,
            tstop=7,
            tout=2,
            output_fluxes=list(
                self.toy_simulator_input.dynamic_input.exchange_variables
            ),
        )
        self.mock_conc = pd.DataFrame(
            {
                "time": [float(x) for x in range(0, 8)],
                "meta1": [float(x / 10) for x in range(0, 8)],
                "meta2": [float(x / 10) for x in range(0, 8)],
            }
        )

        self.mock_conc_fail = pd.DataFrame(
            {
                "time": [0],
                "meta1": [0],
                "meta2": [0],
            }
        )

        self.mock_invalid = pd.DataFrame(
            {
                "time": [float(x) for x in range(0, 10)],
                "meta1": [float(x / 10) for x in range(0, 10)],
                "meta2": [float(x / 10) for x in range(0, 10)],
            }
        )

    @patch("simulib.methods.dynamic.dfba.dfba_module.model.DfbaModel.simulate")
    def test_simulation_status_successful(self, simulate_patch):
        simulate_patch.return_value = self.mock_conc, self.mock_conc
        result = self.simulator.simulate(
            self.toy_simulator_input, self.simulation_options
        )
        self.assertEqual(result.status, DFBASimulationStatus.COMPLETE)
        self.assertEqual(result.report.completion, 1.0)

    @patch("simulib.methods.dynamic.dfba.dfba_module.model.DfbaModel.simulate")
    def test_simulation_status_incomplete(self, simulate_patch):
        simulate_patch.return_value = self.mock_conc, self.mock_conc
        self.simulation_options.tstop = 8.0
        result = self.simulator.simulate(
            self.toy_simulator_input, self.simulation_options
        )
        self.assertEqual(result.status, DFBASimulationStatus.INCOMPLETE)
        self.assertEqual(result.report.completion, 0.875)

    @patch("simulib.methods.dynamic.dfba.dfba_module.model.DfbaModel.simulate")
    def test_simulation_status_fail(self, simulate_patch):
        simulate_patch.return_value = self.mock_conc_fail, self.mock_conc_fail
        result = self.simulator.simulate(
            self.toy_simulator_input, self.simulation_options
        )
        self.assertEqual(result.status, DFBASimulationStatus.FAIL)
        self.assertEqual(result.report.completion, 0)

    @patch("simulib.methods.dynamic.dfba.dfba_module.model.DfbaModel.simulate")
    def test_simulation_status_invalid(self, simulate_patch):
        simulate_patch.return_value = self.mock_invalid, self.mock_invalid
        result = self.simulator.simulate(
            self.toy_simulator_input, self.simulation_options
        )
        self.assertEqual(result.status, DFBASimulationStatus.INVALID)
        self.assertEqual(result.report.completion, 0)
