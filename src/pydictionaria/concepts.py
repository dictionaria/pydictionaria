from copy import copy

from csvw import dsv


class ConceptMap:
    """Add Concepticon IDs to senses from a separate file."""

    def __init__(self, concept_map):
        self._concept_map = concept_map

    @classmethod
    def from_csv(cls, csv_file, **kwargs):
        """Create concept map from a CSV file.

        The CSV must at least contain the following three columns:

         * ``sense_id``: ID of the sense
         * ``concepticon_id``: Concepticon ID of the sense's comparison meaning
         * ``include``: Must be ``1`` if the row is to included in the mapping.
            Rows containing any other value for ``include`` are ignored.

        :param csv_file: file name of the csv file
        :param kwargs: see `csvw.dsv.reader`
        """
        if csv_file.exists():
            mapping = {
                row['sense_id']: row['concepticon_id']
                for row in dsv.reader(csv_file, dicts=True, **kwargs)
                if (row.get('sense_id')
                    and row.get('concepticon_id')
                    and row.get('include') == '1')}
        else:
            mapping = {}
        return cls(mapping)

    def add_concepticon_id(self, sense):
        """Return new sense with an added Concepticon ID."""
        sense_id = sense.get('ID')
        if not sense.get('Concepticon_ID') and sense_id in self._concept_map:
            new_sense = copy(sense)
            new_sense['Concepticon_ID'] = self._concept_map[sense_id]
            return new_sense
        else:
            return sense
