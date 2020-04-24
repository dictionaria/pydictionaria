"""
Process submission
"""
from pydictionaria.cli_util import add_submission, get_submission


def register(parser):
    add_submission(parser)


def run(args):
    s = get_submission(args)
    s.dictionary.process()
    if s.module:
        pp = getattr(s.module, 'postprocess', None)
        if pp:
            pp(s.dir / 'processed')
