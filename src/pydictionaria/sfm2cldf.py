from collections import OrderedDict, ChainMap, defaultdict
import re
import logging
import copy
import os.path
import sys

from clldutils import sfm
import pycldf

from pydictionaria import flextext
from pydictionaria.util import split_ids

DEFAULT_ENTRY_SEP = r'\lx '
DEFAULT_ENTRY_ID = 'lx'
DEFAULT_SENSE_SEP = 'sn'
DEFAULT_EXAMPLE_ID = 'ref'

DEFAULT_ENTRY_MAP = {
    'lx': 'Headword',
    'ps': 'Part_Of_Speech',
    'al': 'Alternative_Form',
    'et': 'Etymology',
    'lc': 'Citation_Form',
    'mn': 'Main_Entry',
    'cf': 'Entry_IDs',
    'cont': 'Contains',
    'va': 'Variant_Form'}

DEFAULT_SENSE_MAP = {
    'de': 'Description',
    'nt': 'Comment',
    'sc': 'Scientific_Name',
    'sd': 'Semantic_Domain',
    'sy': 'Synonym',
    'an': 'Antonym',
    'zcom1': 'Concepticon_ID'}

DEFAULT_EXAMPLE_MAP = {
    'rf': 'Corpus_Reference',
    'tx': 'Primary_Text',
    'mb': 'Analyzed_Word',
    'gl': 'Gloss',
    'ot': 'alt_translation1',
    'ota': 'alt_translation2',
    'ft': 'Translated_Text'}

DEFAULT_FLEXREF_MAP = {
    'cf': 'cf',
    'syn': 'sy',
    'ant': 'an'}

DEFAULT_SOURCES = {}

DEFAULT_PROCESS_LINKS_IN_MARKERS = set()
DEFAULT_LINK_LABEL_MARKER = 'lx'
DEFAULT_CROSS_REFERENCES = {'mn', 'cf', 'cont', 'sy', 'an'}

DEFAULT_SEPARATOR = ' ; '
SEPARATORS = {
    'Contains': DEFAULT_SEPARATOR,
    'Synonym': DEFAULT_SEPARATOR,
    'Antonym': DEFAULT_SEPARATOR,
    'Entry_IDs': DEFAULT_SEPARATOR,
    'Media_IDs': DEFAULT_SEPARATOR,
    'Sense_IDs': DEFAULT_SEPARATOR,
    'Main_Entry': DEFAULT_SEPARATOR}


def _local_mapping(json_mapping, default_mapping, marker_set, source_mapping):
    mapped_values = set(json_mapping.values())
    global_map = ChainMap(
        json_mapping,
        {k: v for k, v in default_mapping.items() if v not in mapped_values})
    markers = set(global_map.keys()) & marker_set
    mapping = {
        marker: value
        for marker, value in global_map.items()
        if marker in markers}
    columns = set(mapping.values())

    sources = {
        marker: mapping[target]
        for marker, target in source_mapping.items()
        if marker in marker_set and target in mapping}
    markers.update(sources)

    return mapping, markers, columns, sources


