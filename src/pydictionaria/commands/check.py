"""
Check submission
"""
from pydictionaria.cli_util import add_submission, get_submission


def register(parser):
    add_submission(parser)


def run(args):
    get_submission(args).dictionary.check()
