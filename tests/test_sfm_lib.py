# coding: utf8
from __future__ import unicode_literals, print_function, division


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