def make_spec(properties, marker_set):
    source_mapping = ChainMap(properties.get('sources', {}), DEFAULT_SOURCES)

    entry_map, entry_markers, entry_columns, entry_sources = _local_mapping(
        properties.get('entry_map', {}),
        DEFAULT_ENTRY_MAP,
        marker_set,
        source_mapping)
    # Note: entry_sep is a string like '\\TAG ' (required by clldutils)
    entry_sep = properties.get('entry_sep', DEFAULT_ENTRY_SEP).strip().lstrip('\\')
    entry_id = properties.get('entry_id', DEFAULT_ENTRY_ID)
    entry_markers.update((entry_sep, entry_id, 'hm', 'sf', 'lc'))
    entry_columns.add('Media_IDs')

    sense_map, sense_markers, sense_columns, sense_sources = _local_mapping(
        properties.get('sense_map', {}),
        DEFAULT_SENSE_MAP,
        marker_set,
        source_mapping)
    sense_sep = properties.get('sense_sep', DEFAULT_SENSE_SEP)
    sense_markers.update((sense_sep, 'xref', 'pc'))
    sense_columns.add('Media_IDs')

    example_map, example_markers, example_columns, example_sources = _local_mapping(
        properties.get('example_map', {}),
        DEFAULT_EXAMPLE_MAP,
        marker_set,
        source_mapping)
    example_id = properties.get('example_id', DEFAULT_EXAMPLE_ID)
    example_markers.update((example_id, 'sfx'))
    example_columns.update(('Sense_IDs', 'Media_IDs'))

    gloss_ref = properties.get('gloss_ref')
    if gloss_ref:
        example_markers.add(gloss_ref)

    return {
        'entry_map': entry_map,
        'entry_markers': entry_markers,
        'entry_columns': entry_columns,
        'entry_sources': entry_sources,
        'entry_sep': entry_sep,
        'entry_id': entry_id,

        'sense_map': sense_map,
        'sense_markers': sense_markers,
        'sense_columns': sense_columns,
        'sense_sep': sense_sep,
        'sense_sources': sense_sources,

        'example_map': example_map,
        'example_markers': example_markers,
        'example_columns': example_columns,
        'example_id': example_id,
        'example_sources': example_sources,
        'gloss_ref': gloss_ref}


def group_by_separator(sep, sfm_pairs):
    """Separate an iterator of tags and their values into groups.

    All groups are separated by the tag specified by `sep`.
    """
    entry = []
    for tag, value in sfm_pairs:
        if entry and tag == sep:
            yield entry
            entry = []
        entry.append((tag, value))
    if entry:
        yield entry


def split_by_pred(pred, iterable, constructor=list):
    """Sort elements of `iterable` into two lists based on predicate `pred`.

    Returns a tuple (l1, l2), where
     * l1: list of elements in `iterable` for which pred(elem) == True
     * l2: list of elements in `iterable` for which pred(elem) == False
    """
    pred_true = constructor()
    pred_false = constructor()
    for item in iterable:
        if pred(item):
            pred_true.append(item)
        else:
            pred_false.append(item)
    return pred_true, pred_false


class IDGenerator(object):

    def __init__(self, prefix=''):
        self.prefix = prefix
        self._last_id = 0

    def next_id(self):
        self._last_id += 1
        return '{}{:06d}'.format(self.prefix, self._last_id)


def prepare_examples(example_id, example_markers, database):
    id_gen = IDGenerator('XV')
    example_index = OrderedDict()

    for old_example in database:
        new_example = sfm.Entry(
            (marker, content)
            for marker, content in old_example
            if marker in example_markers)
        new_example.id = id_gen.next_id()
        new_example.sense_ids = []
        new_example.media_ids = []
        example_index[old_example.id] = new_example

    return example_index


def _preprocess_flex_link(link):
    """Turn FLEx's cross references into the 'lemma hm' format."""
    m = re.fullmatch(r'(.*?)(\d*)\s*(\d*)', link)
    if not m:
        return link
    lemma, hm, sense_nr = m.groups()
    if hm:
        return '{} {}'.format(lemma, hm)
    return lemma


def preprocess_flex_crossrefs(flex_refs, entry):
    r"""Pre-process FLEx's cross references.

    This turns

        \lf marker_name
        \lv content
        \le ...

    into

        \marker_name content
    """
    lf = None
    new_entry = entry.__class__()
    for marker, content in entry:
        if marker not in {'lf', 'lv', 'le'}:
            new_entry.append((marker, content))
        elif marker == 'lv' and lf in flex_refs:
            new_entry.append((flex_refs[lf], _preprocess_flex_link(content)))
        elif marker == 'lf':
            lf = content
    return new_entry


