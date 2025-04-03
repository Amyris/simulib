from sympy import Piecewise, Symbol

from simulib.entities.dynamic import ODE
from tests.core.fixtures.dynamic.expressions import EQUATIONS, VARIABLES

BIOMASS_REACTION_ENTITY = ODE(
    variable="Biomass",
    metabolite_id="Biomass",
    initial_condition=0.03,
    rhs_expression=EQUATIONS[3].sympy,
)

GLUCOSE_REACTION_ENTITY = ODE(
    variable="Glucose",
    metabolite_id="Glucose",
    initial_condition=VARIABLES["GPC1"] + VARIABLES["GPA"],
    rhs_expression=EQUATIONS[3].sympy,
)

OXYGEN_REACTION_ENTITY = ODE(
    variable="Oxygen",
    metabolite_id="Oxygen",
    initial_condition=0.0,
    rhs_expression=EQUATIONS[1].sympy,
)

ACETATE_PW_REACTION_ENTITY = ODE(
    variable="Acetate",
    metabolite_id="Acetate",
    rhs_expression=Piecewise(
        (EQUATIONS[4].sympy, Symbol("Acetate") < 0.1),
        (EQUATIONS[5].sympy, Symbol("Acetate") >= 0.1),
    ),  # type: ignore
    initial_condition=0.0,
)

DYNAMIC_FLUX_ENTITIES = {
    "Glucose": GLUCOSE_REACTION_ENTITY,
    "Biomass": BIOMASS_REACTION_ENTITY,
    "Oxygen": OXYGEN_REACTION_ENTITY,
}
