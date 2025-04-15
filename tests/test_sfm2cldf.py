import unittest
import pydictionaria.sfm2cldf as s
from clldutils import sfm


class SplitMarkersWithSeparators(unittest.TestCase):

    def test_lump_everything_together_if_seperator_isnt_found(self):
        sep = 'sep'
        input_markers = [
            ('marker1', 'value1'),
            ('marker2', 'value2')]
        expected = [
            [('marker1', 'value1'), ('marker2', 'value2')]]
        self.assertEqual(
            list(s.group_by_separator(sep, input_markers)),
            expected)

    def test_split_groups_on_separator(self):
        sep = 'sep'
        input_markers = [
            ('marker1', 'value1'),
            ('sep', 'value'),
            ('marker2', 'value2')]
        expected = [
            [('marker1', 'value1')],
            [('sep', 'value'), ('marker2', 'value2')]]
        self.assertEqual(
            list(s.group_by_separator(sep, input_markers)),
            expected)


class SplitListByPredicate(unittest.TestCase):

    def test_no_element_matches_pred(self):
        def iseven(x):
            return x % 2 == 0
        elements = [1, 3, 5]
        even, odd = s.split_by_pred(iseven, elements)
        self.assertEqual(even, [])
        self.assertEqual(odd, [1, 3, 5])

    def test_all_elements_match_pred(self):
        def iseven(x):
            return x % 2 == 0
        elements = [2, 4, 6]
        even, odd = s.split_by_pred(iseven, elements)
        self.assertEqual(even, [2, 4, 6])
        self.assertEqual(odd, [])

    def test_some_elements_match_pred(self):
        def iseven(x):
            return x % 2 == 0
        elements = [1, 2, 3, 4]
        even, odd = s.split_by_pred(iseven, elements)
        self.assertEqual(even, [2, 4])
        self.assertEqual(odd, [1, 3])


class GenerateSequentialIDs(unittest.TestCase):

    def test_sequence_starts_with_one(self):
        gen = s.IDGenerator()
        first_id = gen.next_id()
        self.assertEqual(first_id, '000001')

    def test_sequence_counts_up(self):
        gen = s.IDGenerator()
        first_id = gen.next_id()
        second_id = gen.next_id()
        self.assertEqual(first_id, '000001')
        self.assertEqual(second_id, '000002')

    def test_adding_prefix(self):
        gen = s.IDGenerator('PRE')
        first_id = gen.next_id()
        second_id = gen.next_id()
        self.assertEqual(first_id, 'PRE000001')
        self.assertEqual(second_id, 'PRE000002')


