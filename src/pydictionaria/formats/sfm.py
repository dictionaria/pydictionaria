import sys
from collections import ChainMap
from itertools import chain
from functools import partial

from clldutils.markup import Table

from pydictionaria.formats import base
from pydictionaria.formats.sfm_lib import (
    Stats, Rearrange, Files, ExampleExtractor, normalize, ComparisonMeanings,
    Check, repair, Database, CheckBibrefs, EXAMPLE_MARKER_MAP
)
from pydictionaria.example import Corpus, Examples, concat_multilines
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
        if self.submission.module and hasattr(self.submission.module, 'process'):
            # Run submission-specific preprocessing/normalization of SFM:
            self.sfm.visit(self.submission.module.process)
        # Run generic normalization of SFM:
        self.sfm.visit(normalize)
        self.sfm.visit(Rearrange())

        # Replace media references with md5 sums of referenced files:
        files = Files(self.submission)
        self.sfm.visit(files)

        # Process FLEx's cross-references in \lf markers
        flexref_map = ChainMap(
            self.submission.md.properties.get('flexref_map', {}),
            sfm2cldf.DEFAULT_FLEXREF_MAP)
        self.sfm.visit(partial(sfm2cldf.preprocess_flex_crossrefs, flexref_map))

        examples_path = self.submission.dir.joinpath('examples.sfm')
        if examples_path.exists():  # Examples are submitted as separate SFM file.
            examples = Examples()
            examples.read(examples_path, marker_map={'sf': 'sfx'})
            examples.visit(concat_multilines)
            original_amount = len(examples)
            cited = {
                xref
                for example in self.sfm
                for xref in example.getall('xref')}
            examples = Examples(
                example
                for example in examples
                if example.id in cited)
            print('pruning', original_amount - len(examples), 'examples from', original_amount)
        else:
            with self.submission.dir.joinpath(
                    'examples.log').open('w', encoding='utf8') as log:
                # FIXME This should go into sfm2cldf.make_spec
                example_markers = set(
                    self.submission.md.properties.get('example_map', sfm2cldf.DEFAULT_EXAMPLE_MAP))
                example_markers.add('sfx')
                if 'gloss_ref' in self.submission.md.properties:
                    example_markers.add(self.submission.md.properties['gloss_ref'])
                extractor = ExampleExtractor(
                    example_markers, Corpus.from_dir(self.submission.dir), log)
                self.sfm.visit(extractor)
                examples = Examples(extractor.examples.values())

        props = self.submission.md.properties
        logpath = self.submission.dir.joinpath('cldf.log')
        with logpath.open('w', encoding='utf8') as logfile:
            log_name = '%s.cldf' % self.submission.id
            log = sfm2cldf.make_log(log_name, logfile)

            all_markers = {
                marker
                for entry in chain(self.sfm, examples)
                for marker, _ in entry}
            spec = sfm2cldf.make_spec(props, all_markers)

            all_markers -= spec['entry_markers']
            all_markers -= spec['sense_markers']
            all_markers -= spec['example_markers']
            all_markers -= set(EXAMPLE_MARKER_MAP.values())
            all_markers -= {'lf', 'lv', 'le'}
            if all_markers:
                marker_list = ', '.join(sorted(all_markers))
                log.warning('No CLDF column defined for markers: %s', marker_list)

            example_index = sfm2cldf.prepare_examples(
                spec['example_id'],
                spec['example_markers'],
                examples)
            examples = Examples(example_index.values())

            glosses = {}
            glosses_path = self.submission.dir.joinpath('glosses.flextext')
            if glosses_path.exists():
                gloss_logpath = self.submission.dir.joinpath('glosses.log')
                gloss_logname = '%s.glosses' % self.submission.id
                with gloss_logpath.open('w', encoding='utf-8') as gloss_logfile:
                    gloss_log = sfm2cldf.make_log(gloss_logname, gloss_logfile)
                    gloss_ref_marker = props.get('gloss_ref')
                    if gloss_ref_marker:
                        glosses = sfm2cldf.prepare_glosses(
                            glosses_path, gloss_ref_marker, examples, gloss_log)
                    else:
                        gloss_log.error("md.json does not specifiy 'gloss_ref' marker")
                    sfm2cldf.check_for_missing_glosses(
                        gloss_ref_marker, glosses, examples, gloss_log)

            self.sfm.visit(lambda e: sfm2cldf.validate_ps(e, log))
            self.sfm.visit(sfm2cldf.merge_pos)

            crossref_markers = (
                sfm2cldf.DEFAULT_CROSS_REFERENCES
                | set(props.get('cross_references', ()))
                | set(flexref_map.values()))

            entry_extr = sfm2cldf.EntryExtractor(
                spec['entry_id'],
                spec['entry_markers'])
            sense_extr = sfm2cldf.SenseExtractor(
                spec['sense_sep'],
                spec['sense_markers'],
                crossref_markers,
                log)

            rest = [entry_extr(entry) for entry in self.sfm]
            rest = [sense_extr(entry) for entry in rest if entry]

            entries = entry_extr.entries
            senses = sense_extr.senses

            ex_ref = sfm2cldf.ExampleReferencer(example_index)
            senses.visit(ex_ref)

            if ex_ref.invalid_example_ids:
                example_list = ', '.join(
                    sorted(map(repr, ex_ref.invalid_example_ids)))
                log.warning('senses refer to non-existent examples: %s', example_list)

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
                log.warning('unknown media files: %s', file_list)

            id_index = sfm2cldf.make_id_index(entries)

            crossref_processor = sfm2cldf.CrossRefs(id_index, crossref_markers)
            entries.visit(crossref_processor)
            senses.visit(crossref_processor)
            examples.visit(crossref_processor)

            try:
                link_processor = sfm2cldf.make_link_processor(
                    props, id_index, entries)
                if link_processor is not None:
                    entries.visit(link_processor)
                    senses.visit(link_processor)
                    examples.visit(link_processor)
            except ValueError as e:
                log.warning('could not process links: %s', str(e))

            lang_id = (
                self.submission.md.language.isocode
                or self.submission.md.language.glottocode
                or '')

            entry_crossref_cols = {c for m, c in spec['entry_map'].items() if m in crossref_markers}
            sense_crossref_cols = {c for m, c in spec['sense_map'].items() if m in crossref_markers}
            example_crossref_cols = {
                c for m, c in spec['example_map'].items() if m in crossref_markers}
            dataset = sfm2cldf.make_cldf_dataset(
                outdir,
                spec['entry_columns'],
                spec['sense_columns'],
                spec['example_columns'],
                spec['entry_sources'],
                spec['sense_sources'],
                spec['example_sources'],
                entry_crossref_cols,
                sense_crossref_cols,
                example_crossref_cols,
                log)

            if props.get('labels'):
                sfm2cldf.attach_column_titles(
                    dataset['EntryTable'], spec['entry_map'], props['labels'])
                sfm2cldf.attach_column_titles(
                    dataset['SenseTable'], spec['sense_map'], props['labels'])
                sfm2cldf.attach_column_titles(
                    dataset['ExampleTable'], spec['example_map'], props['labels'])

            sfm2cldf.add_gloss_columns(dataset, glosses)

            entry_rows = [
                sfm2cldf.sfm_entry_to_cldf_row(
                    'EntryTable',
                    spec['entry_map'],
                    spec['entry_sources'],
                    entry_crossref_cols,
                    entry,
                    lang_id)
                for entry in entries]
            sense_rows = [
                sfm2cldf.sfm_entry_to_cldf_row(
                    'SenseTable',
                    spec['sense_map'],
                    spec['sense_sources'],
                    sense_crossref_cols,
                    sense)
                for sense in senses]
            example_rows = [
                sfm2cldf.sfm_entry_to_cldf_row(
                    'ExampleTable',
                    spec['example_map'],
                    spec['example_sources'],
                    sense_crossref_cols,
                    example,
                    lang_id)
                for example in examples]
            media_rows = [
                {'ID': fileid, 'Language_ID': lang_id, 'Filename': filename}
                for filename, fileid in sorted(media_extr.files)]

            # Separator in log file
            print(file=logfile)

            entry_rows = list(
                sfm2cldf.ensure_required_columns(dataset, 'EntryTable', entry_rows, log))
            sense_rows = list(
                sfm2cldf.ensure_required_columns(dataset, 'SenseTable', sense_rows, log))
            example_rows = list(
                sfm2cldf.ensure_required_columns(dataset, 'ExampleTable', example_rows, log))
            media_rows = list(
                sfm2cldf.ensure_required_columns(dataset, 'media.csv', media_rows, log))

            entry_rows = list(sfm2cldf.remove_senseless_entries(sense_rows, entry_rows, log))

            if glosses:
                example_rows = [
                    sfm2cldf.merge_gloss_into_example(glosses, row)
                    for row in example_rows]

            kwargs = {
                'EntryTable': entry_rows,
                'SenseTable': sense_rows,
                'ExampleTable': example_rows,
                'media.csv': media_rows}
            dataset.write(fname=outdir.joinpath('cldf-md.json'), **kwargs)
            dataset.validate(log=sfm2cldf.LogOnlyBaseNames(log, {}))
