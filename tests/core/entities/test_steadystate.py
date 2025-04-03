from unittest import TestCase

import cobra

from simulib.entities.steadystate import Reaction


class SteadyStateEntityTest(TestCase):
    def setUp(self):
        self.model = cobra.Model("test_model")
        metabolite_names = ["X", "Y", "Z"]

        self.metabolites = [cobra.Metabolite(x) for x in metabolite_names]
        self.model.add_metabolites(self.metabolites)

    def test_entity_to_cobra_reaction(self):
        pre_count = len(self.model.reactions)
        reaction_input = Reaction(
            lower_bound=0, upper_bound=1000, id="R_1", metabolites={"X": -1, "Y": 1}
        )

        cobra_reaction = reaction_input.to_cobra_reaction(self.model)
        self.model.add_reactions([cobra_reaction])

        added_reaction = self.model.reactions.get_by_id("R_1")
        self.assertEqual(pre_count + 1, len(self.model.reactions))
        self.assertEqual(added_reaction.id, "R_1")
        self.assertEqual(added_reaction.bounds, (0, 1000))
        self.assertSetEqual(
            set(added_reaction.metabolites.keys()), set(self.metabolites[:2])
        )