class LinkProcessing(unittest.TestCase):

    def setUp(self):
        id_index = {
            'OLDID1': 'NEWID1',
            'OLDID2': 'NEWID2',
            'OLDID3': 'NEWID3'}
        label_index = {
            'NEWID1': 'label 1',
            'NEWID2': 'label 2',
            'NEWID3': 'label 3'}
        link_markers = {'linkmarker1', 'linkmarker2'}
        link_regex = r'\bOLDID\d+\b'
        self.link_processor = s.LinkProcessor(
            id_index, label_index, link_markers, link_regex)

    def test_entries_without_links_dont_change(self):
        original_entry = sfm.Entry([
            ('linkmarker1', 'no link'),
            ('linkmarker2', 'no link'),
            ('othermarker', 'no link')])
        expected = sfm.Entry([
            ('linkmarker1', 'no link'),
            ('linkmarker2', 'no link'),
            ('othermarker', 'no link')])
        new_entry = self.link_processor(original_entry)
        self.assertEqual(new_entry, expected)

    def test_single_link_is_replaced(self):
        original_entry = sfm.Entry([
            ('linkmarker1', 'no link'),
            ('linkmarker2', 'link: OLDID1'),
            ('othermarker', 'no link')])
        expected = sfm.Entry([
            ('linkmarker1', 'no link'),
            ('linkmarker2', 'link: [label 1](NEWID1)'),
            ('othermarker', 'no link')])
        new_entry = self.link_processor(original_entry)
        self.assertEqual(new_entry, expected)

    def test_links_in_different_markers_are_replaced(self):
        original_entry = sfm.Entry([
            ('linkmarker1', 'link: OLDID2'),
            ('linkmarker2', 'link: OLDID1'),
            ('othermarker', 'no link')])
        expected = sfm.Entry([
            ('linkmarker1', 'link: [label 2](NEWID2)'),
            ('linkmarker2', 'link: [label 1](NEWID1)'),
            ('othermarker', 'no link')])
        new_entry = self.link_processor(original_entry)
        self.assertEqual(new_entry, expected)

    def test_links_in_same_marker_are_replaced(self):
        original_entry = sfm.Entry([
            ('linkmarker1', 'no link'),
            ('linkmarker2', 'link 1: OLDID1; link 2: OLDID2'),
            ('othermarker', 'no link')])
        expected = sfm.Entry([
            ('linkmarker1', 'no link'),
            ('linkmarker2', 'link 1: [label 1](NEWID1); link 2: [label 2](NEWID2)'),
            ('othermarker', 'no link')])
        new_entry = self.link_processor(original_entry)
        self.assertEqual(new_entry, expected)

    def test_same_link_twice_in_the_same_marker(self):
        original_entry = sfm.Entry([
            ('linkmarker1', 'no link'),
            ('linkmarker2', 'link 1: OLDID1; link 2: OLDID1'),
            ('othermarker', 'no link')])
        expected = sfm.Entry([
            ('linkmarker1', 'no link'),
            ('linkmarker2', 'link 1: [label 1](NEWID1); link 2: [label 1](NEWID1)'),
            ('othermarker', 'no link')])
        new_entry = self.link_processor(original_entry)
        self.assertEqual(new_entry, expected)

    def test_only_process_links_in_specified_markers(self):
        original_entry = sfm.Entry([
            ('linkmarker1', 'no link'),
            ('linkmarker2', 'link: OLDID1'),
            ('othermarker', 'link: OLDID2')])
        expected = sfm.Entry([
            ('linkmarker1', 'no link'),
            ('linkmarker2', 'link: [label 1](NEWID1)'),
            ('othermarker', 'link: OLDID2')])
        new_entry = self.link_processor(original_entry)
        self.assertEqual(new_entry, expected)

    def test_ignore_regex_matches_that_are_not_in_the_index(self):
        original_entry = sfm.Entry([
            ('linkmarker1', 'no link'),
            ('linkmarker2', 'link: OLDID1000'),
            ('othermarker', 'no link')])
        expected = sfm.Entry([
            ('linkmarker1', 'no link'),
            ('linkmarker2', 'link: OLDID1000'),
            ('othermarker', 'no link')])
        new_entry = self.link_processor(original_entry)
        self.assertEqual(new_entry, expected)

    def test_dont_mutate_original_entry(self):
        original_entry = sfm.Entry([
            ('linkmarker1', 'no link'),
            ('linkmarker2', 'link: OLDID1'),
            ('othermarker', 'no link')])
        expected = sfm.Entry([
            ('linkmarker1', 'no link'),
            ('linkmarker2', 'link: OLDID1'),
            ('othermarker', 'no link')])
        _ = self.link_processor(original_entry)
        self.assertEqual(original_entry, expected)

    def test_carry_over_attributes(self):
        original_entry = sfm.Entry([
            ('linkmarker1', 'no link'),
            ('linkmarker2', 'link: OLDID1'),
            ('othermarker', 'no link')])
        original_entry.id = 'I have an ID, too!'
        expected = sfm.Entry([
            ('linkmarker1', 'no link'),
            ('linkmarker2', 'link: [label 1](NEWID1)'),
            ('othermarker', 'no link')])
        expected.id = 'I have an ID, too!'
        new_entry = self.link_processor(original_entry)
        self.assertEqual(new_entry, expected)


class MediaCaptionExtraction(unittest.TestCase):

    def test_find_caption(self):
        entry = sfm.Entry([
            ('marker1', 'val1'),
            ('pc', 'image-name'),
            ('cap', 'caption'),
            ('marker2', 'val2')])
        caption_finder = s.CaptionFinder(['pc'], 'cap')
        _ = caption_finder(entry)
        expected = {'image-name': 'caption'}
        self.assertEqual(caption_finder.captions, expected)

    def test_find_multiple_captions(self):
        entry = sfm.Entry([
            ('marker1', 'val1'),
            ('pc', 'image1-name'),
            ('cap', 'caption1'),
            ('marker2', 'val2'),
            ('pc', 'image2-name'),
            ('cap', 'caption2'),
            ('marker3', 'val3')])
        caption_finder = s.CaptionFinder(['pc'], 'cap')
        _ = caption_finder(entry)
        expected = {
            'image1-name': 'caption1',
            'image2-name': 'caption2'}
        self.assertEqual(caption_finder.captions, expected)

    def test_captions_need_to_be_adjacent(self):
        entry = sfm.Entry([
            ('marker1', 'val1'),
            ('pc', 'image-name'),
            ('marker2', 'val2'),
            ('cap', 'caption'),
            ('marker3', 'val3')])
        caption_finder = s.CaptionFinder(['pc'], 'cap')
        _ = caption_finder(entry)
        expected = {}
        self.assertEqual(caption_finder.captions, expected)


