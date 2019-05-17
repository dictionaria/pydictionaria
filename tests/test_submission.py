# coding: utf8
from __future__ import unicode_literals, print_function, division

from clldutils.jsonlib import dump

from pydictionaria.submission import Submission, Metadata, Language


def test_Submission(repos, tmpdir):
    dump(
        Metadata([], Language('name', 'gc', 'iso'), None).asdict(),
        str(tmpdir.join('md.json')))
    s = Submission(str(tmpdir), repos)
    #self.assertEqual(Metadata.fromdict(s.md.asdict()).language.name, 'name')
    assert s.module is None
    assert s.dictionary is None
    assert s.media['audio'] == []
    md = s.md
    md.language.name = 'newname'
    s.md = md.asdict()
    assert s.md.language.name == 'newname'
    s = Submission(str(tmpdir), repos)
    assert s.md.language.name == 'newname'
    assert s.id


def test_Excel(repos):
    Submission(repos.joinpath('submissions', 'sub_excel'), repos)


def test_SFM(repos, capsys):
    s = Submission(repos.joinpath('submissions', 'sub_sfm'), repos)
    s.dictionary.search(zz='custom')
    out, _ = capsys.readouterr()
    assert "1" in out
