import warnings
from functools import reduce
from typing import Any, Dict, List, Optional, Set, Union

import sympy
from pydantic import BaseModel, field_validator
from typing_extensions import Self

from simulib.utils.expression import PYDANTIC_ENCODERS, ExpressionParser, ValueOrExpr


def empty_list():
    """
    Returns an empty list, avoiding mutable argument checks on
    dataclasses.
    """
    return []


class DynamicExpression(BaseModel):
    """
    Dataclass that represents a mathematical expression, supporting the definition of
    an expression serving as a condition.

        expr: A numerical value or a sympy Expr object
        cond: An optional sympy Expr object
    """

    expr: ValueOrExpr
    cond: Optional[sympy.Basic] = None

    @classmethod
    def from_object(cls, dct: Any):
        expr, cond = dct, None
        if isinstance(dct, dict):
            expr, cond = (dct.get(k) for k in ("expr", "cond"))
        return DynamicExpression(expr=expr, cond=cond)  # type: ignore

    @field_validator("expr", mode='before')
    @classmethod
    def validate_expr(cls, v):
        return ExpressionParser.parse_expression(v)

    @field_validator("cond", mode='before')
    @classmethod
    def validate_cond(cls, v):
        return cls.validate_expr(v) if v is not None else v

    def __eq__(self, other: Self) -> bool:
        return (self.expr == other.expr) and (self.cond == other.cond)

    def substitute(self, variable_map: Dict[str, ValueOrExpr]) -> None:
        """
        Replaces sympy Symbol objects on the expression with a user defined
        substitute.

            `variable_map`: A dictionary containing a value, expression or another object
            capable of replacing the variable. Replacements are made by name, which requires
            the dictionary keys to match the symbol names on the expressions.
        """
        # added relational since Expr isn't a subclass
        for key in ("expr", "cond"):
            if isinstance(
                value := getattr(self, key),
                (sympy.Expr, sympy.core.relational.Relational),
            ):
                setattr(self, key, value.subs(variable_map))

    @property
    def free_variables(self) -> Set[sympy.Symbol]:
        """
        Returns the free symbols present in the expr or cond expressions.
        These are variables without assignment that can be replaced in the expression.
        """
        expressions = (getattr(self, key) for key in ("expr", "cond"))
        symbols = (getattr(expr, "free_symbols", set()) for expr in expressions)
        return reduce(set.union, symbols, set())  # type: ignore

    class Config:
        arbitrary_types_allowed = True
        json_encoders = PYDANTIC_ENCODERS


class DynamicExchangeFlux(BaseModel):

    """
    A dataclass representing an exchange flux term present in a kinetic model.
    Fields:
        exchange_flux_id: A string identifier for the exchange reaction. Should match
            a reaction on the steady-state metabolic model
        lower_bound: A list of DynamicExpression instances containing lower bound expressions
        upper_bound: A list of DynamicExpression instances containing lower bound expressions
    """

    exchange_flux_id: str
    lower_bound: Optional[DynamicExpression] = None
    upper_bound: Optional[DynamicExpression] = None

    @property
    def free_variables(self):
        expressions = (self.lower_bound, self.upper_bound)
        return reduce(
            set.union,
            [set(exp.free_variables) for exp in expressions if exp is not None],
            set(),
        )

    def substitute(self, variable_map: Dict[str, Any]):
        for bound in [self.lower_bound, self.upper_bound]:
            if bound:
                bound.substitute(variable_map)

    @classmethod
    def from_dict(cls, dct: Dict[str, Any]) -> Self:
        return DynamicExchangeFlux(**dct)


class ODESimulationProperties(BaseModel):
    abs_tolerance: Optional[float] = None


