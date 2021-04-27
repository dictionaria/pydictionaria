"""
Updload media files of a submission to CDSTAR.
"""

import os
import pathlib

from cdstarcat.catalog import Catalog
from cldfbench.cli_util import with_dataset, add_dataset_spec
from clldutils.clilib import PathType
from clldutils.path import md5

from pydictionaria.util import MediaCatalog


def register(parser):
    add_dataset_spec(parser)
    parser.add_argument(
        '--media-dir',
        default=pathlib.Path('upload'),
        help='directory containing the media files',
        type=PathType(type='dir'))
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


def _upload(args, dataset, dir, cdstar_json):
    with MediaCatalog(cdstar_json.parent) as mcat:
        with Catalog(
            args.cdstar_catalog,
            cdstar_url=args.cdstar_url,
            cdstar_user=args.cdstar_user,
            cdstar_pwd=args.cdstar_pwd
        ) as cat:
            for fname in dir.iterdir():
                if fname.is_file() and md5(fname) not in mcat.items:
                    md = {
                        'collection': 'dictionaria',
                        'path': '%s' % fname.relative_to(dataset.dir),
                        'dictionary': dataset.id,
                    }
                    _, _, obj = list(cat.create(fname, md, filter_=lambda f: True))[0]
                    mcat.add(obj, sid=dataset.id, type=fname.parent.name, fname=fname.name)


def upload(dataset, args):
    cdstar_json = dataset.etc_dir / 'cdstar.json'
    for mtype in ['audio', 'image', 'docs']:
        dir = args.media_dir / mtype
        if dir.exists():
            _upload(args, dataset, dir, cdstar_json)

    args.log.info(args.cdstar_catalog)


def run(args):
    with_dataset(args, upload)
