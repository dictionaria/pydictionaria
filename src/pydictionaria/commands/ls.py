"""
List submissions
"""
from clldutils.clilib import add_format, Table

from pydictionaria.cli_util import get_submission_dir
from pydictionaria.submission import Submission


def register(parser):
    add_format(parser, 'simple')


def run(args):
    with Table(args, 'ID', 'Format', 'Language', 'Glottocode', 'Authors', 'Published') as table:
        for d in sorted(get_submission_dir(args).iterdir(), key=lambda p: p.stem):
            try:
                s = Submission(d, args.repos)
                md = s.md
            except:  # noqa: E722
                args.log.exception('error loading submission {0}'.format(d))
                continue
            if md:
                table.append([
                    s.id,
                    s.dictionary.format if s.dictionary else '',
                    md.language.name,
                    md.language.glottocode,
                    md.author_names,
                    md.date_published or '',
                ])
