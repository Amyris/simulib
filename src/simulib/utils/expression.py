import logging
from copy import copy
from numbers import Number
from typing import Any, Dict, List, Optional, Tuple, Union

import sympy
from sympy.parsing.sympy_parser import convert_equals_signs, standard_transformations

ValueOrExpr = Union[float, sympy.Expr, sympy.Basic, sympy.Symbol]

logger = logging.getLogger(__name__)


def simplify_expression_set(expression_dict: Dict[str, ValueOrExpr]):
    is_different = True
    old_subbed = copy(expression_dict)
    new_subbed = {}

    while is_different:
        for k in old_subbed.keys():
            v = old_subbed[k]
            new_subbed[k] = v.subs(old_subbed) if isinstance(v, sympy.Expr) else v
        is_different = new_subbed != old_subbed
        if is_different:
            old_subbed = copy(new_subbed)
            new_subbed = {}

    return new_subbed


def parse_string(string: str) -> sympy.Expr:
    return sympy.parse_expr(
        string,
        transformations=standard_transformations + (convert_equals_signs,),
        evaluate=True,
    )


def parse_number(number: Number) -> sympy.Expr:
    return sympy.Float(number)


def parse_sympy_expression(expr: sympy.Expr) -> sympy.Expr:
    return expr


EXPRESSION_PARSERS = {
    str: parse_string,  
    Number: parse_number,
    sympy.Expr: parse_sympy_expression,
    sympy.core.relational.Relational: parse_sympy_expression,
}


class ExpressionParser:
    ATOMIC_EXPRESSION_TYPES = tuple(EXPRESSION_PARSERS)

    @classmethod
    def parse_single_expression(cls, obj: Any) -> sympy.Expr:
        for type_, parse_function in EXPRESSION_PARSERS.items():
            if isinstance(obj, type_):
                return parse_function(obj)
        try:
            return sympy.Expr(float(obj))
        except Exception:
            raise ValueError(f"{obj} is not in a valid format for parsing.")

    @classmethod
    def parse_single_piecewise_expression(
        cls, obj: Dict[str, Any]
    ) -> Tuple[sympy.Expr, Optional[sympy.Expr]]:
        expr, cond = (obj.get(k) for k in ("expr", "cond"))
        return cls.parse_expression(expr), cls.parse_expression(cond)

    @classmethod
    def parse_piecewise_expression_from_list(cls, obj: List[Any]) -> sympy.Piecewise:
        expressions_to_merge = []
        for expression in obj:
            if isinstance(expression, dict):
                expr, cond = cls.parse_single_piecewise_expression(expression)
                if isinstance(cond, (Number)):
                    cond = bool(cond)
            else:
                expr, cond = cls.parse_expression(expression), True
            expressions_to_merge.append((expr, cond))
        return sympy.Piecewise(*expressions_to_merge)

    @classmethod
    def parse_expression(cls, obj: Any) -> sympy.Expr:
        # can't use "if obj" here since obj can be a Relational
        # which has an ambiguous truth value
        if isinstance(obj, list) and obj:
            return cls.parse_piecewise_expression_from_list(obj)
        elif isinstance(obj, cls.ATOMIC_EXPRESSION_TYPES):
            return cls.parse_single_expression(obj)
        else:
            raise TypeError(
                f"{obj} of type {type(obj)} is not a valid part of a piecewise expression"
            )


class ExpressionWriter:
    @classmethod
    def __write_piecewise_expression_to_list(cls, expr: sympy.Piecewise):
        piecewise_as_list = []
        for argi in expr.args:
            pw_expr, pw_cond = argi  # type: ignore
            if pw_cond != sympy.logic.boolalg.BooleanTrue:
                pw_element = {
                    "expr": cls.write_expression(pw_expr),
                    "cond": cls.write_expression(pw_cond),
                }
            else:
                pw_element = cls.write_expression(pw_expr)
            piecewise_as_list.append(pw_element)
        return piecewise_as_list

    @classmethod
    def __write_expression_to_string(cls, expr: sympy.Expr):
        return str(expr)

    @classmethod
    def write_expression(cls, expr: Union[sympy.Piecewise, sympy.Expr]):
        if isinstance(expr, sympy.Piecewise):
            return cls.__write_piecewise_expression_to_list(expr)
        elif isinstance(
            expr, (sympy.Expr, sympy.core.relational.Relational, sympy.Basic)
        ):
            return cls.__write_expression_to_string(expr)
        elif isinstance(expr, (Number, str)):
            return expr
        else:
            raise TypeError(f"cannot write expressions of type {type(expr)}.")


PYDANTIC_ENCODERS = {
    sympy.Expr: ExpressionWriter.write_expression,
    ValueOrExpr: ExpressionWriter.write_expression,
    sympy.logic.boolalg.Boolean: bool,
    sympy.Symbol: str,
}
