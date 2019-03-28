# coding: utf8
from __future__ import unicode_literals, print_function, division
import re
from collections import ChainMap
from itertools import chain

from clldutils.markup import Table
from clldutils import sfm

from pydictionaria.formats import base
from pydictionaria.formats.sfm_lib import (
    Stats, Rearrange, Files, ExampleExtractor, normalize, ComparisonMeanings,
    Check, repair, Database, CheckBibrefs,
)
from pydictionaria.example import Corpus, Examples
from pydictionaria.log import pprint

from pydictionaria import sfm2cldf

DEFAULT_MARKER_MAP = {
    'd_Eng': 'de',
    'g_Eng': 'ge',
    'ps_Eng': 'ps',
    'sc_Eng': 'sc',
    'sd_Eng': 'sd',
    'x_Eng': 'xe'}


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
            DEFAULT_MARKER_MAP)
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
        checks = Files(self.submission, mode='check')
        self.sfm.visit(checks)
        for entry, marker, name in checks.missing_files:
            pprint(entry, 'missing file', marker, name)
        self.sfm.visit(Check(self.sfm))
        self.sfm.visit(CheckBibrefs(self.bibentries))

    def repair(self):
        enc = self.submission.md.properties.get('encoding', 'utf8')
        sfm = Database(self.submission.dir.joinpath(self._fname), encoding=enc)
        repair(sfm)
        with self.submission.dir.joinpath(self._fname).open('w', encoding=enc, errors='replace') as fp:
            for entry in sfm:
                fp.write(entry.__unicode__())
                fp.write('\n\n')

    def add_comparison_meanings(self, concepticon, marker):
        enc = self.submission.md.properties.get('encoding', 'utf8')
        sfm = Database(
            self.submission.dir.joinpath(self._fname), encoding=enc, keep_empty=True)
        sfm.visit(ComparisonMeanings(concepticon, marker=marker))
        with self.submission.dir.joinpath(self._fname).open('w', encoding=enc, errors='replace') as fp:
            for entry in sfm:
                fp.write(entry.__unicode__())
                fp.write('\n\n')

    def _process(self, outdir):
        if self.submission.module and hasattr(self.submission.module, 'process'):
            self.sfm.visit(self.submission.module.process)
        self.sfm.visit(normalize)
        self.sfm.visit(Rearrange())
        files = Files(self.submission)
        self.sfm.visit(files)

        examples_path = self.submission.dir.joinpath('examples.sfm')
        if examples_path.exists():
            unchecked_examples = Examples()
            unchecked_examples.read(examples_path)
            unchecked_examples.concat_multilines()
            eids = set(e.id for e in unchecked_examples)
            cited = []
            for e in self.sfm:
                cited.extend(e.getall('xref'))
            cited = set(cited)
            print('pruning {0} uncited examples from {1}'.format(
                len(eids.difference(cited)), len(eids)))
            examples = Examples(
                e for e in unchecked_examples
                if e.id in cited)
        else:
            with self.submission.dir.joinpath(
                    'examples.log').open('w', encoding='utf8') as log:
                extractor = ExampleExtractor(Corpus.from_dir(self.submission.dir), log)
                self.sfm.visit(extractor)
                examples = Examples(extractor.examples.values())

        props = self.submission.md.properties
        log_messages = []

        all_markers = {
            marker
            for entry in chain(self.sfm, examples)
            for marker, _ in entry}
        spec = sfm2cldf.make_spec(props, all_markers)

        example_index, unexpected_markers = sfm2cldf.prepare_examples(
            spec['example_id'],
            spec['example_markers'],
            examples)
        examples = Examples(example_index.values())

        entry_extr = sfm2cldf.EntryExtractor(
            spec['entry_id'],
            spec['entry_markers'])
        sense_extr = sfm2cldf.SenseExtractor(
            spec['sense_sep'],
            spec['sense_markers'])

        rest = map(entry_extr, self.sfm)
        rest = (sense_extr(entry) for entry in rest if entry)
        unexpected_markers.update(
            marker
            for entry in rest
            for marker, _ in entry)

        if unexpected_markers:
            marker_list = ', '.join(sorted(unexpected_markers))
            msg = 'Unexpected markers: {}'.format(marker_list)
            print(msg)
            log_messages.append(msg)

        entries = entry_extr.entries
        senses = sense_extr.senses

        ex_ref = sfm2cldf.ExampleReferencer(example_index)
        senses.visit(ex_ref)

        if ex_ref.invalid_example_ids:
            example_list = ', '.join(
                sorted(map(repr, ex_ref.invalid_example_ids)))
            msg = 'Unknown examples references by senses: {}'.format(example_list)
            print(msg)
            log_messages.append(msg)

        media_id_index = {
            entry['fname']: checksum
            for checksum, entry in self.submission.cdstar.items.items()
            if entry['sid'] in self.submission.media_sids}
        for fname in list(media_id_index.keys()):
            media_id_index[fname.split('.')[0]] = media_id_index[fname]
        media_extr = sfm2cldf.MediaExtractor(
            'sf',
            media_id_index,
            self.submission.cdstar.items)

        entries.visit(media_extr)
        media_extr.tag = 'pc'
        senses.visit(media_extr)
        media_extr.tag = 'sfx'
        examples.visit(media_extr)

        if media_extr.orphans:
            file_list = ', '.join(sorted(map(repr, media_extr.orphans)))
            msg = 'Unknown media files: {}'.format(file_list)
            print(msg)
            log_messages.append(msg)

        try:
            sfm2cldf.process_links(props, entries, senses, examples)
        except ValueError as e:
            msg = 'Could not process links: {}'.format(e)
            print(msg)
            log_messages.append(msg)

        lang_id = (
            self.submission.md.language.isocode
            or self.submission.md.language.glottocode
            or '')

        dataset = sfm2cldf.make_cldf_dataset(
            outdir,
            spec['entry_columns'],
            spec['sense_columns'],
            spec['example_columns'])

        entry_rows = (
            sfm2cldf.sfm_entry_to_cldf_row(spec['entry_map'], entry, lang_id)
            for entry in entries)
        sense_rows = (
            sfm2cldf.sfm_entry_to_cldf_row(spec['sense_map'], sense)
            for sense in senses)
        example_rows = (
            sfm2cldf.sfm_entry_to_cldf_row(spec['example_map'], example, lang_id)
            for example in examples)
        media_rows = (
            {'ID': fileid, 'Language_ID': lang_id, 'Filename': filename}
            for filename, fileid in sorted(media_extr.files))

        row_filter = sfm2cldf.RowFilter()
        entry_rows = row_filter.filter(
            sfm2cldf.RequiredColumns(dataset['EntryTable'].tableSchema),
            entry_rows)
        sense_rows = row_filter.filter(
            sfm2cldf.RequiredColumns(dataset['SenseTable'].tableSchema),
            sense_rows)
        example_rows = row_filter.filter(
            sfm2cldf.RequiredColumns(dataset['ExampleTable'].tableSchema),
            example_rows)
        media_rows = row_filter.filter(
            sfm2cldf.RequiredColumns(dataset['media.csv'].tableSchema),
            media_rows)

        if log_messages or row_filter.filtered:
            logpath = self.submission.dir.joinpath('cldf.log')
            with logpath.open('w', encoding='utf8') as logfile:
                for msg in log_messages:
                    print(msg, file=logfile)
                for row in row_filter.filtered.values():
                    print('\nRequired field missing in CLDF row:', file=logfile)
                    msg ='\n'.join('{}: {}'.format(repr(k), repr(v)) for k, v in row.items())
                    print(msg, file=logfile)

        kwargs = {
            'EntryTable': entry_rows,
            'SenseTable': sense_rows,
            'ExampleTable': example_rows,
            'media.csv': media_rows}
        dataset.write(fname=outdir.joinpath('cldf-md.json'), **kwargs)
