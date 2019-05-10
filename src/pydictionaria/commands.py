# coding: utf8
from __future__ import unicode_literals, print_function, division
import os
import collections

from csvw.dsv import reader, UnicodeWriter
from clldutils.clilib import ParserError, command
from clldutils import jsonlib
from clldutils.path import Path, md5, copy, read_text, write_text
from clldutils.markup import Table
from cdstarcat.catalog import Catalog
from pyconcepticon.api import Concepticon
import html2markdown

from pydictionaria.util import MediaCatalog
from pydictionaria.submission import Submission, Metadata, Language


class ValidationError(ValueError):
    def __init__(self, msg):
        self.msg = msg
        ValueError.__init__(self, msg)


def _upload(repos, d, catalog, name):
    with MediaCatalog(repos) as mcat:
        with Catalog(
                catalog,
                cdstar_url=os.environ['CDSTAR_URL'],
                cdstar_user=os.environ['CDSTAR_USER'],
                cdstar_pwd=os.environ['CDSTAR_PWD']) as cat:
            for fname in d.iterdir():
                if fname.is_file():
                    if md5(fname) not in mcat.items:
                        md = {
                            'collection': 'dictionaria',
                            'path': '%s' % fname.relative_to(repos),
                            'dictionary': name,
                        }
                        try:
                            _, _, obj = list(cat.create(fname, md, filter_=lambda f: True))[0]
                        except:
                            print(fname)
                            raise
                        mcat.add(obj, sid=name, type=fname.parent.name, fname=fname.name)


@command()
def upload_media(args):
    """Upload media files of a submission to CDSTAR

    dictionaria upload_media SUBMISSION [CDSTAR_CATALOG]
    """
    submission = Submission(_submission_dir(args, args.args[0]), args.repos)
    assert submission.md
    catalog = Path(args.args[1] if len(args.args) > 1 else os.environ['CDSTAR_CATALOG'])
    assert catalog.exists()

    for mtype in submission.media:
        if submission.dir.joinpath(mtype).exists():
            _upload(args.repos, submission.dir.joinpath(mtype), catalog, submission.id)

    args.log.info(catalog)


@command()
def ls(args):
    """List submissions

    dictionaria ls
    """
    table = Table('ID', 'Format', 'Language', 'Glottocode', 'Authors', 'Published')
    for d in _submission_dir(args).iterdir():
        try:
            s = Submission(d, args.repos)
            md = s.md
        except:
            args.log.exception('error loading submission {0}'.format(d))
            continue
        if md:
            table.append([
                s.id,
                s.dictionary.format if s.dictionary else '',
                md.language.name,
                md.language.glottocode,
                md.author_names,
                md.date_published or '',
                ])
    print(table.render(tablefmt='simple', sortkey=lambda r: r[0], condensed=False))


@command()
def stat(args):
    """Display statistics of a submission

    dictionaria stat SUBMISSION
    """
    mcat = MediaCatalog(args.repos)
    s = Submission(_submission_dir(args, args.args[0]), args.repos)
    print('# {0} Dictionary by {1}'.format(s.md.language.name, s.md.author_names))
    print('\n## Media\n')
    table = Table('Type', 'Files', 'Uploaded')
    table.extend([(k, len(v), sum([1 if md5(vv) in mcat else 0 for vv in v]))
                  for k, v in s.media.items()])
    print(table.render(tablefmt='simple', sortkey=lambda r: -r[1], condensed=False))
    if s.dictionary is None:
        print('\n## Dictionary\n\n(no dictionary found)')
    else:
        print('\n## Dictionary [{0}]\n'.format(s.dictionary.format))
        s.dictionary.stat()


@command()
def search(args):
    """Search in a submitted dictionary

    dictionaria search SUBMISSION [KEY=VALUE]+
    """
    s = Submission(_submission_dir(args, args.args[0]), args.repos)
    if s.dictionary is None:
        args.log.error("No dictionary found in submission '{}'".format(s.id))
        return

    query = {}
    for arg in args.args[1:]:
        key, value = arg.split('=', 1)
        try:
            value = int(value)
        except (ValueError, TypeError):
            pass
        query[key] = value

    s.dictionary.search(**query)


@command()
def repair(args):
    Submission(_submission_dir(args, args.args[0]), args.repos).dictionary.repair()


@command()
def add_comparison_meanings(args):
    """Add automatically guessed comparison meanings to a dictionary

    dictionaria add_comparison_meanings SUBMISSION [MARKER]
    """
    def format_cs(cs):
        return '{0} [{1}] "{2}"'.format(cs.gloss, cs.id, cs.definition)

    s = Submission(_submission_dir(args, args.args[0]), args.repos)
    if not hasattr(s.dictionary, 'add_comparison_meanings'):
        args.log.warn('Format of submission does not support this command.')
        return

    concepticon = Concepticon(args.concepticon_repos)
    s.dictionary.add_comparison_meanings(
        concepticon, marker='zcom2' if len(args.args) == 1 else args.args[1])


