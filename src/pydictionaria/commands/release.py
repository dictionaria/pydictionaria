"""
Create CLDF release version of a submission in its own repository
"""

from bs4 import BeautifulSoup

from clldutils import jsonlib
from cldfbench.cli_util import with_dataset, add_dataset_spec


LICENSE = "CC-BY-4.0"

ORG_URL = "https://github.com/dictionaria"
README_TEMPLATE = """\
# {title}

> by {authors}

This repository contains the data underlying the published version of the dictionary
at [Dictionaria]({url}) as [CLDF](https://cldf.clld.org)
[Dictionary](cldf)
[![CLDF validation](%s/{id}/workflows/CLDF-validation/badge.svg)](%s/{id}/actions?query=workflow%%3ACLDF-validation)

Releases of this repository are archived with and accessible through
[ZENODO](https://zenodo.org/communities/dictionaria) and the latest release
is published on the [Dictionaria website](https://dictionaria.clld.org).

{intro}
""" % (ORG_URL, ORG_URL)


def register(parser):
    add_dataset_spec(parser)


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


# FIXME Put this somewhere, where the benches can find it, too?
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


def release(dataset, args):
    intro = BeautifulSoup(
        (dataset.raw_dir / 'intro.md').read_text(encoding='utf-8'),
        'html.parser')
    for div in intro.find_all('div', class_='sentence-wrapper'):
        igt_to_table(intro, div)

    md = jsonlib.load(dataset.etc_dir / 'md.json')
    metadata_json = dataset.dir / 'metadata.json'
    cb_metadata = jsonlib.load(metadata_json)

    id_ = dataset.id
    url = 'https://dictionaria.clld.org/contributions/' + dataset.id
    title = (
        md['properties'].get('title')
        or cb_metadata.get('title')
        or md['language']['name'] + ' dictionary')

    cb_metadata['id'] = id_
    cb_metadata['title'] = title
    cb_metadata['license'] = LICENSE
    cb_metadata['url'] = url
    jsonlib.dump(cb_metadata, metadata_json, indent=4)

    readme_kwargs = {
        'id': id_,
        'url': url,
        'intro': '{0}'.format(intro),
        'title': title,
        'authors': format_authors(md['authors']),
    }
    (dataset.dir / 'README.md').write_text(
        README_TEMPLATE.format(**readme_kwargs), encoding='utf-8')

    zenodo_md = {
        "title": "dictionaria/{}: {}".format(id_, title),
        "access_right": "open",
        "keywords": ["cldf:Dictionary", "linguistics"],
        "creators": [{"name": a['name'] if isinstance(a, dict) else a} for a in md['authors']],
        "communities": [
            {"identifier": "cldf-datasets"},
            {"identifier": "clld"},
            {"identifier": "dictionaria"}
        ],
        "upload_type": "dataset",
        "license": {
            "id": LICENSE
        }
    }
    if cb_metadata.get('citation'):
        zenodo_md['description'] = cb_metadata['citation']
    jsonlib.dump(zenodo_md, dataset.dir / '.zenodo.json', indent=4)


def run(args):
    with_dataset(args, release)