class MapSfmToCldf(unittest.TestCase):

    def setUp(self):
        self.mapping = {'marker1': 'Column1', 'marker2': 'Column2'}

    def test_map_id(self):
        sfm_entry = sfm.Entry()
        sfm_entry.id = 'id1'
        cldf_row = s.sfm_entry_to_cldf_row(None, self.mapping, {}, set(), sfm_entry)
        self.assertEqual(cldf_row, {'ID': 'id1'})

    def test_map_columns(self):
        sfm_entry = sfm.Entry([('marker1', 'value1'), ('marker2', 'value2')])
        sfm_entry.id = 'id1'
        cldf_row = s.sfm_entry_to_cldf_row(None, self.mapping, {}, set(), sfm_entry)
        self.assertEqual(
            cldf_row,
            {'ID': 'id1', 'Column1': 'value1', 'Column2': 'value2'})

    def test_ignore_unexpected_sfm_markers(self):
        sfm_entry = sfm.Entry([('marker1', 'value1'), ('unknown', 'value2')])
        sfm_entry.id = 'id1'
        cldf_row = s.sfm_entry_to_cldf_row(None, self.mapping, {}, set(), sfm_entry)
        self.assertEqual(
            cldf_row,
            {'ID': 'id1', 'Column1': 'value1'})

    def test_map_entry_id(self):
        sfm_entry = sfm.Entry([('marker1', 'value1')])
        sfm_entry.id = 'id1'
        sfm_entry.entry_id = 'entry1'
        cldf_row = s.sfm_entry_to_cldf_row(None, self.mapping, {}, set(), sfm_entry)
        self.assertEqual(
            cldf_row,
            {'ID': 'id1', 'Column1': 'value1', 'Entry_ID': 'entry1'})

    def test_map_sense_ids(self):
        sfm_entry = sfm.Entry([('marker1', 'value1')])
        sfm_entry.id = 'id1'
        sfm_entry.sense_ids = ['sense1', 'sense2']
        cldf_row = s.sfm_entry_to_cldf_row(None, self.mapping, {}, set(), sfm_entry)
        self.assertEqual(
            cldf_row,
            {'ID': 'id1', 'Column1': 'value1', 'Sense_IDs': ['sense1', 'sense2']})

    def test_map_language_id(self):
        sfm_entry = sfm.Entry([('marker1', 'value1')])
        sfm_entry.id = 'id1'
        sfm_entry.sense_ids = ['sense1', 'sense2']
        cldf_row = s.sfm_entry_to_cldf_row(None, self.mapping, {}, set(), sfm_entry, 'lang1')
        self.assertEqual(
            cldf_row,
            {'ID': 'id1', 'Column1': 'value1', 'Sense_IDs': ['sense1', 'sense2'], 'Language_ID': 'lang1'})

    def test_map_media_ids(self):
        sfm_entry = sfm.Entry([('marker1', 'value1')])
        sfm_entry.id = 'id1'
        sfm_entry.media_ids = ['file1', 'file2']
        cldf_row = s.sfm_entry_to_cldf_row(None, self.mapping, {}, set(), sfm_entry)
        self.assertEqual(
            cldf_row,
            {'ID': 'id1', 'Column1': 'value1', 'Media_IDs': ['file1', 'file2']})


def test_gloss():
    sfm_entry = sfm.Entry([('ge', 'abc\tdef')])
    cldf_row = s.sfm_entry_to_cldf_row(None, {'ge': 'Gloss'}, {}, set(), sfm_entry)
    assert cldf_row['Gloss'] == 'abc\tdef'
    cldf_row = s.sfm_entry_to_cldf_row('ExampleTable', {'ge': 'Gloss'}, {}, set(), sfm_entry)
    assert cldf_row['Gloss'] == ['abc', 'def']


def test_cf():
    sfm_entry = sfm.Entry([('cf', 'val1'), ('cf', 'val2;val3')])
    cldf_row = s.sfm_entry_to_cldf_row('EntryTable', {'cf': 'Entry_IDs'}, {}, {'Entry_IDs'}, sfm_entry)
    assert cldf_row['Entry_IDs'] == ['val1', 'val2', 'val3']


def test_multimarkers():
    sfm_entry = sfm.Entry([('cf', 'val1'), ('cf', 'val2')])
    cldf_row = s.sfm_entry_to_cldf_row(None, {'cf': 'See_Also'}, {}, set(), sfm_entry)
    assert cldf_row['See_Also'] == 'val1 ; val2'
