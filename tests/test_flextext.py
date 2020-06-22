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
        self.assertEqual(examples[0]['text_id'], 'ID_1')
        self.assertEqual(examples[0]['segnum'], '1')
        self.assertEqual(examples[0]['vernacular'], 'lang1')
        self.assertEqual(examples[0]['languages'], {'lang1', 'lang2'})
        self.assertTrue(examples[0]['example'])

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
        self.assertEqual(len(examples), 1)
        self.assertEqual(examples[0]['text_id'], 'ID_1')
        self.assertEqual(examples[0]['segnum'], '1')
        self.assertEqual(examples[0]['vernacular'], 'lang1')
        self.assertEqual(examples[0]['languages'], {'lang1', 'lang2'})
        self.assertTrue(examples[0]['example'])

    def test_multiple_paragraphs(self):
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
        self.assertEqual(examples[0]['text_id'], 'ID_1')
        self.assertEqual(examples[0]['segnum'], '1')
        self.assertEqual(examples[0]['vernacular'], 'lang1')
        self.assertEqual(examples[0]['languages'], {'lang1', 'lang2'})
        self.assertTrue(examples[0]['example'])
        self.assertEqual(examples[1]['text_id'], 'ID_1')
        self.assertEqual(examples[1]['segnum'], '2')
        self.assertEqual(examples[1]['vernacular'], 'lang1')
        self.assertEqual(examples[1]['languages'], {'lang1', 'lang2'})
        self.assertTrue(examples[1]['example'])

    def test_multiple_texts(self):
        doc = ET.Element('document')

        text1 = ET.SubElement(doc, 'interlinear-text')
        title1 = ET.SubElement(text1, 'item', type='title')
        title1.text = 'ID_1'
        languages = ET.SubElement(text1, 'languages')
        lang1_1 = ET.SubElement(languages, 'language', lang='lang1.1', vernacular='true')
        lang1_2 = ET.SubElement(languages, 'language', lang='lang1.2')
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
        self.assertEqual(examples[0]['text_id'], 'ID_1')
        self.assertEqual(examples[0]['segnum'], '1')
        self.assertEqual(examples[0]['vernacular'], 'lang1.1')
        self.assertEqual(examples[0]['languages'], {'lang1.1', 'lang1.2'})
        self.assertTrue(examples[0]['example'])
        self.assertEqual(examples[1]['text_id'], 'ID_2')
        self.assertEqual(examples[1]['segnum'], '1')
        self.assertEqual(examples[1]['vernacular'], 'lang2.1')
        self.assertEqual(examples[1]['languages'], {'lang2.1', 'lang2.2'})
        self.assertTrue(examples[1]['example'])

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

        examples = list(f.separate_examples(doc))
        self.assertEqual(examples, [])

    def test_missing_paragraphs(self):
        doc = ET.Element('document')
        text = ET.SubElement(doc, 'interlinear-text')
        title = ET.SubElement(text, 'item', type='title')
        title.text = 'ID_1'
        languages = ET.SubElement(text, 'languages')
        lang1 = ET.SubElement(languages, 'language', lang='lang1', vernacular='true')
        lang2 = ET.SubElement(languages, 'language', lang='lang2')

        examples = list(f.separate_examples(doc))
        self.assertEqual(examples, [])

    def test_missing_texts(self):
        doc = ET.Element('document')
        not_text = ET.SubElement(doc, 'not-an-interlinear-text')

        examples = list(f.separate_examples(doc))
        self.assertEqual(examples, [])

    def test_missing_title(self):
        doc = ET.Element('document')
        text = ET.SubElement(doc, 'interlinear-text')
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
        self.assertEqual(examples, [])

    def test_missing_vernacular(self):
        doc = ET.Element('document')
        text = ET.SubElement(doc, 'interlinear-text')
        title = ET.SubElement(text, 'item', type='title')
        title.text = 'ID_1'
        languages = ET.SubElement(text, 'languages')
        lang1 = ET.SubElement(languages, 'language', lang='lang1')
        lang2 = ET.SubElement(languages, 'language', lang='lang2')
        pars = ET.SubElement(text, 'paragraphs')
        par = ET.SubElement(pars, 'paragraph')
        phrases = ET.SubElement(par, 'phrases')
        phrase = ET.SubElement(phrases, 'phrase')
        segnum = ET.SubElement(phrase, 'item', type='segnum')
        segnum.text = '1'

        examples = list(f.separate_examples(doc))
        self.assertEqual(examples, [])

    def test_missing_languages(self):
        doc = ET.Element('document')
        text = ET.SubElement(doc, 'interlinear-text')
        title = ET.SubElement(text, 'item', type='title')
        title.text = 'ID_1'
        pars = ET.SubElement(text, 'paragraphs')
        par = ET.SubElement(pars, 'paragraph')
        phrases = ET.SubElement(par, 'phrases')
        phrase = ET.SubElement(phrases, 'phrase')
        segnum = ET.SubElement(phrase, 'item', type='segnum')
        segnum.text = '1'

        examples = list(f.separate_examples(doc))
        self.assertEqual(examples, [])

    def test_missing_segnum(self):
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

        examples = list(f.separate_examples(doc))
        self.assertEqual(examples, [])

    def test_use_vernacular_title_as_id(self):
        doc = ET.Element('document')
        text = ET.SubElement(doc, 'interlinear-text')
        title1 = ET.SubElement(text, 'item', type='title', lang='lang2')
        title1.text = 'ID_1'
        title2 = ET.SubElement(text, 'item', type='title', lang='lang1')
        title2.text = 'ID_2'
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
        self.assertEqual(examples[0]['text_id'], 'ID_2')
        self.assertEqual(examples[0]['segnum'], '1')
        self.assertEqual(examples[0]['vernacular'], 'lang1')
        self.assertEqual(examples[0]['languages'], {'lang1', 'lang2'})
        self.assertTrue(examples[0]['example'])

    def test_fall_back_to_first_title(self):
        doc = ET.Element('document')
        text = ET.SubElement(doc, 'interlinear-text')
        title1 = ET.SubElement(text, 'item', type='title', lang='lang3')
        title1.text = 'ID_1'
        title2 = ET.SubElement(text, 'item', type='title', lang='lang2')
        title2.text = 'ID_2'
        languages = ET.SubElement(text, 'languages')
        lang1 = ET.SubElement(languages, 'language', lang='lang1', vernacular='true')
        lang2 = ET.SubElement(languages, 'language', lang='lang2')
        lang3 = ET.SubElement(languages, 'language', lang='lang3')
        pars = ET.SubElement(text, 'paragraphs')
        par = ET.SubElement(pars, 'paragraph')
        phrases = ET.SubElement(par, 'phrases')
        phrase = ET.SubElement(phrases, 'phrase')
        segnum = ET.SubElement(phrase, 'item', type='segnum')
        segnum.text = '1'

        examples = list(f.separate_examples(doc))
        self.assertEqual(len(examples), 1)
        self.assertEqual(examples[0]['text_id'], 'ID_1')
        self.assertEqual(examples[0]['segnum'], '1')
        self.assertEqual(examples[0]['vernacular'], 'lang1')
        self.assertEqual(examples[0]['languages'], {'lang1', 'lang2', 'lang3'})
        self.assertTrue(examples[0]['example'])