class EntryExtractor(object):
    def __init__(self, entry_id, entry_markers):
        self.entry_id = entry_id
        self.entry_markers = entry_markers
        self._idgen = IDGenerator('LX')
        self._idset = set()

        self.entries = sfm.SFM()

    def __call__(self, entry):
        new_entry, rest = split_by_pred(
            lambda pair: pair[0] in self.entry_markers,
            entry,
            constructor=sfm.Entry)
        if not new_entry:
            return False

        original_id = entry.get(self.entry_id, '')
        entry_id = re.sub(r'\s+', '_', original_id.strip())
        if entry_id and self.entry_id == 'lx':
            hm_nr = entry.get('hm')
            if hm_nr:
                entry_id = '{}_{}'.format(entry_id, hm_nr)

        if entry_id in self._idset or not re.fullmatch(r'[a-zA-Z0-9_\-]+', entry_id):
            entry_id = self._idgen.next_id()
        self._idset.add(entry_id)

        # XXX Adding attributes to existing types feels very fragile...
        new_entry.id = entry_id
        new_entry.original_id = original_id
        new_entry.media_ids = []
        self.entries.append(new_entry)

        rest.entry_id = new_entry.id
        rest.original_entry_id = original_id
        return rest


class GlossToExMapping:

    def __init__(self, gloss_ref_marker):
        self.gloss_ref_marker = gloss_ref_marker
        self._gloss_to_example_id = defaultdict(dict)

    def add_example(self, example):
        gloss_ref = example.get(self.gloss_ref_marker, '')
        match = re.fullmatch(r'(.*) (\d+)', gloss_ref.strip())
        text_id = match.group(1) if match else gloss_ref
        segnum = match.group(2) if match else '1'
        if not text_id:
            return
        self._gloss_to_example_id[text_id][segnum] = example.id

    def add_examples(self, examples):
        for example in examples:
            self.add_example(example)

    def get_example_id(self, text_id, segnum, default=None):
        text = self._gloss_to_example_id.get(text_id)
        if text is None:
            return default
        example_id = text.get(segnum)
        if example_id is None:
            return default
        return example_id


def prepare_glosses(glosses_path, gloss_ref_marker, examples, log):
    glosses = {}
    mapping = GlossToExMapping(gloss_ref_marker)
    mapping.add_examples(examples)
    for gloss in flextext.parse_flextext(str(glosses_path), log):
        example_id = mapping.get_example_id(gloss['text_id'], gloss['segnum'])
        if example_id:
            glosses[example_id] = gloss
    return glosses


def check_for_missing_glosses(gloss_ref_marker, glosses, examples, log):
    """Log an error message when an example references an unknown gloss."""
    for example in examples:
        gloss_ref = example.get(gloss_ref_marker)
        if not gloss_ref:
            continue
        if example.id not in glosses:
            log.error(
                "Gloss '\\%s %s' not found (ex. %s)",
                gloss_ref_marker, gloss_ref, example.id)


def validate_ps(entry, log):
    """Visitor filtering out entries with invalid \ps markers.

    Enforces the following rules:
     1. There must be at least one non-empty \ps marker
     2. Multiple non-empty \ps markers must not contradict each other

    """
    ps = entry.getall('ps')
    if not ps:
        log.error('\lx %s: entry dropped due to missing \ps marker', entry.get('lx'))
        return False
    ps = [s for s in ps if s.strip()]
    if not ps:
        log.error('\lx %s: entry dropped due to empty \ps marker', entry.get('lx'))
        return False
    if len(set(ps)) > 1:
        log.error(
            '\lx %s: entry dropped due to conflicting \ps markers: %s',
            entry.get('lx'),
            ', '.join(map(repr, ps)))
        return False
    return None


def merge_pos(entry):
    """Merge all unique \ps markers of an entry into one."""
    ps = [s for s in entry.getall('ps') if s.strip()]
    if len(ps) < 2:
        return entry
    new_entry = entry.__class__()
    for marker, content in entry:
        if marker == 'ps':
            if ps:
                new_entry.append(('ps', ' ; '.join(sorted(set(ps)))))
                ps = None
        else:
            new_entry.append((marker, content))
    return new_entry


