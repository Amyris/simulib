class MissingExchangeFluxException(Exception):
    def __init__(self, missing) -> None:
        self.missing = missing
        self.missing_str = ",".join(list(missing))
        self.message = (
            f"exchange fluxes are missing in the steady-state model: {self.missing_str}"
        )


class UndefinedVariableException(Exception):
    def __init__(self, var_list, var_type):
        self.var_list = var_list
        self.var_type = var_type
        self.message = (
            f"variables {','.join(var_list)} of type {self.var_type} are not solvable."
        )
