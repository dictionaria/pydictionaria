"""
Create CLDF release version of a submission in its own repository
"""
from pycldf import Dictionary
from csvw.dsv import UnicodeWriter, reader
from bs4 import BeautifulSoup

from clldutils.clilib import PathType, ParserError
from clldutils import jsonlib
from clldutils.path import copy

from pydictionaria.cli_util import add_submission, get_submission

TRAVIS_BASE_URL = "https://travis-ci.org/dictionaria/"
README_TEMPLATE = """\
# {title}

> by {authors}

This repository contains the data underlying the published version of the dictionary
at [Dictionaria]({url}) as [CLDF](https://cldf.clld.org)
[Dictionary](cldf)
[![Build Status](%s{id}.svg?branch=master)](%s{id})

Releases of this repository are archived with and accessible through
[ZENODO](https://zenodo.org/communities/dictionaria) and the latest release
is published on the [Dictionaria website](https://dictionaria.clld.org).

{intro}
""" % (TRAVIS_BASE_URL, TRAVIS_BASE_URL)

TRAVIS_YML = """\
language: python
python: "3.6"
cache: pip
before_cache: rm -f $HOME/.cache/pip/log/debug.log
install: pip install pytest-cldf
script: pytest --cldf-metadata=cldf/Dictionary-metadata.json test.py
"""

TEST_PY = """\
def test_valid(cldf_dataset, cldf_logger):
    assert cldf_dataset.validate(log=cldf_logger)
"""


def register(parser):
    add_submission(parser)
    parser.add_argument('release_repos', type=PathType(type='dir'))


def igt_to_table(soup, div):
    """
    """
    morphemes, glosses = [], []
    ot = div.find('div', class_='object-language')
    tt = div.find('div', class_='translation')
    sn = div.find('div', class_='sentence-number')

    def coalesce(e):
        return e or soup.new_tag('td')

    for d in div.find_all('div', class_='gloss-unit'):
        morphemes.append(coalesce(d.find('div', class_='morpheme')))
        glosses.append(coalesce(d.find('div', class_='gloss')))

    table = soup.new_tag('table')
    tbody = soup.new_tag('tbody')
    tbody.append('\n')

    tr = soup.new_tag('tr')
    if sn:
        nr = soup.new_tag('td')
        s = soup.new_tag('strong')
        s.string = div.find('div', class_='sentence-number').string
        nr.append(s)
        tr.append(nr)
    ot.name = 'td'
    ot['colspan'] = len(morphemes)
    tr.append(ot)
    tbody.append(tr)
    tbody.append('\n')

    tr = soup.new_tag('tr')
    if sn:
        tr.append(soup.new_tag('td'))
    for m in morphemes:
        m.name = 'td'
        tr.append(m)
    tbody.append(tr)
    tbody.append('\n')

    tr = soup.new_tag('tr')
    if sn:
        tr.append(soup.new_tag('td'))
    for m in glosses:
        m.name = 'td'
        tr.append(m)
    tbody.append(tr)
    tbody.append('\n')

    tr = soup.new_tag('tr')
    if sn:
        tr.append(soup.new_tag('td'))
    tt.name = 'td'
    tt['colspan'] = len(morphemes)
    tr.append(tt)
    tbody.append(tr)
    tbody.append('\n')

    table.append(tbody)
    div.replace_with(table)


def run(args):
    s = get_submission(args)
    processed = s.dir / 'processed'
    cldf_md_path = processed / 'cldf-md.json'
    if not cldf_md_path.exists():
        raise ParserError('submission has not been processed yet')
    cldf_md = Dictionary.from_metadata(cldf_md_path)
    outdir = args.release_repos
    media = jsonlib.load(args.repos / 'cdstar.json')
    copy(s.dir / 'md.json', outdir / 'md.json')

    def format_authors(authors):
        res, in_with = [], False
        for i, a in enumerate(authors):
            name = a['name'] if isinstance(a, dict) else a
            primary = a.get('primary', True) if isinstance(a, dict) else True
            assert (in_with and not primary) or (not in_with)
            if i > 0:
                sep = 'and'
                if (not primary) and (not in_with):
                    in_with = True
                    sep = 'with'
                res.append(sep)
            res.append(name)
        return ' '.join(res)

    intro = BeautifulSoup((s.dir / 'intro.md').read_text(encoding='utf-8'), 'html.parser')
    for div in intro.find_all('div', class_='sentence-wrapper'):
        igt_to_table(intro, div)

    md = jsonlib.load(s.dir / 'md.json')
    md_readme = {
        'id': s.dir.name,
        'url': 'https://dictionaria.clld.org/contributions/' + s.dir.name,
        'intro': '{0}'.format(intro),
        'title': md['properties'].get('title') or md['language']['name'] + ' dictionary',
        'authors': format_authors(md['authors']),
    }
    (outdir / 'README.md').write_text(README_TEMPLATE.format(**md_readme), encoding='utf-8')
    cldf = outdir / 'cldf'

    if not cldf.exists():
        cldf.mkdir()

    sources = s.dir / 'sources.bib'
    if sources.exists():
        copy(sources, cldf / sources.name)
        cldf_md.properties['dc:source'] = sources.name

    cldf_md.properties['dc:creator'] = md_readme['authors']
    cldf_md.properties['dc:title'] = md_readme['title']
    cldf_md.properties['dc:identifier'] = md_readme['url']

    media_table = processed / 'media.csv'
    for table in cldf_md.tables:
        if table.local_name != media_table.name:
            copy(processed / table.local_name, cldf / table.local_name)
    try:
        cldf_md['LanguageTable']
    except KeyError:
        lid = next(cldf_md['EntryTable'].iterdicts())[
            cldf_md['EntryTable', 'languageReference'].name]
        t = cldf_md.add_component('LanguageTable')
        t.write(
            [dict(
                ID=lid,
                Name=md['language']['name'],
                Glottocode=md['language'].get('glottocode'),
                ISO639P3code=md['language'].get('isocode'),
            )],
            fname=cldf / 'languages.csv')

    if media_table.exists():
        with UnicodeWriter(cldf / media_table.name) as w:
            for i, row in enumerate(reader(media_table, dicts=True)):
                if i == 0:
                    w.writerow(list(row.keys()) + ['URL', 'mimetype', 'size'])
                    cldf_md.add_columns(
                        media_table.name,
                        {'name': 'URL', 'datatype': 'anyURI'},
                        {'name': 'mimetype'},
                        {'name': 'size', 'datatype': 'integer'},
                    )
                assert row['ID'] in media
                row['URL'] = 'https://cdstar.shh.mpg.de/bitstreams/{0[objid]}/{0[original]}'.format(
                    media[row['ID']])
                row['mimetype'] = media[row['ID']]['mimetype']
                row['size'] = media[row['ID']]['size']
                w.writerow(row.values())
    new_md = cldf / 'Dictionary-metadata.json'
    cldf_md.write_metadata(new_md)
    Dictionary.from_metadata(new_md).validate(log=args.log)
    (outdir / '.travis.yml').write_text(TRAVIS_YML, encoding='utf-8')
    (outdir / 'test.py').write_text(TEST_PY, encoding='utf-8')