class SenseExtractor(object):

    def __init__(self, sense_sep, sense_markers, crossref_markers, log):
        self.sense_sep = sense_sep
        self.sense_markers = sense_markers
        self.log = log
        self.crossrefs = crossref_markers
        self._idgen = IDGenerator('SN')

        self.senses = sfm.SFM()

    def __call__(self, entry):
        extracted_markers, rest = split_by_pred(
            lambda pair: pair[0] in self.sense_markers,
            entry)

        groups = list(group_by_separator(self.sense_sep, extracted_markers))
        for group in groups:
            # Drop everything before the first \sn marker
            if len(groups) > 1 and group[0][0] != self.sense_sep:
                msg = ', '.join(sorted({
                    '\\%s' % m
                    for m, _ in group
                    if m not in self.crossrefs}))
                if msg:
                    self.log.warning(
                        r'\lx %s: sense markers before first \sn: %s',
                        entry.original_entry_id, msg)
                continue
            new_sense = sfm.Entry(group)
            new_sense.id = self._idgen.next_id()
            new_sense.entry_id = entry.entry_id
            new_sense.media_ids = []
            self.senses.append(new_sense)

        return rest


class ExampleReferencer(object):

    def __init__(self, example_index):
        self.example_index = example_index
        self.invalid_example_ids = set()

    def __call__(self, sense):
        # FIXME Hardcoded SFM marker: xref
        for example_ref in sense.getall('xref'):
            if example_ref in self.example_index:
                example = self.example_index[example_ref]
                example.sense_ids.append(sense.id)
            else:
                self.invalid_example_ids.add(example_ref)

        # Note: This is a no-op on the senses themselves
        return sense


class MediaExtractor(object):

    def __init__(self, tag, id_index, cdstar_items):
        self.tag = tag
        self.id_index = id_index
        self.cdstar_items = cdstar_items

        self.orphans = set()
        self.files = set()

    def __call__(self, entry):
        for values in entry.getall(self.tag):
            for value in re.split(r'\s*;\s*', values):
                if not value.strip():
                    continue

                filename = value
                fileid = value

                if value in self.cdstar_items:
                    filename = self.cdstar_items[value]['fname']
                elif value in self.id_index:
                    fileid = self.id_index[value]
                else:
                    self.orphans.add(value)

                self.files.add((filename, fileid))
                entry.media_ids.append(fileid)

        # Note: no-op on the actual entry
        return entry


def _lx_hm_pair(entry, space=True):
    lx = entry.get('lx')
    hm = entry.get('hm')
    if hm:
        return '{}{}{}'.format(lx, ' ' if space else '', hm)
    return lx


def _lc_hm_pair(entry, space=True):
    lc = entry.get('lc')
    hm = entry.get('hm')
    if hm:
        return '{}{}{}'.format(lc, ' ' if space else '', hm)
    return lc


def make_id_index(entries):
    id_index = {
        entry.original_id: entry.id
        for entry in entries}
    id_index.update(
        (_lx_hm_pair(entry, True), entry.id)
        for entry in entries
        if entry.get('lx', '').strip())
    id_index.update(
        (_lx_hm_pair(entry, False), entry.id)
        for entry in entries
        if entry.get('lx', '').strip())
    id_index.update(
        (_lc_hm_pair(entry, True), entry.id)
        for entry in entries
        if entry.get('lc', '').strip())
    id_index.update(
        (_lc_hm_pair(entry, False), entry.id)
        for entry in entries
        if entry.get('lc', '').strip())
    return id_index


class CrossRefs:

    def __init__(self, id_index, crossref_markers):
        self._index = id_index
        self.markers = crossref_markers

    def _process_tag(self, tag, value):
        if tag not in self.markers:
            return tag, value
        refs = split_ids(value)
        refs = [self._index.get(ref, ref) for ref in refs]
        return tag, ' ; '.join(refs)

    def __call__(self, entry):
        # Preserve both the type and any potential attributes of the entry
        new_entry = copy.copy(entry)
        new_entry.clear()
        new_entry.extend(self._process_tag(tag, value) for tag, value in entry)
        return new_entry


