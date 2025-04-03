from collections import namedtuple

from sympy import Symbol

EQUATION_SYMBOL_NAMES = [
    "GPA",
    "GPB",
    "GPC1",
    "GPC2",
    "Glucose",
    "BIOMASS_Ecoli_core_w_GAM",
    "Biomass",
    "Oxygen",
    "Ten",
    "EX_o2_e",
    "EX_glc__D_e",
]

VARIABLES = {name: Symbol(name) for name in EQUATION_SYMBOL_NAMES}
__TestEquation = namedtuple("TestEquation", ["string", "sympy"])

EQUATIONS = [
    __TestEquation(*args)
    for args in (
        (
            "GPA * (Glucose / (GPB + Glucose)) * (1 / (1 / (GPC1 * GPC2)))",
            VARIABLES["GPA"]
            * (VARIABLES["Glucose"] / (VARIABLES["GPB"] + VARIABLES["Glucose"]))
            * (1 / (1 / (VARIABLES["GPC1"] * VARIABLES["GPC2"]))),
        ),
        (
            "EX_o2_e * 16.0 * Biomass / 1000.0",
            VARIABLES["EX_o2_e"] * 16.0 * VARIABLES["Biomass"] / 1000.0,
        ),
        (
            "15.0 * (Oxygen / (0.024 + Oxygen))",
            15.0 * (VARIABLES["Oxygen"] / (0.024 + VARIABLES["Oxygen"])),
        ),
        (
            "BIOMASS_Ecoli_core_w_GAM * Biomass",
            VARIABLES["BIOMASS_Ecoli_core_w_GAM"] * VARIABLES["Biomass"],
        ),
        ("1.5 * (0.03 + Acetate)", 1.5 * (0.03 + Symbol("Acetate"))),
        ("0.1 * (0.03 + Acetate)", 0.1 * (0.03 + Symbol("Acetate"))),
    )
]
