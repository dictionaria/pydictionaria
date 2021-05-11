import unittest
from pydictionaria.concepts import ConceptMap


class MapConcepts(unittest.TestCase):

    def test_sense_not_in_mapping(self):
        mapping = ConceptMap({'sense-1': 'concept-1'})
        sense = {'ID': 'not-sense-1'}
        new_sense = mapping.add_concepticon_id(sense)
        self.assertEqual(sense, new_sense)

    def test_sense_in_mapping(self):
        mapping = ConceptMap({'sense-1': 'concept-1'})
        sense = {'ID': 'sense-1'}
        new_sense = mapping.add_concepticon_id(sense)
        self.assertEqual(new_sense['Concepticon_ID'], 'concept-1')

    def test_dont_overwrite_authors_mapping(self):
        mapping = ConceptMap({'sense-1': 'concept-1'})
        sense = {'ID': 'sense-1', 'Concepticon_ID': 'not-concept-1'}
        new_sense = mapping.add_concepticon_id(sense)
        self.assertEqual(new_sense['Concepticon_ID'], 'not-concept-1')
