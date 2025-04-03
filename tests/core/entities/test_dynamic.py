from copy import deepcopy
from typing import Union
from unittest import TestCase

from pydantic import ValidationError
from sympy import Eq, Expr, Piecewise, Symbol

from simulib.entities.dynamic import (
    ODE,
    DynamicExchangeFlux,
    DynamicExpression,
    DynamicModelInput,
    empty_list,
)
from simulib.utils.expression import ExpressionParser
from tests.core.fixtures.dynamic.entities.model import TOY_DYNAMIC_MODEL_ENTITY
from tests.core.fixtures.dynamic.expressions import EQUATION_SYMBOL_NAMES, EQUATIONS
from tests.core.fixtures.dynamic.inputs.model import TOY_DYNAMIC_MODEL, VARIABLES


class DynamicSimulationInputTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dynamic_model = TOY_DYNAMIC_MODEL
        cls.parsed_model = DynamicModelInput.from_dict(cls.dynamic_model)

    def test_model_dict_input_is_correct(self):
        for field in ["odes", "initial_conditions", "variables"]:
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(self.parsed_model, field),
                    getattr(TOY_DYNAMIC_MODEL_ENTITY, field),
                )
        self.assertEqual(self.parsed_model, TOY_DYNAMIC_MODEL_ENTITY)

    def test_get_exchange_fluxes(self):
        self.assertSetEqual(
            {"BIOMASS_Ecoli_core_w_GAM", "EX_glc__D_e", "EX_o2_e"},
            self.parsed_model.exchange_variables,
        )

    def test_get_defined_variables(self):
        self.assertSetEqual(
            set(self.parsed_model.variables.keys()), set(VARIABLES.keys())
        )

    def test_get_free_variables(self):
        # ethanol and glucose drain are not in any equation
        # and should not appear as free variables
        # variable Ten appears in a variable definition but not in any equation
        symbols_not_in_eqs = {"EX_etoh_e", "EX_glc__D_e", "Ten"}
        var_definitions = set(self.parsed_model.variables.keys())
        self.assertSetEqual(
            (var_definitions | set(EQUATION_SYMBOL_NAMES)) - symbols_not_in_eqs,
            self.parsed_model.free_variables,
        )


class DynamicExpressionTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expressions = [
            {"expr": "3 * Acetaldehyde + Variable", "cond": "Acetaldehyde"},
            {"expr": "3.7637", "cond": "X"},
            {"expr": "Heme + Iron3"},
        ]

        acald, var, xvar, heme, fe3 = (
            Symbol(x) for x in ["Acetaldehyde", "Variable", "X", "Heme", "Iron3"]
        )

        cls.expected = [
            {"expr": 3 * acald + var, "cond": acald},
            {"expr": 3.7637, "cond": xvar},
            {"expr": heme + fe3, "cond": None},
        ]

        cls.expected_free_variables = [{acald, var}, {xvar}, {heme, fe3}]

    def test_empty_list(self):
        # just so pytest-cov is happy
        self.assertListEqual(empty_list(), [])

    def test_parse_sympy_expression(self):
        for dict_to_parse, expected_dict in zip(self.expressions, self.expected):
            with self.subTest(expression=dict_to_parse):
                parsed_expr = DynamicExpression.from_object(expected_dict["expr"])
                self.assertEqual(parsed_expr.expr, expected_dict["expr"])

    def test_parse_unexpected_type(self):
        self.assertRaises(TypeError, DynamicExpression.from_object, tuple())

    def test_parse_expression_dict(self):
        for dict_to_parse, expected_dict in zip(self.expressions, self.expected):
            with self.subTest(expression=dict_to_parse):
                parsed_expr = DynamicExpression.from_object(dict_to_parse)
                self.assertEqual(parsed_expr.expr, expected_dict["expr"])
                self.assertEqual(parsed_expr.cond, expected_dict["cond"])

    def test_parse_expression_string(self):
        for tup in EQUATIONS:
            expression = tup.string
            with self.subTest(expression=expression):
                parsed_expr = DynamicExpression.from_object(tup.string)
                self.assertEqual(parsed_expr.expr, tup.sympy)

    def test_substitute_variables(self):
        expression = DynamicExpression.from_object(self.expressions[0])
        free_vars_before = expression.free_variables

        subs_dict = {"Acetaldehyde": -5.0, "Heme": 10.0, "Iron3": 50.0}

        expression.substitute(subs_dict)  # type: ignore
        free_vars_after = expression.free_variables

        self.assertEqual(
            free_vars_after,
            free_vars_before - set([Symbol(k) for k in subs_dict.keys()]),
        )
        self.assertEqual(expression.cond, subs_dict["Acetaldehyde"])

    def test_get_free_variables(self):
        for dict_to_parse, free_vars in zip(
            self.expressions, self.expected_free_variables
        ):
            with self.subTest(expression=dict_to_parse):
                parsed_expr = DynamicExpression.from_object(dict_to_parse)
                self.assertEqual(parsed_expr.free_variables, free_vars)

    def test_expression_equality(self):
        expressions = [
            DynamicExpression(expr=expr)
            for expr in [
                Symbol("X") ** 2 - 1,
                Symbol("Y") ** 2 - 1,
                Symbol("Y") * Symbol("Y") - 1,
                Symbol("Y") * 2 * 3 + 1.0,
                Symbol("Y") * 6 + 2 / 2,
            ]
        ]

        expressions.extend(
            [
                DynamicExpression(expr=expr, cond=cond)
                for expr, cond in [
                    (Symbol("Y") * 2 * 3 + 1, Symbol("A")),
                    (Symbol("Y") * 2 * 3 + 1, Symbol("B")),
                    (Symbol("Y") * 2 * 3 + 1, None),
                ]
            ]
        )

        self.assertNotEqual(expressions[0], expressions[1])
        self.assertEqual(expressions[1], expressions[2])
        self.assertEqual(expressions[3], expressions[4])
        self.assertNotEqual(expressions[5], expressions[6])
        self.assertNotEqual(expressions[5], expressions[7])
        self.assertNotEqual(expressions[6], expressions[7])


class ExchangeFluxEntityTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dynamic_expressions = [
            DynamicExpression.from_object(exp.string) for exp in EQUATIONS
        ]

    def test_exchange_flux_parse(self):
        exchange_flux = DynamicExchangeFlux(
            exchange_flux_id="test_flux",
            lower_bound=self.dynamic_expressions[0],
            upper_bound=self.dynamic_expressions[1],
        )

        self.assertEqual(exchange_flux.lower_bound, self.dynamic_expressions[0])
        self.assertEqual(exchange_flux.upper_bound, self.dynamic_expressions[1])

    def test_exchange_flux_without_id(self):
        eq_lb, eq_ub = self.dynamic_expressions[:2]

        def exchange_dict_factory(x):
            return {"exchange_flux": x, "lower_bound": [eq_lb], "upper_bound": [eq_ub]}

        self.assertRaises(
            ValueError, DynamicExchangeFlux.from_dict, exchange_dict_factory("")
        )
        self.assertRaises(
            ValueError, DynamicExchangeFlux.from_dict, exchange_dict_factory(None)
        )


class DynamicFluxEntityTest(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dynamic_expressions = [
            DynamicExpression.from_object(exp.string) for exp in EQUATIONS
        ]

    def test_parse_dynamic_flux_wo_exchange(self):
        flux_dict = {
            "variable": "test_flux",
            "rhs_expression": self.dynamic_expressions[0].expr,
            "metabolite_id": "test_flux_name",
            "initial_condition": 10.0,
        }
        dflux_without_exchange = ODE(**flux_dict)
        self.assertEqual(
            dflux_without_exchange.rhs_expression, self.dynamic_expressions[0].expr
        )
        self.assertEqual(dflux_without_exchange.variable, "test_flux")
        self.assertEqual(dflux_without_exchange.metabolite_id, "test_flux_name")
        self.assertEqual(dflux_without_exchange.initial_condition, 10.0)

    def test_parse_dynamic_flux_with_exchange(self):
        flux_dict = {
            "variable": "test_flux",
            "rhs_expression": self.dynamic_expressions[0].expr,
            "metabolite_id": "test_flux_name",
            "initial_condition": 10.0,
        }
        dflux_with_exchange = ODE(**flux_dict)
        self.assertEqual(
            dflux_with_exchange.rhs_expression, self.dynamic_expressions[0].expr
        )
        self.assertEqual(dflux_with_exchange.metabolite_id, "test_flux_name")
        self.assertEqual(dflux_with_exchange.variable, "test_flux")
        self.assertEqual(dflux_with_exchange.initial_condition, 10.0)

    def test_piecewise_dynamic_flux(self):
        exp_pw1 = deepcopy(self.dynamic_expressions[0].expr)
        exp_pw2 = deepcopy(self.dynamic_expressions[1].expr)

        flux_dict = {
            "variable": "test_flux_name",
            "metabolite_id": "test_flux_pw",
            "rhs_expression": exp_pw1,
            "initial_condition": 10.0,
        }

        dflux = ODE(**flux_dict)

        self.assertNotIsInstance(dflux.rhs_expression, Piecewise)

        flux_dict["rhs_expression"] = [
            {"expr": exp_pw1, "cond": Symbol("Acetate") > 1.1},
            exp_pw2,
        ]

        dflux = ODE(**flux_dict)
        self.assertIsInstance(dflux.rhs_expression, Piecewise)

    def test_free_variables(self):
        flux_dict = {
            "variable": "test_flux_name",
            "metabolite_id": "test_flux",
            "rhs_expression": self.dynamic_expressions[0].expr,
            "initial_condition": 10.0,
        }
        dflux = ODE(**flux_dict)

        exp_free_vars = set(self.dynamic_expressions[0].expr.free_symbols)

        self.assertEqual(dflux.free_variables, exp_free_vars)

    def test_nested_piecewise_expression(self):
        obj_from_string = ExpressionParser.parse_expression(
            [
                {"expr": "Biomass * (1/Glucose)", "cond": "Glucose <= 10"},
                {
                    "expr": [
                        {"expr": "Biomass * (2/Glucose)", "cond": "Pulse = 1"},
                        {"expr": "Biomass * (3/Glucose)", "cond": "Pulse = 2"},
                    ],
                    "cond": "Glucose > 10",
                },
            ]
        )

        biomass, glucose, pulse = map(Symbol, ["Biomass", "Glucose", "Pulse"])

        obj_from_sympy = Piecewise(
            (biomass * 1 / glucose, glucose <= 10),
            (
                Piecewise(
                    (biomass * 2 / glucose, Eq(pulse, 1)),
                    (biomass * 3 / glucose, Eq(pulse, 2)),
                ),
                glucose > 10,
            ),
        )  # type: ignore

        def glucose_ode_factory(expr: Union[Expr, Piecewise]) -> ODE:
            return ODE(
                variable="Glucose",
                metabolite_id="D-Glucose metabolite",
                rhs_expression=expr,
                initial_condition=10.0,
            )

        self.assertEquals(
            glucose_ode_factory(obj_from_string), glucose_ode_factory(obj_from_sympy)  # type: ignore
        )
