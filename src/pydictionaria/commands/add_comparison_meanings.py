"""
Add automatically guessed comparison meanings to a dictionary
"""
from pyconcepticon import Concepticon

from pydictionaria.cli_util import add_submission, get_submission


def register(parser):
    add_submission(parser)
    parser.add_argument('concepticon-repos')
    parser.add_argument('--marker', default='zcom2', help='SFM marker name')


def run(args):
    s = get_submission(args)

    if not hasattr(s.dictionary, 'add_comparison_meanings'):
        args.log.warn('Format of submission does not support this command.')
        return

    s.dictionary.add_comparison_meanings(Concepticon(args.concepticon_repos), marker=args.marker)