class ODE(BaseModel):
    """
    A dataclass representing an ordinary differential equation (ODE).
    Fields:
        variable: The name of the variable being described by the ODE.
        rhs_expression: The right-hand side expression of the ODE.
        initial_condition: The initial condition for the ODE.
        annotations: Additional annotations for the ODE.
        simulation_properties: Properties related to the simulation of the ODE.
        metabolite_id: Optional metabolite identifier associated with the ODE.
    """
    variable: str
    rhs_expression: ValueOrExpr
    initial_condition: ValueOrExpr
    annotations: Dict[str, Any] = {}
    simulation_properties: ODESimulationProperties = ODESimulationProperties()
    metabolite_id: Optional[str] = None

    @field_validator("rhs_expression", "initial_condition", mode='before')
    @classmethod
    def validate_expr(cls, v):
        return ExpressionParser.parse_expression(v)

    @property
    def free_variables(self) -> Set[sympy.Symbol]:
        """
        Returns the free symbols present in all expressions contained in this instance.
        These are variables without assignment that can be replaced.
        """
        return set(getattr(self.rhs_expression, "free_symbols", []))  # type: ignore

    def substitute(
        self, variable_map: Dict[str, ValueOrExpr], replace_initial=False
    ) -> None:
        """
        Replaces sympy Symbol objects on the expression with a user defined
        substitute.

            `variable_map`: A dictionary containing a value, expression or another object
            capable of replacing the variable. Replacements are made by name, which requires
            the dictionary keys to match the symbol names on the expressions.
        """
        # added relational since Expr isn't a subclass
        try:
            self.rhs_expression = self.rhs_expression.subs(variable_map)
        except Exception:
            warnings.warn(
                f"Could not replace RHS expression {self.rhs_expression} of {self.variable} with {variable_map}."
            )

        if replace_initial and isinstance(self.initial_condition, sympy.Expr):
            try:
                self.initial_condition = self.initial_condition.subs(variable_map)
            except Exception:
                warnings.warn(
                    f"Could not replace initial condition {self.initial_condition} of {self.variable} with {variable_map}."
                )

    class Config:
        arbitrary_types_allowed = True
        json_encoders = PYDANTIC_ENCODERS


class DynamicModelInput(BaseModel):
    """
    A dataclass representing the input for a dynamic model.
    Fields:
        name: The name of the dynamic model.
        description: An optional description of the dynamic model.
        odes: A list of ODE instances.
        exchange_fluxes: A list of DynamicExchangeFlux instances.
        variables: A dictionary of variables and their associated expressions.
        simulation_properties: A dictionary of simulation properties.
    """
    name: str
    description: Optional[str] = ""
    odes: List[ODE] = empty_list()
    exchange_fluxes: List[DynamicExchangeFlux] = empty_list()
    variables: Dict[str, ValueOrExpr]
    simulation_properties: Dict[str, Union[str, int, float, bool]] = {}

    @classmethod
    def from_dict(cls, dct: Dict[str, Any]) -> Self:
        return DynamicModelInput(**dct)

    @field_validator("variables", mode='before')
    @classmethod
    def validate_expression_dicts(cls, v):
        return {ki: ExpressionParser.parse_expression(vi) for ki, vi in v.items()}

    @property
    def initial_conditions(self):
        return {ode.variable: ode.initial_condition for ode in self.odes}

    @property
    def free_variables(self) -> Set[str]:
        """
        Returns the free symbols present in all expressions contained in this instance.
        These are variables without assignment that can be replaced.
        """
        return {
            var.name
            for var in reduce(
                set.union,
                [
                    reduce(set.union, var_set, set())
                    for var_set in [
                        [flux.free_variables for flux in self.odes],
                        [exch.free_variables for exch in self.exchange_fluxes],
                    ]
                ],
                set(),
            )
        }

    @property
    def exchange_variables(self) -> Set[str]:
        """
        Returns the identifiers of the exchange reactions in this instance.
        """
        return {exflx.exchange_flux_id for exflx in self.exchange_fluxes}

    @property
    def defined_variables(self) -> Set[str]:
        """
        Returns the names of the variables contained in variables
        """
        return set(self.variables.keys())

    class Config:
        arbitrary_types_allowed = True
        union_mode='smart'
        json_encoders = PYDANTIC_ENCODERS
