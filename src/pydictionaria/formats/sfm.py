# coding: utf8
from __future__ import unicode_literals, print_function, division
import re
from collections import ChainMap, defaultdict
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
                # FIXME This should go into sfm2cldf.make_spec
                example_markers = set(self.submission.md.properties.get('example_map', sfm2cldf.DEFAULT_EXAMPLE_MAP))
                if 'gloss_ref' in self.submission.md.properties:
                    example_markers.add(self.submission.md.properties['gloss_ref'])
                extractor = ExampleExtractor(example_markers, Corpus.from_dir(self.submission.dir), log)
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

        glosses = {}
        glosses_path = self.submission.dir.joinpath('glosses.flextext')
        if glosses_path.exists():
            logpath = self.submission.dir.joinpath('glosses.log')
            log_name = '%s.glosses' % self.submission.id
            with logpath.open('w', encoding='utf-8') as logfile:
                log = sfm2cldf.cldf_logger(log_name, logfile)
                gloss_ref_marker = props.get('gloss_ref')
                if gloss_ref_marker:
                    glosses = sfm2cldf.prepare_glosses(
                        glosses_path, gloss_ref_marker, examples, log)
                else:
                    log.error("'gloss_ref' marker not specified in md.json!")

        pos_filter = sfm2cldf.PartOfSpeechFilter()
        self.sfm.visit(pos_filter)
        self.sfm.visit(sfm2cldf.merge_pos)

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
        # if marker not in spec['ref_markers']
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
            spec['example_columns'],
            spec['entry_refs'],
            spec['sense_refs'],
            spec['example_refs'])

        if props.get('labels'):
            sfm2cldf.attach_column_titles(
                dataset['EntryTable'], spec['entry_map'], props['labels'])
            sfm2cldf.attach_column_titles(
                dataset['SenseTable'], spec['sense_map'], props['labels'])
            sfm2cldf.attach_column_titles(
                dataset['ExampleTable'], spec['example_map'], props['labels'])

        sfm2cldf.add_gloss_columns(dataset, glosses)

        entry_rows = (
            sfm2cldf.sfm_entry_to_cldf_row('EntryTable', spec['entry_map'], spec['entry_refs'], entry, lang_id)
            for entry in entries)
        sense_rows = (
            sfm2cldf.sfm_entry_to_cldf_row('SenseTable', spec['sense_map'], spec['sense_refs'], sense)
            for sense in senses)
        example_rows = (
            sfm2cldf.sfm_entry_to_cldf_row('ExampleTable', spec['example_map'], spec['example_refs'], example, lang_id)
            for example in examples)
        media_rows = (
            {'ID': fileid, 'Language_ID': lang_id, 'Filename': filename}
            for filename, fileid in sorted(media_extr.files))

        entry_filter = sfm2cldf.RequiredColumnsFilter(dataset['EntryTable'].tableSchema)
        entry_rows = entry_filter.filter(entry_rows)
        sense_filter = sfm2cldf.RequiredColumnsFilter(dataset['SenseTable'].tableSchema)
        sense_rows = sense_filter.filter(sense_rows)
        example_filter = sfm2cldf.RequiredColumnsFilter(dataset['ExampleTable'].tableSchema)
        example_rows = example_filter.filter(example_rows)
        media_filter = sfm2cldf.RequiredColumnsFilter(dataset['media.csv'].tableSchema)
        media_rows = media_filter.filter(media_rows)

        # TODO Factor out
        if glosses:
            def merge_gloss_into_example(example):
                if example['ID'] in glosses:
                    return ChainMap(glosses[example['ID']]['example'], example)
                return example
            example_rows = map(merge_gloss_into_example, example_rows)

        kwargs = {
            'EntryTable': entry_rows,
            'SenseTable': sense_rows,
            'ExampleTable': example_rows,
            'media.csv': media_rows}
        dataset.write(fname=outdir.joinpath('cldf-md.json'), **kwargs)

        logpath = self.submission.dir.joinpath('cldf.log')
        with logpath.open('w', encoding='utf8') as logfile:
            for msg in log_messages:
                print(msg, file=logfile)

            print(file=logfile)
            for error in pos_filter.errors:
                print('ERROR:', error, file=logfile)

            for error in entry_filter.warnings:
                print('\nERROR in entry: {}'.format(error), file=logfile)
            for error in sense_filter.warnings:
                print('\nERROR in sense: {}'.format(error), file=logfile)
            for error in example_filter.warnings:
                print('\nERROR in example: {}'.format(error), file=logfile)
            for error in media_filter.warnings:
                print('\nERROR in media entry: {}'.format(error), file=logfile)

            print(file=logfile)
            log_name = '%s.cldf' % self.submission.id
            dataset.validate(log=sfm2cldf.cldf_logger(log_name, logfile))
