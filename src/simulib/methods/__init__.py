import abc

from simulib.entities import SimulatorInput


class MetabolicSimulator:
    __metaclass__ = abc.ABCMeta
    input_class = SimulatorInput

    @abc.abstractmethod
    def simulate(self, input: input_class, **options):
        pass
