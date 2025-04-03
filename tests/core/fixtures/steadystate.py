from itertools import permutations
from typing import Dict, List, Optional, Tuple

import cobra


class CobraModelFactory:
    @staticmethod
    def create_reaction_from_metabolites(
        name: str,
        metabolites: Dict[cobra.Metabolite, float],
        bounds: Tuple[Optional[float], Optional[float]] = (None, None),
    ) -> cobra.Reaction:
        reaction = cobra.Reaction(name, lower_bound=bounds[0], upper_bound=bounds[1])  # type: ignore
        reaction.add_metabolites(metabolites)
        return reaction

    @classmethod
    def create_fully_connected_test_model(cls, metabolite_names: List[str]):
        model = cobra.Model()
        metab_internal, metab_external = [
            [
                cobra.Metabolite(id=f"{name}_{compartment}", compartment=compartment)
                for name in metabolite_names
            ]
            for compartment in ["c", "e"]
        ]

        model.add_metabolites(metab_internal + metab_external)
        reactions = [model.add_boundary(metab) for metab in metab_external]

        reactions.extend(
            [
                cls.create_reaction_from_metabolites(
                    name=f"{internal.id}_transport",
                    metabolites={internal: -1, external: 1},
                    bounds=(None, None),
                )
                for internal, external in zip(metab_internal, metab_external)
            ]
            + [
                cls.create_reaction_from_metabolites(
                    name=f"{substrate.id}_to_{product.id}",
                    metabolites={substrate: -1, product: 1},
                    bounds=(0, None),
                )
                for substrate, product in permutations(metab_internal, 2)
            ]
        )

        model.add_reactions(reactions)
        return model
