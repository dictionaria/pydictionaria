import unittest
import xml.etree.ElementTree as ET

import pydictionaria.flextext as f


class ParseItemTag(unittest.TestCase):

    def test_valid_item(self):
        node = ET.Element('node')
        item = ET.SubElement(node, 'item', type='key')
        item.text = 'value'

        value = f.get_item(node, 'key')
        self.assertEqual(value, 'value')

    def test_multiple_matches_yield_first_result(self):
        node = ET.Element('node')
        item1 = ET.SubElement(node, 'item', type='key')
        item1.text = 'value1'
        item2 = ET.SubElement(node, 'item', type='key')
        item2.text = 'value2'

        value = f.get_item(node, 'key')
        self.assertEqual(value, 'value1')

    def test_ignore_non_matching_results(self):
        node = ET.Element('node')
        item1 = ET.SubElement(node, 'not-item', type='not-key')
        item1.text = 'value1'
        item1 = ET.SubElement(node, 'item', type='not-key')
        item1.text = 'value2'
        item2 = ET.SubElement(node, 'item', type='key')
        item2.text = 'value3'

        value = f.get_item(node, 'key')
        self.assertEqual(value, 'value3')


    def test_no_matches_yields_default(self):
        node = ET.Element('node')
        item1 = ET.SubElement(node, 'not-item', type='not-key')
        item1.text = 'value1'
        item1 = ET.SubElement(node, 'item', type='not-key')
        item1.text = 'value2'
        item2 = ET.SubElement(node, 'item', type='not-key-either')
        item2.text = 'value3'

        value = f.get_item(node, 'key', 'default_value')
        self.assertEqual(value, 'default_value')


