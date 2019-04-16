# coding: utf8
from __future__ import unicode_literals, print_function, division

import unittest
from unittest.mock import Mock

from pydictionaria.formats import sfm_lib
from clldutils.sfm import Entry


def test_split_join():
    from pydictionaria.formats.sfm_lib import split, join

    assert split(join(['a', 'b'])) == ['a', 'b']


def test_Entry():
    from pydictionaria.formats.sfm_lib import Entry

    e = Entry.from_string("""
\\lx lexeme
\\hm 1
\\marker value
""")
    assert e.id == 'lexeme 1'
    e.upsert('marker', 'new value')
    assert e.get('marker') == 'new value'
    e.upsert('new_marker', 'value')
    assert e.get('new_marker') == 'value'


def test_ComparisonMeanings(mocker):
    from pydictionaria.formats.sfm_lib import Entry, ComparisonMeanings

    class Concepticon(object):
        conceptsets = {1: mocker.Mock(id='1', gloss='gloss', definition='definition')}

        def lookup(self, *args, **kw):
            return [[(None, 1)]]

    cm = ComparisonMeanings(Concepticon())
    e = Entry([('lx', 'lexeme'), ('de', 'meaning')])
    cm(e)
    assert 'gloss' in e.get('zcom2')
    e = Entry([('lx', 'lexeme'), ('ge', 'gl.oss')])
    cm(e)
    assert 'gloss' in e.get('zcom2')


def test_Check(mocker):
    from pydictionaria.formats.sfm_lib import Entry, Check

    error, warn = mocker.Mock(), mocker.Mock()
    mocker.patch.multiple('pydictionaria.formats.sfm_lib', error=error, warn=warn)
    entries = [Entry([('lx', 'lexeme')])]
    chk = Check(entries)
    assert not error.called
    chk(entries[0])
    assert error.called

    error, warn = mocker.Mock(), mocker.Mock()
    mocker.patch.multiple('pydictionaria.formats.sfm_lib', error=error, warn=warn)
    Check([Entry([('lx', 'lexeme')]), Entry([('lx', 'lexeme')])])
    assert error.called


