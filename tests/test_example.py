from pathlib import Path

from pydictionaria.example import Corpus, Examples, Example, concat_multilines


EAF_SFM = """
\\_sh v3.0  400  Text
\\_DateStampHasFourDigitYear

\\utterance_id Iar_02RG.002
\\ELANBegin 1.843
\\ELANEnd 5.708
\\ELANParticipant
\\utterance Enaa a henanaa e Ruth Iarabee.
\\gramm_units # Enaa          a       hena  -naa        e    Ruth Iarabee
\\rp_gloss # 1SG.PRON      ART2.SG name- -1SG.PRON   ART1 Ruth Iarabee
\\GRAID # pro.1:dt_poss         np:s  -pro.1:poss      np:pred
\\utterance_tokens Enaa a henanaa e Ruth Iarabee
\\ft My name is Ruth Iarabee.
\\comment
"""

NORM_EXAMPLE = """\
\\ref Iar_02RG.002
\\lemma
\\rf
\\tx Enaa a henanaa e Ruth Iarabee.
\\mb Enaa	a	hena	-naa	e	Ruth	Iarabee
\\gl 1SG.PRON	ART2.SG	name-	-1SG.PRON	ART1	Ruth	Iarabee
\\ft My name is Ruth Iarabee.
\\ot
\\ota
\\sfx"""


def test_example_obj():
    ex = Example.from_string(NORM_EXAMPLE)
    assert ex.gloss == '1SG.PRON\tART2.SG\tname-\t-1SG.PRON	ART1\tRuth\tIarabee'
    assert ex.translation == 'My name is Ruth Iarabee.'
    assert ex.soundfile is None
    assert ex.alt_translation is None
    assert ex.alt_translation2 is None


def test_examples_obj():
    ex = Examples([Example.from_string(NORM_EXAMPLE + '\n\\mb more morphemes')])
    ex.visit(concat_multilines)
    assert ex[0].morphemes.split('\t') == \
        ['Enaa', 'a', 'hena', '-naa', 'e', 'Ruth', 'Iarabee', 'more', 'morphemes']


def test_corpus_obj(tmpdir):
    c = Corpus.from_dir(Path(str(tmpdir)))
    assert c.get('key') is None

    tmpdir.join('test.eaf.sfm').write_text(EAF_SFM, 'utf8')
    c = Corpus.from_dir(Path(str(tmpdir)))
    example = c.get('Iar_02RG.2')
    assert isinstance(example, Example)
    assert str(example) == NORM_EXAMPLE
    assert example.id == 'Iar_02RG.002'
    example.set('lemma', 'x')
    example.set('lemma', 'y')
    assert example.lemmas == ['x', 'y']
