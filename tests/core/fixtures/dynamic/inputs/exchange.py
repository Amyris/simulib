from tests.core.fixtures.dynamic.expressions import EQUATIONS

BIOMASS_EXCHANGE = {
    "exchange_flux_id": "BIOMASS_Ecoli_core_w_GAM",
    "lower_bound": None,
    "upper_bound": None,
}

GLUCOSE_EXCHANGE = {
    "exchange_flux_id": "EX_glc__D_e",
    "lower_bound": {"expr": EQUATIONS[0].string, "cond": "Glucose"},
}

OXYGEN_EXCHANGE = {
    "exchange_flux_id": "EX_o2_e",
    "lower_bound": {"expr": EQUATIONS[2].string, "cond": "Oxygen"},
}

ACETATE_EXCHANGE = {"exchange_flux_id": "EX_ac_e"}


EXCHANGES = [GLUCOSE_EXCHANGE, BIOMASS_EXCHANGE, OXYGEN_EXCHANGE]