class ExampleExtraction(unittest.TestCase):

    def test_separate_examples_from_entry(self):
        example_markers = {'xv', 'xe'}
        extractor = sfm_lib.ExampleExtractor(example_markers, {}, Mock())
        entry = Entry([
            ('lx', 'headword'),
            ('xv', 'primary text'),
            ('xe', 'translation'),
            ('dt', 'time stamp')])
        new_entry = extractor(entry)
        examples = list(extractor.examples.values())
        example = examples[0]
        self.assertEqual(new_entry, [
            ('lx', 'headword'),
            ('xref', example.id),
            ('dt', 'time stamp')])

    def test_marker_mapping(self):
        example_markers = {'xv', 'xe'}
        extractor = sfm_lib.ExampleExtractor(example_markers, {}, Mock())
        entry = Entry([
            ('lx', 'headword'),
            ('xv', 'primary text'),
            ('xe', 'translation')])
        extractor(entry)
        examples = list(extractor.examples.values())
        example = examples[0]
        self.assertEqual(example, [
            ('ref', example.id),
            ('tx', 'primary text'),
            ('ft', 'translation'),
            ('lemma', 'headword')])

    def test_generation_of_lemma_marker(self):
        # Side Question: Is it bad that the lemma marker is appended to the end?
        example_markers = {'xv', 'xe'}
        extractor = sfm_lib.ExampleExtractor(example_markers, {}, Mock())
        entry = Entry([
            ('lx', 'headword'),
            ('xv', 'primary text'),
            ('xe', 'translation')])
        extractor(entry)
        examples = list(extractor.examples.values())
        example = examples[0]
        self.assertEqual(example, [
            ('ref', example.id),
            ('tx', 'primary text'),
            ('ft', 'translation'),
            ('lemma', 'headword')])

    def test_merging_of_lemma_marker(self):
        example_markers = {'lemma', 'xv', 'xe'}
        extractor = sfm_lib.ExampleExtractor(example_markers, {}, Mock())
        entry = Entry([
            ('lx', 'headword'),
            ('lemma', 'other_headword'),
            ('xv', 'primary text'),
            ('xe', 'translation')])
        extractor(entry)
        examples = list(extractor.examples.values())
        example = examples[0]
        self.assertEqual(example, [
            ('ref', example.id),
            ('lemma', 'other_headword ; headword'),
            ('tx', 'primary text'),
            ('ft', 'translation')])

    def test_multiple_examples(self):
        example_markers = {'xv', 'xe'}
        extractor = sfm_lib.ExampleExtractor(example_markers, {}, Mock())
        entry = Entry([
            ('lx', 'headword'),
            ('xv', 'primary text 1'),
            ('xe', 'translation 1'),
            ('xv', 'primary text 2'),
            ('xe', 'translation 2'),
            ('xv', 'primary text 3'),
            ('xe', 'translation 3')])
        extractor(entry)
        examples = list(extractor.examples.values())
        example1 = examples[0]
        self.assertEqual(example1, [
            ('ref', example1.id),
            ('tx', 'primary text 1'),
            ('ft', 'translation 1'),
            ('lemma', 'headword')])
        example2 = examples[1]
        self.assertEqual(example2, [
            ('ref', example2.id),
            ('tx', 'primary text 2'),
            ('ft', 'translation 2'),
            ('lemma', 'headword')])
        example3 = examples[2]
        self.assertEqual(example3, [
            ('ref', example3.id),
            ('tx', 'primary text 3'),
            ('ft', 'translation 3'),
            ('lemma', 'headword')])

    def test_there_might_be_stuff_before_xv(self):
        example_markers = {'rf', 'xv', 'xe'}
        extractor = sfm_lib.ExampleExtractor(example_markers, {}, Mock())
        entry = Entry([
            ('lx', 'headword'),
            ('rf', 'source 1'),
            ('xv', 'primary text 1'),
            ('xe', 'translation 1'),
            ('rf', 'source 2'),
            ('xv', 'primary text 2'),
            ('xe', 'translation 2'),
            ('rf', 'source 3'),
            ('xv', 'primary text 3'),
            ('xe', 'translation 3')])
        extractor(entry)
        examples = list(extractor.examples.values())
        example1 = examples[0]
        self.assertEqual(example1, [
            ('ref', example1.id),
            ('rf', 'source 1'),
            ('tx', 'primary text 1'),
            ('ft', 'translation 1'),
            ('lemma', 'headword')])
        example2 = examples[1]
        self.assertEqual(example2, [
            ('ref', example2.id),
            ('rf', 'source 2'),
            ('tx', 'primary text 2'),
            ('ft', 'translation 2'),
            ('lemma', 'headword')])
        example3 = examples[2]
        self.assertEqual(example3, [
            ('ref', example3.id),
            ('rf', 'source 3'),
            ('tx', 'primary text 3'),
            ('ft', 'translation 3'),
            ('lemma', 'headword')])

    def test_there_might_be_stuff_after_xe(self):
        example_markers = {'xv', 'xe', 'z0'}
        extractor = sfm_lib.ExampleExtractor(example_markers, {}, Mock())
        entry = Entry([
            ('lx', 'headword'),
            ('xv', 'primary text 1'),
            ('xe', 'translation 1'),
            ('z0', 'gloss ref 1'),
            ('xv', 'primary text 2'),
            ('xe', 'translation 2'),
            ('z0', 'gloss ref 2'),
            ('xv', 'primary text 3'),
            ('xe', 'translation 3'),
            ('z0', 'gloss ref 3')])
        extractor(entry)
        examples = list(extractor.examples.values())
        example1 = examples[0]
        self.assertEqual(example1, [
            ('ref', example1.id),
            ('tx', 'primary text 1'),
            ('ft', 'translation 1'),
            ('z0', 'gloss ref 1'),
            ('lemma', 'headword')])
        example2 = examples[1]
        self.assertEqual(example2, [
            ('ref', example2.id),
            ('tx', 'primary text 2'),
            ('ft', 'translation 2'),
            ('z0', 'gloss ref 2'),
            ('lemma', 'headword')])
        example3 = examples[2]
        self.assertEqual(example3, [
            ('ref', example3.id),
            ('tx', 'primary text 3'),
            ('ft', 'translation 3'),
            ('z0', 'gloss ref 3'),
            ('lemma', 'headword')])

    def test_merge_glosses(self):
        example_markers = {'xv', 'xvm', 'xeg', 'xe'}
        extractor = sfm_lib.ExampleExtractor(example_markers, {}, Mock())
        entry = Entry([
            ('lx', 'headword'),
            ('xv', 'primary text 1'),
            ('xe', 'translation 1'),
            ('xv', 'primary text 2a'),
            ('xvm', 'analyzed word 2a'),
            ('xeg', 'glossed word 2a'),
            ('xv', 'primary text 2b'),
            ('xvm', 'analyzed word 2b'),
            ('xeg', 'glossed word 2b'),
            ('xv', 'primary text 2c'),
            ('xvm', 'analyzed word 2c'),
            ('xeg', 'glossed word 2c'),
            ('xe', 'translation 2'),
            ('xv', 'primary text 3'),
            ('xe', 'translation 3')])
        extractor(entry)
        examples = list(extractor.examples.values())
        example1 = examples[0]
        self.assertEqual(example1, [
            ('ref', example1.id),
            ('tx', 'primary text 1'),
            ('ft', 'translation 1'),
            ('lemma', 'headword')])
        example2 = examples[1]
        self.assertEqual(example2, [
            ('ref', example2.id),
            ('tx', 'primary text 2a primary text 2b primary text 2c'),
            ('mb', 'analyzed word 2a analyzed word 2b analyzed word 2c'),
            ('gl', 'glossed word 2a glossed word 2b glossed word 2c'),
            ('ft', 'translation 2'),
            ('lemma', 'headword')])
        example3 = examples[2]
        self.assertEqual(example3, [
            ('ref', example3.id),
            ('tx', 'primary text 3'),
            ('ft', 'translation 3'),
            ('lemma', 'headword')])

    def test_missing_xe(self):
        example_markers = {'xv', 'xe'}
        log = Mock()
        extractor = sfm_lib.ExampleExtractor(example_markers, {}, log)
        entry = Entry([
            ('lx', 'headword'),
            ('xv', 'primary text 1'),
            ('xe', 'translation 1'),
            ('xv', 'primary text 2'),
            ('xv', 'primary text 3'),
            ('xe', 'translation 3')])

        extractor(entry)

        examples = list(extractor.examples.values())
        example1 = examples[0]
        self.assertEqual(example1, [
            ('ref', example1.id),
            ('tx', 'primary text 1'),
            ('ft', 'translation 1'),
            ('lemma', 'headword')])
        example3 = examples[1]
        self.assertEqual(example3, [
            ('ref', example3.id),
            ('tx', 'primary text 3'),
            ('ft', 'translation 3'),
            ('lemma', 'headword')])

        with self.assertRaises(AssertionError):
            log.write.assert_not_called()


    def test_two_xv_markers_at_the_beginning(self):
        example_markers = {'rf', 'xv', 'xe'}
        log = Mock()
        extractor = sfm_lib.ExampleExtractor(example_markers, {}, log)
        entry = Entry([
            ('lx', 'headword'),
            ('rf', 'source 1'),
            ('xv', 'primary text 1'),
            ('xe', 'translation 1'),
            ('rf', 'source 2'),
            ('xe', 'translation 2'),
            ('rf', 'source 3'),
            ('xv', 'primary text 3'),
            ('xe', 'translation 3')])

        extractor(entry)

        examples = list(extractor.examples.values())
        example1 = examples[0]
        self.assertEqual(example1, [
            ('ref', example1.id),
            ('rf', 'source 1'),
            ('tx', 'primary text 1'),
            ('ft', 'translation 1'),
            ('lemma', 'headword')])
        example3 = examples[1]
        self.assertEqual(example3, [
            ('ref', example3.id),
            ('rf', 'source 3'),
            ('tx', 'primary text 3'),
            ('ft', 'translation 3'),
            ('lemma', 'headword')])

        with self.assertRaises(AssertionError):
            log.write.assert_not_called()

    def test_missing_beginning(self):
        example_markers = {'rf', 'xv', 'xe', 'other_marker'}
        log = Mock()
        extractor = sfm_lib.ExampleExtractor(example_markers, {}, log)
        entry = Entry([
            ('lx', 'headword'),
            ('xv', 'primary text 1'),
            ('other_marker', 'other marker 1'),
            ('xe', 'translation 1'),
            ('other_marker', 'other marker 2'),
            ('xe', 'translation 2'),
            ('xv', 'primary text 3'),
            ('other_marker', 'other marker 3'),
            ('xe', 'translation 3')])

        extractor(entry)

        examples = list(extractor.examples.values())
        example1 = examples[0]
        self.assertEqual(example1, [
            ('ref', example1.id),
            ('tx', 'primary text 1'),
            ('other_marker', 'other marker 1'),
            ('ft', 'translation 1'),
            # Note: trailing stuff ends up in the previous example, because we
            # never know, when an example *truly* ends
            ('other_marker', 'other marker 2'),
            ('lemma', 'headword')])
        example3 = examples[1]
        self.assertEqual(example3, [
            ('ref', example3.id),
            ('tx', 'primary text 3'),
            ('other_marker', 'other marker 3'),
            ('ft', 'translation 3'),
            ('lemma', 'headword')])

        with self.assertRaises(AssertionError):
            log.write.assert_not_called()
