from tests.core.fixtures.dynamic.inputs.exchange import ACETATE_EXCHANGE, EXCHANGES
from tests.core.fixtures.dynamic.inputs.ode import ACETATE_PW_REACTION, ODES

VARIABLES = {"Ten": 10, "GPA": "Ten + 0.5", "GPB": 0.0027, "GPC1": 5, "GPC2": 4}


TOY_DYNAMIC_MODEL = {
    "name": "TOY_DYNAMIC_MODEL_ENTITY",
    "odes": ODES,
    "variables": VARIABLES,
    "exchange_fluxes": EXCHANGES,
}


TOY_DYNAMIC_MODEL_PW = {
    "name": "TOY_DYNAMIC_MODEL_PW_ENTITY",
    "odes": ODES + [ACETATE_PW_REACTION],
    "variables": VARIABLES,
    "exchange_fluxes": EXCHANGES + [ACETATE_EXCHANGE],
}
