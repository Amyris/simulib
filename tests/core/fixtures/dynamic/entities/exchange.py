from simulib.entities.dynamic import DynamicExchangeFlux, DynamicExpression
from tests.core.fixtures.dynamic.expressions import EQUATIONS, VARIABLES

EXCHANGE_FLUX_ENTITIES = {
    "Glucose": DynamicExchangeFlux(
        exchange_flux_id="EX_glc__D_e",
        lower_bound=DynamicExpression(
            expr=EQUATIONS[0].sympy, cond=VARIABLES["Glucose"]
        ),
        upper_bound=None,
    ),
    "Biomass": DynamicExchangeFlux(
        exchange_flux_id="BIOMASS_Ecoli_core_w_GAM", lower_bound=None, upper_bound=None
    ),
    "Oxygen": DynamicExchangeFlux(
        exchange_flux_id="EX_o2_e",
        lower_bound=DynamicExpression(
            expr=EQUATIONS[2].sympy, cond=VARIABLES["Oxygen"]
        ),
    ),
    "Acetate": DynamicExchangeFlux(exchange_flux_id="EX_ac_e"),
}
