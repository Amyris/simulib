from sympy import Float, Piecewise, Symbol

from simulib.entities.dynamic import (
    ODE,
    DynamicExchangeFlux,
    DynamicExpression,
    DynamicModelInput,
)
from simulib.utils.expression import ExpressionParser
from tests.core.fixtures.dynamic.entities.exchange import EXCHANGE_FLUX_ENTITIES
from tests.core.fixtures.dynamic.entities.ode import (
    ACETATE_PW_REACTION_ENTITY,
    DYNAMIC_FLUX_ENTITIES,
)
from tests.core.fixtures.dynamic.expressions import VARIABLES

DEFINITIONS_ENTITY = {
    k: ExpressionParser.parse_expression(v)
    for k, v in {
        "Ten": 10,
        "GPA": VARIABLES["Ten"] + 0.5,
        "GPB": 0.0027,
        "GPC1": 5,
        "GPC2": 4,
    }.items()
}

TOY_DYNAMIC_MODEL_ENTITY = DynamicModelInput(
    name="TOY_DYNAMIC_MODEL_ENTITY",
    odes=list(DYNAMIC_FLUX_ENTITIES.values()),
    variables=DEFINITIONS_ENTITY,  # type: ignore
    exchange_fluxes=[
        exch for name, exch in EXCHANGE_FLUX_ENTITIES.items() if name != "Acetate"
    ],
)

TOY_DYNAMIC_MODEL_ENTITY_PW = DynamicModelInput(
    name="TOY_DYNAMIC_MODEL_ENTITY_PW",
    odes=list(DYNAMIC_FLUX_ENTITIES.values()) + [ACETATE_PW_REACTION_ENTITY],
    variables=DEFINITIONS_ENTITY,  # type: ignore
    exchange_fluxes=list(EXCHANGE_FLUX_ENTITIES.values()),
)

IMPORT_TEST_MODEL = DynamicModelInput(
    name="TEST_MODEL",
    odes=[
        ODE(
            variable="Volume",
            rhs_expression=Symbol("D"),
            initial_condition=0.5,
        ),
        ODE(
            variable="Time",
            rhs_expression=Float(1),
            initial_condition=0.0,
        ),
        ODE(
            variable="Biomass",
            metabolite_id="Biomass",
            initial_condition=0.05,
            rhs_expression=Symbol("BIOMASS_SC4_bal") * Symbol("Biomass"),
        ),
        ODE(
            variable="Glucose",
            metabolite_id="Glucose",
            initial_condition=10.0,
            rhs_expression=Piecewise(
                (Symbol("Glucose") * Symbol("K1"), Symbol("D") > 20),
                (Symbol("Glucose") * Symbol("K2"), Symbol("D") > 0),
                (Symbol("Glucose"), True),
            ),
        ),
        ODE(
            variable="Ethanol",
            metabolite_id="Ethanol",
            initial_condition=0.0,
            rhs_expression=(Symbol("Ethanol") / Symbol("Volume")),
        ),
        ODE(
            variable="Glycerol",
            metabolite_id="Glycerol",
            initial_condition=0.0,
            rhs_expression=(Symbol("Glycerol") / Symbol("Volume")),
        ),
        ODE(
            variable="Oxygen",
            metabolite_id="Oxygen",
            initial_condition=Symbol("V1"),
            rhs_expression=0.0,
        ),
    ],
    exchange_fluxes=[
        DynamicExchangeFlux(exchange_flux_id="EX_etoh_e"),
        DynamicExchangeFlux(exchange_flux_id="BIOMASS_SC4_bal"),
        DynamicExchangeFlux(
            exchange_flux_id="EX_glyc_e",
            lower_bound=DynamicExpression(
                expr=Symbol("Glycerol") * Symbol("K3"), cond=Symbol("Glycerol")
            ),
            upper_bound=DynamicExpression(
                expr=Symbol("Glycerol") * Symbol("K4"), cond=Symbol("Glycerol")
            ),
        ),
        DynamicExchangeFlux(
            exchange_flux_id="EX_o2_e",
            lower_bound=DynamicExpression(
                expr=Piecewise(
                    (Symbol("Vomax"), Symbol("Time") <= Float(7.7)),
                    (Float(0.0), Symbol("Time") > Float(7.7)),
                ),  # type: ignore
                cond=Symbol("Oxygen"),
            ),
        ),
    ],
    variables={
        k: Float(v)
        for k, v in {"K1": 0.5, "K2": 0.25, "K3": 5, "K4": 10, "V1": 20}.items()
    },
)
