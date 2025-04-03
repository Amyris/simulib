from unittest import TestCase
from simulib.entities.dynamic import DynamicModelInput
from simulib.entities.steadystate import SteadyStateSimulationInput
from simulib.methods.dynamic.dfba.entities import DFBASimulationInput
from simulib.methods.dynamic.dfba.simulator import DynamicFBASimulator
from tests.core.fixtures.dynamic.entities.exchange import EXCHANGE_FLUX_ENTITIES
from tests.core.fixtures.dynamic.inputs.model import TOY_DYNAMIC_MODEL_PW
from tests.core.fixtures.steadystate import CobraModelFactory


class DFBATestCase(TestCase):
    def setUp(self) -> None:
        self.simulator = DynamicFBASimulator()
        self.test_cobra_model = CobraModelFactory.create_fully_connected_test_model(
            ["ac", "biomass", "glc__D", "o2"]
        )

        biomass_reaction_obj = self.test_cobra_model.reactions.get_by_id("EX_biomass_e")
        biomass_reaction_obj.id = EXCHANGE_FLUX_ENTITIES["Biomass"].exchange_flux_id

        self.dynamic_model = DynamicModelInput.from_dict(TOY_DYNAMIC_MODEL_PW)
        self.steadystate_input = SteadyStateSimulationInput(model=self.test_cobra_model)
        self.toy_simulator_input = DFBASimulationInput(
            steady_state_input=self.steadystate_input,
            dynamic_input=self.dynamic_model,
        )
        self.dynamic_sim_input = TOY_DYNAMIC_MODEL_PW