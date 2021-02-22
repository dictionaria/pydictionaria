import sys
from collections import ChainMap

from clldutils.markup import Table
import pycldf

from pydictionaria.formats import base
from pydictionaria.formats.sfm_lib import (
    Check, CheckBibrefs, ComparisonMeanings, Database, Files, Stats, repair
)
from pydictionaria.example import Examples, concat_multilines
from pydictionaria.log import pprint

from pydictionaria import sfm2cldf

def load_examples(examples_path):
    if not examples_path.exists():
        return None
    examples = Examples()
    examples.read(examples_path, marker_map={'sf': 'sfx'})
    examples.visit(concat_multilines)
    return examples


class Dictionary(base.Dictionary):
    _fname = 'db.sfm'

    def __init__(self, submission):
        base.Dictionary.__init__(self, submission)
        kw = {}
        for key, default in [
            ('encoding', 'utf8'),
            ('entry_sep', '\\lx '),
        ]:
            kw[key] = submission.md.properties.get(key, default)
        kw['marker_map'] = ChainMap(
            submission.md.properties.get('marker_map', {}),
            sfm2cldf.DEFAULT_MARKER_MAP)
        self.sfm = Database(submission.dir.joinpath(self._fname), **kw)

    @classmethod
    def match(cls, submission):
        return submission.dir.joinpath(cls._fname).exists()

    def search(self, **query):
        def match(entry, marker, value):
            if isinstance(value, int):
                return len(entry.getall(marker)) == value
            return value in ' ; '.join(entry.getall(marker))

        count = 0
        for entry in self.sfm:
            if all(match(entry, marker, value) for marker, value in query.items()):
                print(('%s\n' % entry).encode('utf8'))
                count += 1
        print('{0} matches'.format(count))

    def stat(self):
        stats = Stats()
        self.sfm.visit(stats)
        table = Table('Marker', 'Repr.', 'Total', 'Max/Entry', 'Mult.values')
        for marker, count in stats.count.most_common():
            table.append([
                marker,
                count,
                stats.total[marker],
                stats._mult_markers[marker],
                'yes' if marker in stats._implicit_mult_markers else 'no'])
        print(table.render(tablefmt='simple', condensed=False))

    def check(self):
        if self.submission.module and hasattr(self.submission.module, 'process'):
            self.sfm.visit(self.submission.module.process)
        checks = Files(
            self.submission.cdstar.items,
            self.submission.media_sids,
            mode='check')
        self.sfm.visit(checks)
        for entry, marker, name in checks.missing_files:
            pprint(entry, 'missing file', marker, name)
        # Flushing stdout to ensure the messages from `pprint` always appear
        # before the messages from the checks below (which print to stderr)
        sys.stdout.flush()
        self.sfm.visit(Check(self.sfm))
        self.sfm.visit(CheckBibrefs(self.bibentries))

    def repair(self):
        enc = self.submission.md.properties.get('encoding', 'utf8')
        sfm = Database(self.submission.dir.joinpath(self._fname), encoding=enc)
        repair(sfm)
        with self.submission.dir.joinpath(
                self._fname).open('w', encoding=enc, errors='replace') as fp:
            for entry in sfm:
                fp.write(str(entry))
                fp.write('\n\n')

    def add_comparison_meanings(self, concepticon, marker):
        enc = self.submission.md.properties.get('encoding', 'utf8')
        sfm = Database(
            self.submission.dir.joinpath(self._fname), encoding=enc, keep_empty=True)
        sfm.visit(ComparisonMeanings(concepticon, marker=marker))
        with self.submission.dir.joinpath(
                self._fname).open('w', encoding=enc, errors='replace') as fp:
            for entry in sfm:
                fp.write(str(entry))
                fp.write('\n\n')

    def _process(self, outdir):
        if self.submission.module:
            if hasattr(self.submission.module, 'reorganize'):
                # Run submission-specific reorganisation of the SFM database:
                self.sfm = self.submission.module.reorganize(self.sfm)
            if hasattr(self.submission.module, 'process'):
                # Run submission-specific preprocessing/normalization of SFM:
                self.sfm.visit(self.submission.module.process)

        examples = load_examples(self.submission.dir.joinpath('examples.sfm'))

        cldf_log_path = self.submission.dir / 'cldf.log'
        with cldf_log_path.open('w', encoding='utf-8') as log_file:
            log_name = '%s.cldf' % self.submission.id
            cldf_log = sfm2cldf.make_log(log_name, log_file)

            language_id = (
                self.submission.md.language.isocode
                or self.submission.md.language.glottocode
                or '')
            entry_rows, sense_rows, example_rows, media_rows = sfm2cldf.process_dataset(
                self.submission.id, language_id, self.submission.md.properties,
                self.sfm, examples, self.submission.cdstar.items,
                glosses_path=self.submission.dir / 'glosses.flextext',
                examples_log_path=self.submission.dir / 'examples.log',
                glosses_log_path=self.submission.dir / 'glosses.log',
                cldf_log=cldf_log)

            cldf = pycldf.Dictionary.in_dir(self.submission.dir / 'processed')
            sfm2cldf.make_cldf_schema(
                cldf, self.submission.md.properties,
                entry_rows, sense_rows, example_rows, media_rows)

            sfm2cldf.attach_column_titles(cldf, self.submission.md.properties)

            print(file=log_file)

            entry_rows = sfm2cldf.ensure_required_columns(
                cldf, 'EntryTable', entry_rows, cldf_log)
            sense_rows = sfm2cldf.ensure_required_columns(
                cldf, 'SenseTable', sense_rows, cldf_log)
            example_rows = sfm2cldf.ensure_required_columns(
                cldf, 'ExampleTable', example_rows, cldf_log)
            media_rows = sfm2cldf.ensure_required_columns(
                cldf, 'media.csv', media_rows, cldf_log)

            entry_rows = sfm2cldf.remove_senseless_entries(
                sense_rows, entry_rows, cldf_log)

            kwargs = {
                'EntryTable': entry_rows,
                'SenseTable': sense_rows,
                'ExampleTable': example_rows,
                'media.csv': media_rows,
                'LanguageTable': [
                    {
                        'ID': language_id,
                        'Name': self.submission.md.language.name,
                        'ISO639P3code': self.submission.md.language.isocode,
                        'Glottocode': self.submission.md.language.glottocode}]}

            cldf.write(fname=outdir.joinpath('cldf-md.json'), **kwargs)
            cldf.validate(log=sfm2cldf.LogOnlyBaseNames(cldf_log, {}))