def with_submission(args, func):
    if args.args:
        submission_dir = _submission_dir(args, args.args[0])
        if submission_dir is None:
            args.log.error("Could not find {}submission '{}'".format(
                'internal ' if args.internal else '',
                args.args[0]))
        else:
            func(Submission(submission_dir, args.repos))
    else:
        for d in sorted(_submission_dir(args).iterdir(), key=lambda d: d.name):
            if d.is_dir() and d.name != '_template' and d.joinpath('md.json').exists():
                args.log.info(d.name)
                func(Submission(d, args.repos))


@command()
def check(args):
    """Run checks on submission(s)

    dictionaria check [SUBMISSION]
    """
    def _check(s):
        if s.dictionary is None:
            args.log.error("No dictionary found in submission '{}'".format(s.id))
        else:
            s.dictionary.check()
    with_submission(args, _check)


@command()
def process(args):
    """Process submission(s)

    dictionaria process [SUBMISSION]
    """
    def _process(s):
        if s.dictionary is None:
            args.log.error("No dictionary found in submission '{}'".format(s.id))
        else:
            s.dictionary.process()
    with_submission(args, _process)


@command()
def new(args):
    """Initialise a new submission directory.

    dictionaria new SUBMISSION
    """
    d = _submission_dir(args).joinpath(args.args[0])
    if d.exists():
        raise ParserError('submission directory does already exist')
    d.mkdir()
    md = Metadata('', Language('', ''), None, {})
    jsonlib.dump(md.asdict(), d.joinpath('md.json'), indent=4)


def _submission_dir(args, path_or_id=None):
    subdir = 'submissions-internal' if args.internal else 'submissions'

    if path_or_id is None:
        return args.repos.joinpath(subdir)

    if Path(path_or_id).exists():
        return Path(path_or_id)

    for fname in args.repos.joinpath(subdir).iterdir():
        if fname.name == path_or_id:
            return fname

    return None


README_TEMPLATE = """
# {title}

> by {authors}

This repository contains the data underlying the published version of the dictionary
at [Dictionaria]({url}) as 
[CLDF](https://cldf.clld.org) [Dictionary](cldf).

Releases of this repository are archived with and accessible through 
[ZENODO](https://zenodo.org/communities/dictionaria) and the latest release
is published on the [Dictionaria website](https://dictionaria.clld.org).

{intro}
"""


@command()
def release(args):
    """Release a dictionary by copying it to its own public github repository.

    dictionaria release SUBMISSION REPOS
    """
    d = _submission_dir(args).joinpath(args.args[0])
    processed = d / 'processed'
    cldf_md_path = processed / 'cldf-md.json'
    if not cldf_md_path.exists():
        raise ParserError('submission has not been processed yet')
    cldf_md = jsonlib.load(cldf_md_path, object_pairs_hook=collections.OrderedDict)
    outdir = Path(args.args[1])
    if not outdir.exists():
        raise ParserError('publication repos does not exist')
    media = jsonlib.load(args.repos / 'cdstar.json')
    copy(d / 'md.json', outdir / 'md.json')

    def format_authors(authors):
        res, in_with = [], False
        for i, a in enumerate(authors):
            name = a['name'] if isinstance(a, dict) else a
            primary = a['primary'] if isinstance(a, dict) else True
            assert (in_with and not primary) or (not in_with)
            if i > 0:
                sep = 'and'
                if (not primary) and (not in_with):
                    in_with = True
                    sep = 'with'
                res.append(sep)
            res.append(name)
        return ' '.join(res)

    md = jsonlib.load(d / 'md.json')
    md_readme = {
        'url': 'https://dictionaria.clld.org/contributions/' + d.name,
        'intro': html2markdown.convert(read_text(d / 'md.html')),
        'title': md['properties'].get('title') or md['language']['name'] + ' dictionary',
        'authors': format_authors(md['authors']),
    }
    write_text(outdir / 'README.md', README_TEMPLATE.format(**md_readme))
    cldf = outdir / 'cldf'

    if not cldf.exists():
        cldf.mkdir()

    sources = d / 'sources.bib'
    if sources.exists():
        copy(sources, cldf / sources.name)
        cldf_md['dc:source'] = sources.name

    cldf_md['dc:creator'] = md_readme['authors']
    cldf_md['dc:title'] = md_readme['title']
    cldf_md['dc:identifier'] = md_readme['url']
    jsonlib.dump(cldf_md, cldf / 'Dictionary-metadata.json', indent=4)

    media_table = processed / 'media.csv'
    for table in cldf_md['tables']:
        if table['url'] != media_table.name:
            copy(processed / table['url'], cldf / table['url'])
    if media_table.exists():
        with UnicodeWriter(cldf / media_table.name) as w:
            for i, row in enumerate(reader(media_table, dicts=True)):
                if i == 0:
                    w.writerow(list(row.keys()) + ['URL', 'mimetype', 'size'])
                assert row['ID'] in media
                row['URL'] = 'https://cdstar.shh.mpg.de/bitstreams/{0[objid]}/{0[original]}'.format(
                    media[row['ID']])
                row['mimetype'] = media[row['ID']]['mimetype']
                row['size'] = media[row['ID']]['size']
                w.writerow(row.values())
