import pathlib

from clldutils.clilib import ParserError

from pydictionaria.submission import Submission


def add_submission(parser):
    parser.add_argument(
        'submission',
        metavar='SUBMISSION_ID',
    )


def get_submission_dir(args):
    return args.repos / ('submissions-internal' if args.internal else 'submissions')


def get_submission(args):
    d = pathlib.Path(args.submission)
    if d.exists() and d.is_dir():
        return Submission(d, args.repos)
    d = get_submission_dir(args) / args.submission
    if not d.exists():
        raise ParserError('submission dir {0} does not exist'.format(d))
    return Submission(d, args.repos)
