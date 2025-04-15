"""
Updload media files of a submission to CDSTAR.
"""

import os
import pathlib
from contextlib import ExitStack

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
            f'--cdstar-{kw.lower()}',
            help=f'CDSTAR service {kw.lower()}',
            default=os.environ.get(f'CDSTAR_{kw}'),
        )


def _upload(args, dataset, file_dir, cdstar_json):
    with ExitStack() as stack:
        mcat = MediaCatalog(cdstar_json.parent)
        stack.enter_context(mcat)
        cat = Catalog(
            args.cdstar_catalog,
            cdstar_url=args.cdstar_url,
            cdstar_user=args.cdstar_user,
            cdstar_pwd=args.cdstar_pwd)
        stack.enter_context(cat)
        for fname in file_dir.iterdir():
            if fname.is_file() and md5(fname) not in mcat.items:
                md = {
                    'collection': 'dictionaria',
                    'path': str(fname.relative_to(dataset.file_dir)),
                    'dictionary': dataset.id,
                }
                _, _, obj = next(cat.create(fname, md, filter_=lambda _: True))
                mcat.add(obj, sid=dataset.id, type=fname.parent.name, fname=fname.name)


def upload(dataset, args):
    cdstar_json = dataset.etc_dir / 'cdstar.json'
    for mtype in ['audio', 'image', 'docs']:
        type_dir = args.media_dir / mtype
        if type_dir.exists():
            _upload(args, dataset, type_dir, cdstar_json)

    args.log.info(args.cdstar_catalog)


def run(args):
    with_dataset(args, upload)
