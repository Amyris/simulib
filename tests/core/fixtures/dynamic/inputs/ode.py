from tests.core.fixtures.dynamic.expressions import EQUATIONS

BIOMASS_REACTION = {
    "ode_type": "metabolite",
    "rhs_expression": EQUATIONS[3].string,
    "variable": "Biomass",
    "initial_condition": 0.03,
    "metabolite_id": "Biomass",
    "exchange_flux": {
        "exchange_flux_id": "BIOMASS_Ecoli_core_w_GAM",
        "lower_bound": None,
        "upper_bound": None,
    },
}

GLUCOSE_REACTION = {
    "ode_type": "metabolite",
    "rhs_expression": EQUATIONS[3].string,
    "variable": "Glucose",
    "initial_condition": "GPC1 + GPA",
    "metabolite_id": "Glucose",
    "exchange_flux": {
        "exchange_flux_id": "EX_glc__D_e",
        "lower_bound": {"expr": EQUATIONS[0].string, "cond": "Glucose"},
    },
}

OXYGEN_REACTION = {
    "ode_type": "metabolite",
    "rhs_expression": [EQUATIONS[1].string],
    "variable": "Oxygen",
    "initial_condition": 0.0,
    "metabolite_id": "Oxygen",
    "exchange_flux": {
        "exchange_flux_id": "EX_o2_e",
        "lower_bound": {"expr": EQUATIONS[2].string, "cond": "Oxygen"},
    },
}

ACETATE_PW_REACTION = {
    "ode_type": "metabolite",
    "variable": "Acetate",
    "initial_condition": 0.0,
    "metabolite_id": "Acetate",
    "rhs_expression": [
        {"expr": EQUATIONS[4].string, "cond": "Acetate < 0.1"},
        {"expr": EQUATIONS[5].string, "cond": "Acetate >= 0.1"},
    ],
    "exchange_flux": {"exchange_flux_id": "EX_ac_e"},
}

ODES = [GLUCOSE_REACTION, BIOMASS_REACTION, OXYGEN_REACTION]
