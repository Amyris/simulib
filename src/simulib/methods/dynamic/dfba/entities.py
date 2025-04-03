from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from pandas import DataFrame
from pydantic import BaseModel

from simulib.entities.dynamic import DynamicModelInput
from simulib.entities.steadystate import SteadyStateSimulationInput

DEFAULT_ABS_TOLERANCE = 1e-4
DEFAULT_REL_TOLERANCE = 1e-4


class DFBAProblemVariableType(Enum):
    METABOLITE = "metabolite"
    EXCHANGE = "exchange"
    PARAMETER = "parameter"


class DFBASimulationInput(BaseModel):
    """
    A dataclass that holds the required inputs for a dynamic FBA simulation
    """

    steady_state_input: SteadyStateSimulationInput
    dynamic_input: DynamicModelInput


class DFBASimulationStatus(str, Enum):
    FAIL = "Fail"
    INCOMPLETE = "Incomplete"
    COMPLETE = "Successful"
    INVALID = "Invalid"


@dataclass
class DFBASimulationReport:
    """
    A dataclass that generates the report of a dynamic FBA simulation
    Fields:
        tsim: simulation concentration dataframe
        tstop: simulation stop time
        status: simulation status (Fail, Incomplete, Successful, Invalid)
        completion: fraction of time points that were completed
    """

    tmax: float
    tstop: float
    status: DFBASimulationStatus = field(init=False)
    completion: float = field(init=False)
    exception: Optional[Exception] = None

    def __post_init__(self):
        self.__get_status()
        self.__get_completion()

    def __get_status(self):
        if self.tmax == 0:
            self.status = DFBASimulationStatus.FAIL
        elif self.tmax < self.tstop:
            self.status = DFBASimulationStatus.INCOMPLETE
        elif self.tmax == self.tstop:
            self.status = DFBASimulationStatus.COMPLETE
        else:
            self.status = DFBASimulationStatus.INVALID
        return self.status.value

    def __get_completion(self):
        self.completion = self.tmax / self.tstop if self.tstop >= self.tmax else 0
        return self.completion


@dataclass
class DFBASimulationResult:
    """
    A dataclass that holds simulation results from dynamic FBA simulations.

    The concentrations field stores a DataFrame with a time column (simulation time)
    and one column for each metabolite defined in the dynamic model input.
    The values in each of these metabolite columns is the predicted concentration.

    The trajectories field stores a DataFrame with a time column (simulation time)
    and one column for each exchange flux defined in the dynamic model input.

    The status field stores the status of the simulation.

    The report field stores information such as tmax, tstop, the status of the simulation
    and the simulation completion.
    """

    concentrations: DataFrame
    trajectories: DataFrame
    status: DFBASimulationStatus
    report: DFBASimulationReport


class DFBAAlgorithm(str, Enum):
    DIRECT = "direct"
    HARWOOD = "Harwood"


class DFBAODEMethod(str, Enum):
    BDF = "BDF"
    ADAMS = "ADAMS"


class DFBASunmatrix(str, Enum):
    DENSE = "dense"
    SPARSE = "sparse"


class DFBADisplay(str, Enum):
    FULL = "full"
    GLPK = "glpk_only"
    SUNDIALS = "sundials_only"
    NONE = "none"


class DFBASimulationOptions(BaseModel):
    """
    A dataclass that contains parameters needed for a dynamic FBA simulation
    Fields:
        tstart: simulation start time (time unit)
        tstop: simulation stop time (time unit)
        tout: simulation resolution (time unit) - defines the length between data points
        output_fluxes: a list of fluxes in the steady-state model to be displayed as trajectories
        model_setup_func: a function that accepts a single DfbaModel object as a parameter
    """

    tstart: float
    tstop: float
    tout: float
    output_fluxes: List[str]
    rel_tolerance: float = DEFAULT_REL_TOLERANCE
    default_abs_tolerance: float = DEFAULT_ABS_TOLERANCE
    display: DFBADisplay = DFBADisplay.FULL
    algorithm: DFBAAlgorithm = DFBAAlgorithm.HARWOOD
    ode_method: DFBAODEMethod = DFBAODEMethod.BDF
    sunmatrix: DFBASunmatrix = DFBASunmatrix.DENSE
    sunlinsolver: str = "dense"

    def __post_init__(self):
        diff = self.tstop - self.tstart
        return (diff >= 0) and self.tout < diff

    @property
    def model_setup_func(self):
        def return_func(dfba_model, odes):
            tolerance_dict = {
                ode.variable: float(ode.simulation_properties.abs_tolerance)
                for ode in odes
                if ode.simulation_properties.abs_tolerance is not None
            }

            default_value = self.default_abs_tolerance
            ordered_vars = [kv.id for kv in dfba_model.kinetic_variables]
            tolerance_vector = [
                tolerance_dict.get(var, default_value) for var in ordered_vars
            ]

            dfba_model.solver_data.set_abs_tolerance(tolerance_vector)
            dfba_model.solver_data.set_algorithm(self.algorithm.value)
            dfba_model.solver_data.set_display(self.display.value)
            dfba_model.solver_data.set_ode_method(self.ode_method.value)
            dfba_model.solver_data.set_rel_tolerance(self.rel_tolerance)
            dfba_model.solver_data.set_sunmatrix(self.sunmatrix.value)
            dfba_model.solver_data.set_sunlinsolver(self.sunmatrix.value)

            return dfba_model

        return return_func
