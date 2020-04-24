"""
Upload media files of a submission to CDSTAR
"""
import os

from clldutils.clilib import PathType
from clldutils.path import md5
from cdstarcat.catalog import Catalog

from pydictionaria.util import MediaCatalog
from pydictionaria.cli_util import add_submission, get_submission


def register(parser):
    add_submission(parser)
    parser.add_argument(
        '--cdstar-catalog',
        default=os.environ.get('CDSTAR_CATALOG'),
        help='CDSTAR catalog',
        type=PathType(type='file'))
    for kw in ['URL', 'USER', 'PWD']:
        parser.add_argument(
            '--cdstar-{0}'.format(kw.lower()),
            help='CDSTAR service {0}'.format(kw.lower()),
            default=os.environ.get('CDSTAR_{0}'.format(kw)),
        )


def run(args):
    submission = get_submission(args)
    assert submission.md

    for mtype in submission.media:
        if submission.dir.joinpath(mtype).exists():
            _upload(args, submission.dir.joinpath(mtype), submission.id)

    args.log.info(args.cdstar_catalog)


def _upload(args, d, name):
    with MediaCatalog(args.repos) as mcat:
        with Catalog(
                args.cdstar_catalog,
                cdstar_url=args.cdstar_url,
                cdstar_user=args.cdstar_user,
                cdstar_pwd=args.cdstar_pwd) as cat:
            for fname in d.iterdir():
                if fname.is_file():
                    if md5(fname) not in mcat.items:
                        md = {
                            'collection': 'dictionaria',
                            'path': '%s' % fname.relative_to(args.repos),
                            'dictionary': name,
                        }
                        _, _, obj = list(cat.create(fname, md, filter_=lambda f: True))[0]
                        mcat.add(obj, sid=name, type=fname.parent.name, fname=fname.name)