class GlossExtraction(unittest.TestCase):

    def test_analysed_word(self):
        phrase = ET.Element('phrase')
        words = ET.SubElement(phrase, 'words')

        word1 = ET.SubElement(words, 'word')
        morphemes1 = ET.SubElement(word1, 'morphemes')
        morph1_1 = ET.SubElement(morphemes1, 'morph')
        txt1_1 = ET.SubElement(morph1_1, 'item', type='txt')
        txt1_1.text = 'morpheme1.1'
        morph1_2 = ET.SubElement(morphemes1, 'morph')
        txt1_2 = ET.SubElement(morph1_2, 'item', type='txt')
        txt1_2.text = 'morpheme1.2'

        word2 = ET.SubElement(words, 'word')
        morphemes2 = ET.SubElement(word2, 'morphemes')
        morph2_1 = ET.SubElement(morphemes2, 'morph')
        txt2_1 = ET.SubElement(morph2_1, 'item', type='txt')
        txt2_1.text = 'morpheme2.1'
        morph2_2 = ET.SubElement(morphemes2, 'morph')
        txt2_2 = ET.SubElement(morph2_2, 'item', type='txt')
        txt2_2.text = 'morpheme2.2'

        processed = f.extract_gloss(phrase)
        self.assertEqual(
            processed.get('Analyzed_Word'),
            ['morpheme1.1', 'morpheme1.2', 'morpheme2.1', 'morpheme2.2'])

    def test_gloss(self):
        phrase = ET.Element('phrase')
        words = ET.SubElement(phrase, 'words')

        word1 = ET.SubElement(words, 'word')
        morphemes1 = ET.SubElement(word1, 'morphemes')
        morph1_1 = ET.SubElement(morphemes1, 'morph')
        gls1_1 = ET.SubElement(morph1_1, 'item', type='gls')
        gls1_1.text = 'gloss1.1'
        morph1_2 = ET.SubElement(morphemes1, 'morph')
        gls1_2 = ET.SubElement(morph1_2, 'item', type='gls')
        gls1_2.text = 'gloss1.2'

        word2 = ET.SubElement(words, 'word')
        morphemes2 = ET.SubElement(word2, 'morphemes')
        morph2_1 = ET.SubElement(morphemes2, 'morph')
        gls2_1 = ET.SubElement(morph2_1, 'item', type='gls')
        gls2_1.text = 'gloss2.1'
        morph2_2 = ET.SubElement(morphemes2, 'morph')
        gls2_2 = ET.SubElement(morph2_2, 'item', type='gls')
        gls2_2.text = 'gloss2.2'

        processed = f.extract_gloss(phrase)
        self.assertEqual(
            processed.get('Gloss'),
            ['gloss1.1', 'gloss1.2', 'gloss2.1', 'gloss2.2'])

    def test_gloss_pos(self):
        phrase = ET.Element('phrase')
        words = ET.SubElement(phrase, 'words')

        word1 = ET.SubElement(words, 'word')
        morphemes1 = ET.SubElement(word1, 'morphemes')
        morph1_1 = ET.SubElement(morphemes1, 'morph')
        msa1_1 = ET.SubElement(morph1_1, 'item', type='msa')
        msa1_1.text = 'pos1.1'
        morph1_2 = ET.SubElement(morphemes1, 'morph')
        msa1_2 = ET.SubElement(morph1_2, 'item', type='msa')
        msa1_2.text = 'pos1.2'

        word2 = ET.SubElement(words, 'word')
        morphemes2 = ET.SubElement(word2, 'morphemes')
        morph2_1 = ET.SubElement(morphemes2, 'morph')
        msa2_1 = ET.SubElement(morph2_1, 'item', type='msa')
        msa2_1.text = 'pos2.1'
        morph2_2 = ET.SubElement(morphemes2, 'morph')
        msa2_2 = ET.SubElement(morph2_2, 'item', type='msa')
        msa2_2.text = 'pos2.2'

        processed = f.extract_gloss(phrase)
        self.assertEqual(
            processed.get('Gloss_POS'),
            ['pos1.1', 'pos1.2', 'pos2.1', 'pos2.2'])

    def test_fallback_to_words(self):
        phrase = ET.Element('phrase')
        words = ET.SubElement(phrase, 'words')

        word1 = ET.SubElement(words, 'word')
        txt1 = ET.SubElement(word1, 'item', type='txt')
        txt1.text = 'word1'

        word2 = ET.SubElement(words, 'word')
        morphemes2 = ET.SubElement(word2, 'morphemes')
        morph2_1 = ET.SubElement(morphemes2, 'morph')
        txt2_1 = ET.SubElement(morph2_1, 'item', type='txt')
        txt2_1.text = 'morpheme2.1'
        morph2_2 = ET.SubElement(morphemes2, 'morph')
        txt2_2 = ET.SubElement(morph2_2, 'item', type='txt')
        txt2_2.text = 'morpheme2.2'

        processed = f.extract_gloss(phrase)
        self.assertEqual(
            processed.get('Analyzed_Word'),
            ['word1', 'morpheme2.1', 'morpheme2.2'])

    def test_punctuation(self):
        phrase = ET.Element('phrase')
        words = ET.SubElement(phrase, 'words')

        word1 = ET.SubElement(words, 'word')
        morphemes1 = ET.SubElement(word1, 'morphemes')
        morph1_1 = ET.SubElement(morphemes1, 'morph')
        txt1_1 = ET.SubElement(morph1_1, 'item', type='txt')
        txt1_1.text = 'morpheme1.1'
        pos1_1 = ET.SubElement(morph1_1, 'item', type='msa')
        pos1_1.text = 'pos1.1'
        morph1_2 = ET.SubElement(morphemes1, 'morph')
        txt1_2 = ET.SubElement(morph1_2, 'item', type='txt')
        txt1_2.text = 'morpheme1.2'
        pos1_2 = ET.SubElement(morph1_2, 'item', type='msa')
        pos1_2.text = 'pos1.2'

        word2 = ET.SubElement(words, 'word')
        punct1 = ET.SubElement(word2, 'item', type='punct')
        punct1.text = '!'

        processed = f.extract_gloss(phrase)
        self.assertEqual(
            processed.get('Analyzed_Word'),
            ['morpheme1.1', 'morpheme1.2', '!'])
        self.assertEqual(
            processed.get('Gloss_POS'),
            ['pos1.1', 'pos1.2', ''])

    def test_multilanguage_gloss(self):
        phrase = ET.Element('phrase')
        words = ET.SubElement(phrase, 'words')

        word1 = ET.SubElement(words, 'word')
        morphemes1 = ET.SubElement(word1, 'morphemes')
        morph1_1 = ET.SubElement(morphemes1, 'morph')
        gls1_1_en = ET.SubElement(morph1_1, 'item', type='gls', lang='en')
        gls1_1_en.text = 'gloss1.1'
        gls1_1_fr = ET.SubElement(morph1_1, 'item', type='gls', lang='fr')
        gls1_1_fr.text = 'le gloss1.1'
        morph1_2 = ET.SubElement(morphemes1, 'morph')
        gls1_2_en = ET.SubElement(morph1_2, 'item', type='gls', lang='en')
        gls1_2_en.text = 'gloss1.2'
        gls1_2_fr = ET.SubElement(morph1_2, 'item', type='gls', lang='fr')
        gls1_2_fr.text = 'le gloss1.2'

        word2 = ET.SubElement(words, 'word')
        morphemes2 = ET.SubElement(word2, 'morphemes')
        morph2_1 = ET.SubElement(morphemes2, 'morph')
        gls2_1_en = ET.SubElement(morph2_1, 'item', type='gls', lang='en')
        gls2_1_en.text = 'gloss2.1'
        gls2_1_fr = ET.SubElement(morph2_1, 'item', type='gls', lang='fr')
        gls2_1_fr.text = 'le gloss2.1'
        morph2_2 = ET.SubElement(morphemes2, 'morph')
        gls2_2_en = ET.SubElement(morph2_2, 'item', type='gls', lang='en')
        gls2_2_en.text = 'gloss2.2'
        gls2_2_fr = ET.SubElement(morph2_2, 'item', type='gls', lang='fr')
        gls2_2_fr.text = 'le gloss2.2'

        processed = f.extract_gloss(phrase)
        self.assertEqual(
            processed.get('Gloss'),
            ['gloss1.1', 'gloss1.2', 'gloss2.1', 'gloss2.2'])
        self.assertEqual(
            processed.get('Gloss_Fr'),
            ['le gloss1.1', 'le gloss1.2', 'le gloss2.1', 'le gloss2.2'])

    def test_missing_text(self):
        phrase = ET.Element('phrase')
        words = ET.SubElement(phrase, 'words')

        word1 = ET.SubElement(words, 'word')
        morphemes1 = ET.SubElement(word1, 'morphemes')
        morph1_1 = ET.SubElement(morphemes1, 'morph')
        gls1_1 = ET.SubElement(morph1_1, 'item', type='gls')
        gls1_1.text = 'gloss1.1'
        morph1_2 = ET.SubElement(morphemes1, 'morph')
        gls1_2 = ET.SubElement(morph1_2, 'item', type='gls')

        word2 = ET.SubElement(words, 'word')
        morphemes2 = ET.SubElement(word2, 'morphemes')
        morph2_1 = ET.SubElement(morphemes2, 'morph')
        gls2_1 = ET.SubElement(morph2_1, 'item', type='gls')
        gls2_1.text = 'gloss2.1'
        morph2_2 = ET.SubElement(morphemes2, 'morph')
        gls2_2 = ET.SubElement(morph2_2, 'item', type='gls')
        gls2_2.text = 'gloss2.2'

        processed = f.extract_gloss(phrase)
        self.assertEqual(
            processed.get('Gloss'),
            ['gloss1.1', '', 'gloss2.1', 'gloss2.2'])


