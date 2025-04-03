from typing import Dict, List, Optional

import cobra
from pydantic import BaseModel


class BoundedEntity(BaseModel):
    """
    A dataclass that represents numerical lower and upper bounds for a flux.
    """

    lower_bound: Optional[float]
    upper_bound: Optional[float]


class Reaction(BoundedEntity):
    """
    A dataclass that represents a steady-state reaction
    Exclusive fields:
        id: the string identifier for this reaction
        metabolites: a dictionary mapping metabolite names to their stoichiometric coefficients
            in this reaction
    """

    id: str
    metabolites: Dict[str, float]

    def to_cobra_reaction(self, model: cobra.Model) -> cobra.Reaction:
        """
        Returns a cobra Reaction object that uses metabolites from the supplied model parameter
        """
        reaction = cobra.Reaction(
            id=self.id,
            name=self.id,
            lower_bound=self.lower_bound,  # type: ignore
            upper_bound=self.upper_bound,
        )
        reaction.add_metabolites(
            {
                model.metabolites.get_by_id(metab_name): coef
                for metab_name, coef in self.metabolites.items()
            }  # type: ignore
        )

        return reaction


class ReactionConstraint(BoundedEntity):
    reaction_id: str


class SteadyStateSimulationInput(BaseModel):
    model: cobra.Model
    added_reactions: Optional[List[Reaction]] = None
    reaction_constraints: Optional[List[ReactionConstraint]] = None

    class Config:
        arbitrary_types_allowed = True
