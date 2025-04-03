import logging
from copy import deepcopy
from itertools import chain
from typing import Dict

import cobra
import pandas as pd
import sympy

from simulib.entities.dynamic import DynamicModelInput, ValueOrExpr
from simulib.entities.steadystate import SteadyStateSimulationInput
from simulib.methods import MetabolicSimulator
from simulib.methods.dynamic.dfba import dfba_module as dfba
from simulib.methods.dynamic.dfba.entities import (
    DFBAProblemVariableType,
    DFBASimulationInput,
    DFBASimulationOptions,
    DFBASimulationReport,
    DFBASimulationResult,
)
from simulib.methods.dynamic.exceptions import (
    MissingExchangeFluxException,
    UndefinedVariableException,
)
from simulib.utils.expression import simplify_expression_set

logger = logging.getLogger(__name__)


class DynamicFBASimulator(MetabolicSimulator):
    input_class = DFBASimulationInput
    options_class = DFBASimulationOptions

    def simulate(
        self,
        simulation_input: input_class,
        simulation_options: options_class,
        cached_model: "dfba.DfbaModel" = None,
    ) -> DFBASimulationResult:
        """
        Performs a dynamic FBA simulation using inputs from the `simulation_input` parameter
        with the parameters supplied in `simulation_options`. Optionally, the dFBA model object
        can be supplied if cached, by supplying it in the `cached_model` parameter.

        The default behavior is to create the model object every time the simulate method is called.
        """
        if not (dfba_model := cached_model):
            dfba_model = self.create_model_object(simulation_input)

        dfba_model = simulation_options.model_setup_func(
            dfba_model, simulation_input.dynamic_input.odes
        )
        try:
            concentrations, trajectories = dfba_model.simulate(
                simulation_options.tstart,
                simulation_options.tstop,
                simulation_options.tout,
                simulation_options.output_fluxes,
            )
            concentrations_variables = (
                self.__calculate_variable_definitions_trajectories(
                    simulation_input.dynamic_input.variables,
                    concentrations,
                    trajectories,
                )
            )
            concentrations = pd.concat(
                (concentrations, concentrations_variables),
                axis=1,
            )
        except RuntimeError as rte:
            raise rte

        report = DFBASimulationReport(
            max(concentrations["time"].tolist()),
            simulation_options.tstop,
        )
        status = report.status
        return DFBASimulationResult(concentrations, trajectories, status, report)

    @staticmethod
    def __calculate_variable_definitions_trajectories(
        variables: dict,
        concentrations: pd.DataFrame,
        trajectories: pd.DataFrame,
    ) -> pd.DataFrame:
        all_results = pd.concat((concentrations, trajectories), axis=1)
        constants = simplify_expression_set(variables)
        df = pd.DataFrame()
        for constant, expr in constants.items():
            try:
                if free_symbols := list(expr.free_symbols):
                    expr_lambda = sympy.lambdify(free_symbols, expr, "numpy")
                    free_symbols_values = []
                    for fs in free_symbols:
                        free_symbols_values.append(all_results[str(fs)])
                    df[constant] = expr_lambda(*free_symbols_values)
            except (KeyError, AttributeError):
                logger.exception(
                    f"Unable to create concentration trajectories for {constant}"
                )
                continue
        return df

    def create_model_object(self, simulation_input: input_class) -> "dfba.DfbaModel":
        """
        Creates a validated DfbaModel instance from the inputs in `simulation_input`.
        """
        model_object, dynamic_model, constants, variables = self.__create_dfba_model(
            simulation_input
        )
        init_variables = set(dynamic_model.initial_conditions.keys())

        for var_type_name, var_type in DFBAProblemVariableType.__members__.items():
            if var_type != DFBAProblemVariableType.EXCHANGE:
                variable_list = set(variables[var_type].keys())
                if len(flux_var_diff := variable_list - init_variables) > 0:
                    raise UndefinedVariableException(flux_var_diff, var_type_name)

        self.__add_initial_conditions(
            model_object, dynamic_model.initial_conditions, constants
        )

        return model_object

    @classmethod
    def __add_initial_conditions(
        cls,
        dfba_model: "dfba.DfbaModel",
        initial_conditions: Dict[str, ValueOrExpr],
        constants: Dict[str, ValueOrExpr],
    ) -> None:
        initial_conditions_final = deepcopy(initial_conditions)
        for var, exp in initial_conditions.items():
            if isinstance(exp, sympy.Expr):
                initial_conditions_final[var] = exp.subs(constants)

        try:
            simulation_initial_conditions = {
                k: float(v) for k, v in initial_conditions_final.items()
            }
            dfba_model.add_initial_conditions(simulation_initial_conditions)
        except Exception:
            raise ValueError(
                f"one or more initial conditions are missing: {initial_conditions_final}"
            )

    @staticmethod
    def __create_cobra_model(
        steadystate_input: SteadyStateSimulationInput,
    ) -> cobra.Model:
        cobra_model = steadystate_input.model.copy()
        if constraints := steadystate_input.reaction_constraints:
            for constraint in constraints:
                bounds = (constraint.lower_bound, constraint.upper_bound)
                cobra_model.reactions.get_by_id(constraint.reaction_id).bounds = bounds
        if added_reaction_list := steadystate_input.added_reactions:
            cobra_model.add_reactions(
                [
                    reaction_obj.to_cobra_reaction(cobra_model)
                    for reaction_obj in added_reaction_list
                ]
            )
        return cobra_model

    @classmethod
    def __create_kinetic_variables(cls, dynamic_input: DynamicModelInput):
        dynamic_model = deepcopy(dynamic_input)
        # resolve and simplify all variable definitions
        constants = simplify_expression_set(dynamic_input.variables)

        # replace all constants with their definitions and/or values
        for expr_element in dynamic_model.odes + dynamic_model.exchange_fluxes:
            expr_element.substitute(constants)

        var_set_names = {
            DFBAProblemVariableType.METABOLITE: set(
                ode.variable for ode in dynamic_model.odes
            ),
            DFBAProblemVariableType.EXCHANGE: dynamic_model.exchange_variables,
        }

        var_set_names[
            DFBAProblemVariableType.PARAMETER
        ] = dynamic_model.free_variables - (
            var_set_names[DFBAProblemVariableType.METABOLITE]
            | var_set_names[DFBAProblemVariableType.EXCHANGE]
        )

        var_groups = {
            DFBAProblemVariableType.METABOLITE: dfba.KineticVariable,
            DFBAProblemVariableType.EXCHANGE: dfba.ExchangeFlux,
            DFBAProblemVariableType.PARAMETER: dfba.KineticVariable,
        }

        return (
            dynamic_model,
            {
                group: {k: var(k) for k in var_set_names[group]}  # type: ignore
                for group, var in var_groups.items()
            },
            constants,
        )

    @classmethod
    def __create_dfba_model(cls, simulation_input: DFBASimulationInput):
        cobra_model = cls.__create_cobra_model(simulation_input.steady_state_input)
        dfba_model = dfba.DfbaModel(cobra_model)
        dynamic_model, variables, constants = cls.__populate_dynamic_model(
            dfba_model, simulation_input
        )
        return dfba_model, dynamic_model, constants, variables

    @classmethod
    def __add_exchange_bounds(
        cls, dfba_model, exchange_flux, dynamic_vars, exchange_vars
    ):
        func_to_bound = {
            "lower_bound": dfba_model.add_exchange_flux_lb,
            "upper_bound": dfba_model.add_exchange_flux_ub,
        }

        exchange_id = exchange_flux.exchange_flux_id
        for bound, func in func_to_bound.items():
            if expression := getattr(exchange_flux, bound):
                expression.substitute(dynamic_vars)
                expression.substitute(exchange_vars)
                func(
                    exchange_flux_id=exchange_id,
                    expression=expression.expr,
                    condition=expression.cond,
                )

    @classmethod
    def __populate_dynamic_model(
        cls, dfba_model: "dfba.DfbaModel", simulation_input: DFBASimulationInput
    ):
        dynamic_model, dynamic_var_dict, constants = cls.__create_kinetic_variables(
            simulation_input.dynamic_input
        )

        dynamic_variables = dict(
            chain(
                *(
                    dynamic_var_dict[k].items()
                    for k in [
                        DFBAProblemVariableType.METABOLITE,
                        DFBAProblemVariableType.PARAMETER,
                    ]
                )
            )
        )
        exchange_variables = dynamic_var_dict[DFBAProblemVariableType.EXCHANGE]

        if intersection := (set(dynamic_variables) & set(exchange_variables)):
            raise ValueError(
                f"found non-unique variables in both exchange and kinetic groups: {intersection}"
            )

        reaction_ids = [
            r.id for r in simulation_input.steady_state_input.model.reactions
        ]
        if missing_reactions := (set(exchange_variables.keys()) - set(reaction_ids)):
            raise MissingExchangeFluxException(missing_reactions)

        dfba_model.add_kinetic_variables(list(dynamic_variables.values()))
        dfba_model.add_exchange_fluxes(list(exchange_variables.values()))

        for flux in dynamic_model.odes:
            flux.substitute(dynamic_variables)
            flux.substitute(exchange_variables)

            dfba_model.add_rhs_expression(
                flux.variable,
                flux.rhs_expression,
            )

        for exchange_flux in dynamic_model.exchange_fluxes:
            cls.__add_exchange_bounds(
                dfba_model,
                exchange_flux,
                dynamic_variables,
                exchange_variables,
            )

        return dynamic_model, dynamic_var_dict, constants