class MergeGlosses(unittest.TestCase):

    def test_merge_lists(self):
        gloss1 = {
            'Analyzed_Word': ['mb1.1', 'mb1.2', 'mb1.3'],
            'Gloss': ['gl1.1', 'gl1.2', 'gl1.3']}
        gloss2 = {
            'Analyzed_Word': ['mb2.1', 'mb2.2', 'mb2.3'],
            'Gloss': ['gl2.1', 'gl2.2', 'gl2.3']}

        combo = f.merge_glosses([gloss1, gloss2])
        self.assertEqual(combo['Analyzed_Word'], ['mb1.1', 'mb1.2', 'mb1.3', 'mb2.1', 'mb2.2', 'mb2.3'])
        self.assertEqual(combo['Gloss'], ['gl1.1', 'gl1.2', 'gl1.3', 'gl2.1', 'gl2.2', 'gl2.3'])

    def test_pad_missing_fields(self):
        gloss1 = {
            'Analyzed_Word': ['mb1.1', 'mb1.2'],
            'Gloss': ['gl1.1', 'gl1.2']}
        gloss2 = {
            'Gloss': ['gl2.1', 'gl2.2'],
            'Gloss_POS': ['pos2.1', 'pos2.2']}
        gloss3 = {
            'Analyzed_Word': ['mb3.1', 'mb3.2'],
            'Gloss_POS': ['pos3.1', 'pos3.2']}

        combo = f.merge_glosses([gloss1, gloss2, gloss3])
        self.assertEqual(combo['Analyzed_Word'], ['mb1.1', 'mb1.2', '', '', 'mb3.1', 'mb3.2'])
        self.assertEqual(combo['Gloss'], ['gl1.1', 'gl1.2', 'gl2.1', 'gl2.2', '', ''])
        self.assertEqual(combo['Gloss_POS'], ['', '', 'pos2.1', 'pos2.2', 'pos3.1', 'pos3.2'])
