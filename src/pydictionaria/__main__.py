import sys
import pathlib
import contextlib

from clldutils.clilib import get_parser_and_subparsers, register_subcommands, PathType, ParserError
from clldutils.loglib import Logging

import pydictionaria.commands


def main(args=None, catch_all=False, parsed_args=None):
    parser, subparsers = get_parser_and_subparsers('dictionaria')
    parser.add_argument('--internal', dest='internal', action='store_true')
    parser.add_argument('--no-internal', dest='internal', action='store_false')
    parser.add_argument(
        '--repos',
        type=PathType(type='dir'),
        default=pathlib.Path('.'),
        help='Location of clone of dictionaria/dictionaria-intern')
    register_subcommands(subparsers, pydictionaria.commands)

    args = parsed_args or parser.parse_args(args=args)

    if not hasattr(args, "main"):
        parser.print_help()
        return 1

    if not args.repos.joinpath('submissions').exists():
        raise ParserError('Invalid repository {0}'.format(args.repos))

    with contextlib.ExitStack() as stack:
        stack.enter_context(Logging(args.log, level=args.log_level))
        try:
            return args.main(args) or 0
        except KeyboardInterrupt:  # pragma: no cover
            return 0
        except Exception as e:  # pragma: no cover
            if catch_all:
                print(e)
                return 1
            raise


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main() or 0)
