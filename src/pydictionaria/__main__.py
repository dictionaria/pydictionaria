import sys

from clldutils.clilib import ArgumentParserWithLogging
from clldutils.path import Path

import pydictionaria
from pydictionaria import commands
assert commands


def main():  # pragma: no cover
    parser = ArgumentParserWithLogging(pydictionaria.__name__)
    parser.add_argument('--internal', dest='internal', action='store_true')
    parser.add_argument('--no-internal', dest='internal', action='store_false')
    parser.add_argument('--repos', type=Path, default=Path('dictionaria-internal'))
    parser.add_argument(
        '--concepticon-repos',
        type=Path,
        default=Path('concepticon-data'))
    parser.set_defaults(internal=False)
    sys.exit(parser.main())