class LinkProcessor:

    def __init__(self, id_index, label_index, link_markers, link_regex):
        self._ids = id_index
        self._labels = label_index
        self.markers = link_markers
        self.regex = link_regex

    def _replace_link(self, match):
        ref = match.group().strip()
        if not ref or ref not in self._ids:
            return ref
        id_ = self._ids[ref]
        return '[{}]({})'.format(self._labels.get(id_, id_), id_)

    def _process_tag(self, tag, value):
        if tag in self.markers:
            return tag, re.sub(self.regex, self._replace_link, value)
        else:
            return tag, value

    def __call__(self, entry):
        # Preserve both the type and any potential attributes of the entry
        new_entry = copy.copy(entry)
        new_entry.clear()
        new_entry.extend(self._process_tag(tag, value) for tag, value in entry)
        return new_entry


def make_label_index(link_display_label, entries):
    return {
        entry.id: entry.get(link_display_label, entry.id)
        for entry in entries}


def make_link_processor(properties, id_index, entries):
    link_markers = (
        set(properties.get('process_links_in_markers', ()))
        | DEFAULT_PROCESS_LINKS_IN_MARKERS)
    label_marker = properties.get(
        'link_label_marker',
        DEFAULT_LINK_LABEL_MARKER)
    link_regex = properties.get('link_regex')

    if not link_markers:
        return None
    if link_regex is None:
        raise ValueError('Missing property: link_regex')

    link_labels = make_label_index(label_marker, entries)
    return LinkProcessor(id_index, link_labels, link_markers, link_regex)


def _single_spaces(s):
    s = s.strip().replace('\n', ' ')
    s = re.sub(' +', ' ', s)
    return s


def sfm_entry_to_cldf_row(
        table_name, mapping, source_refs, cross_ref_columns, entry, language_id=None):
    # XXX What if the same tag appears multiple times?
    #  * Option 1: Overwrite old value for tag
    #  * Option 2: Ignore new value if tag is already there
    #  * Option 3: Collect values into semicolon-separated list (happening now)
    row = defaultdict(list)
    sources = []
    for tag, value in entry:
        if tag in source_refs:
            sources.extend(
                '{}[{}]'.format(s.strip(), source_refs[tag])
                for s in value.split(';'))
        key = mapping.get(tag)
        if key and value:
            row[key].append(_single_spaces(value))
    row = {k: DEFAULT_SEPARATOR.join(v) for k, v in row.items()}
    if hasattr(entry, 'id'):
        row['ID'] = entry.id
    if hasattr(entry, 'entry_id'):
        row['Entry_ID'] = entry.entry_id
    if hasattr(entry, 'sense_ids'):
        row['Sense_IDs'] = entry.sense_ids
    if hasattr(entry, 'media_ids'):
        row['Media_IDs'] = entry.media_ids
    if language_id:
        row['Language_ID'] = language_id

    if sources:
        row['Source'] = sources

    # The `csvw` package expects lists as input for fields with separators
    if table_name == 'ExampleTable':
        if 'Gloss' in row:
            row['Gloss'] = row['Gloss'].split()
        if 'Analyzed_Word' in row:
            row['Analyzed_Word'] = row['Analyzed_Word'].split()
    for col in cross_ref_columns:
        if col in row:
            row[col] = [eid.strip() for eid in row[col].split(';') if eid.strip()]

    return row


def _add_columns(dataset, table_name, columns, sources, cross_refs, log):
    for column in sorted(columns):
        col = column
        if column in SEPARATORS or column in cross_refs:
            col = {
                'name': column,
                'datatype': 'string',
                'separator': SEPARATORS.get(column, DEFAULT_SEPARATOR)}
        try:
            dataset.add_columns(table_name, col)
        except ValueError as error:
            msg = str(error)
            # Ignore columns that are already there
            if not msg.startswith('Duplicate column name:'):
                log.error('%s: Could not add column: %s', table_name, msg)

        if column in cross_refs:
            dataset[table_name].add_foreign_key(column, 'entries.csv', 'ID')
        if column == 'Media_IDs':
            dataset[table_name].add_foreign_key(column, 'media.csv', 'ID')
        if column == 'Sense_IDs':
            dataset[table_name].add_foreign_key(column, 'senses.csv', 'ID')
    if sources:
        try:
            dataset.add_columns(
                table_name,
                'http://cldf.clld.org/v1.0/terms.rdf#source')
        except ValueError:
            # ValueError means the column is already there
            pass


