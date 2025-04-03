from unittest import TestCase

from yaml import safe_load

from simulib.utils.expression import ExpressionParser, simplify_expression_set


class SimplifyExpressionTestCase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        with open("./resources/test/models/yaml/test_expression_set.yaml", "r") as f:
            cls.expression_set = safe_load(f)
        with open(
            "./resources/test/models/yaml/test_expression_set_with_piecewise.yaml", "r"
        ) as f:
            cls.expression_set_with_piecewise = safe_load(f)

        cls.OTR = "OTR"
        cls.test_variable = "test_variable"
        cls.simplified_OTR = ExpressionParser.parse_expression("1.0 - 1.0*Oxygen")
        cls.simplified_test_variable = ExpressionParser.parse_expression(
            [
                {
                    "expr": "2*Biomass",
                    "cond": "Biomass < 1.0",
                },
                {
                    "expr": "0.5*Biomass",
                    "cond": "Biomass >= 1.0",
                },
            ]
        )

    def test_simplify_expression_set(self):
        variable_definitions = {
            k: ExpressionParser.parse_expression(v)
            for k, v in self.expression_set.items()
        }
        simplified_definitions = simplify_expression_set(variable_definitions)  # type: ignore
        self.assertEqual(simplified_definitions.get(self.OTR), self.simplified_OTR)

    def test_simplify_expression_set_with_piecewise(self):
        variable_definitions = {
            k: ExpressionParser.parse_expression(v)
            for k, v in self.expression_set_with_piecewise.items()
        }
        simplified_definitions = simplify_expression_set(variable_definitions)  # type: ignore
        self.assertEqual(
            simplified_definitions.get(self.test_variable),
            self.simplified_test_variable,
        )
