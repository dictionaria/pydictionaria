"""
Initialise a new submission directory.
"""
from clldutils.clilib import ParserError
from clldutils import jsonlib

from pydictionaria.cli_util import add_submission, get_submission_dir
from pydictionaria.submission import Metadata, Language


def register(parser):
    add_submission(parser)


def run(args):
    d = get_submission_dir(args) / args.submission
    if d.exists():
        raise ParserError('submission directory does already exist')
    d.mkdir()
    md = Metadata('', Language('', ''), None, {})
    jsonlib.dump(md.asdict(), d.joinpath('md.json'), indent=4)