class ExampleSeparation(unittest.TestCase):

    def test_single_example(self):
        doc = ET.Element('document')
        text = ET.SubElement(doc, 'interlinear-text')
        title = ET.SubElement(text, 'item', type='title')
        title.text = 'ID_1'
        languages = ET.SubElement(text, 'languages')
        lang1 = ET.SubElement(languages, 'language', lang='lang1', vernacular='true')
        lang2 = ET.SubElement(languages, 'language', lang='lang2')
        pars = ET.SubElement(text, 'paragraphs')
        par = ET.SubElement(pars, 'paragraph')
        phrases = ET.SubElement(par, 'phrases')
        phrase = ET.SubElement(phrases, 'phrase')
        segnum = ET.SubElement(phrase, 'item', type='segnum')
        segnum.text = '1'

        examples = list(f.separate_examples(doc))
        self.assertEqual(len(examples), 1)
        self.assertEqual(examples[0]['title'], 'ID_1')
        self.assertEqual(examples[0]['segnum'], '1')
        self.assertEqual(examples[0]['vernacular'], 'lang1')
        self.assertEqual(examples[0]['other_langs'], ['lang2'])
        self.assertTrue(examples[0]['phrase'])

    def test_multiple_phrases(self):
        doc = ET.Element('document')
        text = ET.SubElement(doc, 'interlinear-text')
        title = ET.SubElement(text, 'item', type='title')
        title.text = 'ID_1'
        languages = ET.SubElement(text, 'languages')
        lang1 = ET.SubElement(languages, 'language', lang='lang1', vernacular='true')
        lang2 = ET.SubElement(languages, 'language', lang='lang2')
        pars = ET.SubElement(text, 'paragraphs')
        par = ET.SubElement(pars, 'paragraph')
        phrases = ET.SubElement(par, 'phrases')

        phrase1 = ET.SubElement(phrases, 'phrase')
        segnum1 = ET.SubElement(phrase1, 'item', type='segnum')
        segnum1.text = '1.1'

        phrase2 = ET.SubElement(phrases, 'phrase')
        segnum2 = ET.SubElement(phrase2, 'item', type='segnum')
        segnum2.text = '1.2'

        examples = list(f.separate_examples(doc))
        self.assertEqual(len(examples), 2)
        self.assertEqual(examples[0]['title'], 'ID_1')
        self.assertEqual(examples[0]['segnum'], '1.1')
        self.assertEqual(examples[0]['vernacular'], 'lang1')
        self.assertEqual(examples[0]['other_langs'], ['lang2'])
        self.assertTrue(examples[0]['phrase'])
        self.assertEqual(examples[1]['title'], 'ID_1')
        self.assertEqual(examples[1]['segnum'], '1.2')
        self.assertEqual(examples[1]['vernacular'], 'lang1')
        self.assertEqual(examples[1]['other_langs'], ['lang2'])
        self.assertTrue(examples[1]['phrase'])

    def test_multiple_paragrahs(self):
        doc = ET.Element('document')
        text = ET.SubElement(doc, 'interlinear-text')
        title = ET.SubElement(text, 'item', type='title')
        title.text = 'ID_1'
        languages = ET.SubElement(text, 'languages')
        lang1 = ET.SubElement(languages, 'language', lang='lang1', vernacular='true')
        lang2 = ET.SubElement(languages, 'language', lang='lang2')
        pars = ET.SubElement(text, 'paragraphs')

        par1 = ET.SubElement(pars, 'paragraph')
        phrases1 = ET.SubElement(par1, 'phrases')
        phrase1 = ET.SubElement(phrases1, 'phrase')
        segnum1 = ET.SubElement(phrase1, 'item', type='segnum')
        segnum1.text = '1'

        par2 = ET.SubElement(pars, 'paragraph')
        phrases2 = ET.SubElement(par2, 'phrases')
        phrase2 = ET.SubElement(phrases2, 'phrase')
        segnum2 = ET.SubElement(phrase2, 'item', type='segnum')
        segnum2.text = '2'

        examples = list(f.separate_examples(doc))
        self.assertEqual(len(examples), 2)
        self.assertEqual(examples[0]['title'], 'ID_1')
        self.assertEqual(examples[0]['segnum'], '1')
        self.assertEqual(examples[0]['vernacular'], 'lang1')
        self.assertEqual(examples[0]['other_langs'], ['lang2'])
        self.assertTrue(examples[0]['phrase'])
        self.assertEqual(examples[1]['title'], 'ID_1')
        self.assertEqual(examples[1]['segnum'], '2')
        self.assertEqual(examples[1]['vernacular'], 'lang1')
        self.assertEqual(examples[1]['other_langs'], ['lang2'])
        self.assertTrue(examples[1]['phrase'])

    def test_multiple_texts(self):
        doc = ET.Element('document')

        text1 = ET.SubElement(doc, 'interlinear-text')
        title1 = ET.SubElement(text1, 'item', type='title')
        title1.text = 'ID_1'
        languages = ET.SubElement(text1, 'languages')
        lang1 = ET.SubElement(languages, 'language', lang='lang1', vernacular='true')
        lang2 = ET.SubElement(languages, 'language', lang='lang2')
        pars = ET.SubElement(text1, 'paragraphs')
        par1 = ET.SubElement(pars, 'paragraph')
        phrases1 = ET.SubElement(par1, 'phrases')
        phrase1 = ET.SubElement(phrases1, 'phrase')
        segnum1 = ET.SubElement(phrase1, 'item', type='segnum')
        segnum1.text = '1'

        text2 = ET.SubElement(doc, 'interlinear-text')
        title2 = ET.SubElement(text2, 'item', type='title')
        title2.text = 'ID_2'
        languages2 = ET.SubElement(text2, 'languages')
        lang2_1 = ET.SubElement(languages2, 'language', lang='lang2.1', vernacular='true')
        lang2_2 = ET.SubElement(languages2, 'language', lang='lang2.2')
        pars2 = ET.SubElement(text2, 'paragraphs')
        par2 = ET.SubElement(pars2, 'paragraph')
        phrases2 = ET.SubElement(par2, 'phrases')
        phrase2 = ET.SubElement(phrases2, 'phrase')
        segnum2 = ET.SubElement(phrase2, 'item', type='segnum')
        segnum2.text = '1'

        examples = list(f.separate_examples(doc))
        self.assertEqual(len(examples), 2)
        self.assertEqual(examples[0]['title'], 'ID_1')
        self.assertEqual(examples[0]['segnum'], '1')
        self.assertEqual(examples[0]['vernacular'], 'lang1')
        self.assertEqual(examples[0]['other_langs'], ['lang2'])
        self.assertTrue(examples[0]['phrase'])
        self.assertEqual(examples[1]['title'], 'ID_2')
        self.assertEqual(examples[1]['segnum'], '1')
        self.assertEqual(examples[1]['vernacular'], 'lang2.1')
        self.assertEqual(examples[1]['other_langs'], ['lang2.2'])
        self.assertTrue(examples[1]['phrase'])

    def test_missing_phrases(self):
        doc = ET.Element('document')
        text = ET.SubElement(doc, 'interlinear-text')
        title = ET.SubElement(text, 'item', type='title')
        title.text = 'ID_1'
        languages = ET.SubElement(text, 'languages')
        lang1 = ET.SubElement(languages, 'language', lang='lang1', vernacular='true')
        lang2 = ET.SubElement(languages, 'language', lang='lang2')
        pars = ET.SubElement(text, 'paragraphs')
        par = ET.SubElement(pars, 'paragraph')

        with self.assertRaises(ValueError):
            examples = list(f.separate_examples(doc))

    def test_missing_texts(self):
        doc = ET.Element('document')
        not_text = ET.SubElement(doc, 'not-an-interlinear-text')

        with self.assertRaises(ValueError):
            examples = list(f.separate_examples(doc))