def make_cldf_dataset(
        folder,
        entry_columns, sense_columns, example_columns,
        entry_sources, sense_sources, example_sources,
        entry_crossrefs, sense_crossrefs, example_crossrefs,
        log):
    dataset = pycldf.Dictionary.in_dir(folder)
    dataset.add_component('ExampleTable')
    dataset.add_table('media.csv', 'ID', 'Language_ID', 'Filename')

    _add_columns(dataset, 'EntryTable', entry_columns, entry_sources, entry_crossrefs, log)
    _add_columns(dataset, 'SenseTable', sense_columns, sense_sources, sense_crossrefs, log)
    if example_columns:
        _add_columns(
            dataset, 'ExampleTable', example_columns, example_sources, example_crossrefs, log)
        # Manually mark Translated_Text as required
        # Turns out, e.g. for Daakaka, that this shouldn't be required after all ...
        # ft = dataset['ExampleTable'].tableSchema.get_column('Translated_Text')
        # if ft:
        #     ft.required = True

    return dataset


def add_gloss_columns(dataset, glosses):
    gloss_columns = {
        column
        for gloss in glosses.values()
        for column in gloss['example']}
    for column in sorted(gloss_columns):
        try:
            dataset.add_columns(
                'ExampleTable',
                {'name': column, 'datatype': 'string', 'separator': r'\t'})
        except ValueError:
            # ValueError means the column is already there
            pass


def attach_column_titles(table, mapping, labels):
    label_map = {
        mapping[marker]: label
        for marker, label in labels.items()
        if marker in mapping}
    for col in table.tableSchema.columns:
        if str(col) in label_map:
            col.titles = label_map[str(col)]


def ensure_required_columns(dataset, table_name, rows, log):
    required_cols = [
        col.name
        for col in dataset[table_name].tableSchema.columns
        if col.required]
    for row in rows:
        missing_fields = [
            col
            for col in required_cols
            if not row.get(col)]
        if missing_fields:
            field_list = ','.join(missing_fields)
            row_repr = '\n'.join(
                '{}: {}'.format(k, repr(v))
                for k, v in sorted(row.items()))
            log.error(
                '%s: row dropped due to missing required fields (%s):\n%s\n',
                table_name, field_list, row_repr)
        else:
            yield row


def remove_senseless_entries(sense_rows, entry_rows, log):
    referenced_entries = {
        row['Entry_ID']
        for row in sense_rows
        if 'Entry_ID' in row}
    for entry in entry_rows:
        entry_id = entry.get('ID', '').strip()
        if entry_id in referenced_entries:
            yield entry
        else:
            log.error("%s: entry dropped since there aren't any senses referring to it", entry_id)


def merge_gloss_into_example(glosses, example_row):
    if example_row['ID'] in glosses:
        return ChainMap(glosses[example_row['ID']]['example'], example_row)
    return example_row


class LogOnlyBaseNames(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        msg = re.sub(
            r'^.*?\.csv(?=:)',
            lambda m: os.path.basename(m.group()),
            msg)
        return msg, kwargs


def make_log(name, stream=None):
    log = logging.getLogger(name)
    log.propagate = False
    log.setLevel(logging.INFO)

    formatter = logging.Formatter('%(levelname)s %(message)s')

    to_stdout = logging.StreamHandler(sys.stdout)
    to_stdout.setFormatter(formatter)
    log.addHandler(to_stdout)

    if stream is not None:
        to_stream = logging.StreamHandler(stream)
        to_stream.setFormatter(formatter)
        log.addHandler(to_stream)

    return log
