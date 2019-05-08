from collections import OrderedDict, ChainMap, defaultdict
from itertools import chain
import re
import logging
import copy
import os.path
import sys

from clldutils import sfm
import pycldf
import csvw

from pydictionaria import flextext

DEFAULT_ENTRY_SEP = r'\lx '
DEFAULT_ENTRY_ID = 'lx'
DEFAULT_SENSE_SEP = 'sn'
DEFAULT_EXAMPLE_ID = 'ref'

DEFAULT_ENTRY_MAP = {
    'lx': 'Headword',
    'ps': 'Part_Of_Speech',
    'al': 'Alternative_Form',
    'et': 'Etymology',
    'hm': 'Homonym',
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
    'zcom1': 'Concepticon_ID'}

DEFAULT_EXAMPLE_MAP = {
    'rf': 'Corpus_Reference',
    'tx': 'Primary_Text',
    'mb': 'Analyzed_Word',
    'gl': 'Gloss',
    'ft': 'Translated_Text'}

DEFAULT_REFERENCES = {}

DEFAULT_PROCESS_LINKS_IN_LABELS = ()
DEFAULT_LINK_DISPLAY_LABEL = 'lx'
LINKS_WITH_NO_LABEL = ['mn', 'cf', 'cont']

DEFAULT_SEPARATOR = ' ; '
SEPARATORS = {
    'Contains': DEFAULT_SEPARATOR,
    'Entry_IDs': DEFAULT_SEPARATOR,
    'Media_IDs': DEFAULT_SEPARATOR,
    'Sense_IDs': DEFAULT_SEPARATOR,
    'Main_Entry': DEFAULT_SEPARATOR}

def _local_mapping(json_mapping, default_mapping, marker_set, ref_mapping):
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

    refs = {
        marker: mapping[target]
        for marker, target in ref_mapping.items()
        if marker in marker_set and target in mapping}
    markers.update(refs)

    return mapping, markers, columns, refs


def make_spec(properties, marker_set):
    ref_mapping = ChainMap(properties.get('references', {}), DEFAULT_REFERENCES)

    entry_map, entry_markers, entry_columns, entry_refs = _local_mapping(
        properties.get('entry_map', {}),
        DEFAULT_ENTRY_MAP,
        marker_set,
        ref_mapping)
    # Note: entry_sep is a string like '\\TAG ' (required by clldutils)
    entry_sep = properties.get('entry_sep', DEFAULT_ENTRY_SEP).strip().lstrip('\\')
    entry_id = properties.get('entry_id', DEFAULT_ENTRY_ID)
    entry_markers.update((entry_sep, entry_id))
    entry_columns.add('Media_IDs')

    sense_map, sense_markers, sense_columns, sense_refs = _local_mapping(
        properties.get('sense_map', {}),
        DEFAULT_SENSE_MAP,
        marker_set,
        ref_mapping)
    sense_sep = properties.get('sense_sep', DEFAULT_SENSE_SEP)
    sense_markers.update((sense_sep, 'xref', 'pc'))
    sense_columns.add('Media_IDs')

    example_map, example_markers, example_columns, example_refs = _local_mapping(
        properties.get('example_map', {}),
        DEFAULT_EXAMPLE_MAP,
        marker_set,
        ref_mapping)
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
        'entry_refs': entry_refs,
        'entry_sep': entry_sep,
        'entry_id': entry_id,

        'sense_map': sense_map,
        'sense_markers': sense_markers,
        'sense_columns': sense_columns,
        'sense_sep': sense_sep,
        'sense_refs': sense_refs,

        'example_map': example_map,
        'example_markers': example_markers,
        'example_columns': example_columns,
        'example_id': example_id,
        'example_refs': example_refs,
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
    unexpected_markers = set()
    id_gen = IDGenerator('XV')
    example_index = OrderedDict()
    for markers in database:
        extracted_markers, rest = split_by_pred(
            lambda pair: pair[0] in example_markers,
            markers)
        unexpected_markers.update(tag for tag, _ in rest)

        new_example = sfm.Entry(extracted_markers)
        new_example.id = id_gen.next_id()
        new_example.sense_ids = []
        new_example.media_ids = []
        example_index[markers.id] = new_example

    return example_index, unexpected_markers


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


class PartOfSpeechFilter:
    """Filters out all entries with multiple conflicting \ps markers."""

    def __init__(self, log):
        self.log = log

    def __call__(self, entry):
        ps = entry.getall('ps')
        if not ps:
            self.log.error('\lx %s: \ps marker missing', entry.get('lx'))
            return False
        ps = [s for s in ps if s.strip()]
        if not ps:
            self.log.error('\lx %s: \ps marker empty', entry.get('lx'))
            return False
        if len(set(ps)) > 1:
            self.log.error(
                '\lx %s: conflicting \ps markers: %s',
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

    def __init__(self, sense_sep, sense_markers):
        self.sense_sep = sense_sep
        self.sense_markers = sense_markers
        self._idgen = IDGenerator('SN')

        self.senses = sfm.SFM()

    def __call__(self, entry):
        extracted_markers, rest = split_by_pred(
            lambda pair: pair[0] in self.sense_markers,
            entry)

        for group in group_by_separator(self.sense_sep, extracted_markers):
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


class LinkIndex(object):

    def __init__(self, process_links_in_labels, link_display_label, id_regex):
        self.link_display_label = link_display_label
        self.process_links_in_labels = process_links_in_labels
        self.id_regex = id_regex
        self._index = {}

    def add_entry(self, entry):
        v = '[{}]({})'.format(entry.get(self.link_display_label, ''), entry.id)
        self._index[entry.original_id] = v
        lx = entry.get('lx')
        if not lx:
            # Don't fill the index with empty strings or integers
            return
        if entry.get('hm'):
            lx += ' {0}'.format(entry.get('hm'))
        self._index[lx] = v

    def _process_tag(self, tag, value):
        if tag not in self.process_links_in_labels:
            return tag, value

        def replace_ref(match):
            match_str = match.group().strip()
            replacement = self._index.get(match_str)
            if replacement and (tag in LINKS_WITH_NO_LABEL):
                replacement = replacement.split('(')[1].split(')')[0]
            return replacement or match.group()

        value = re.sub(self.id_regex, replace_ref, value)

        return tag, value

    def process_entry(self, entry):
        # Preserve both the type and any potential attributes of the entry
        new_entry = copy.copy(entry)
        new_entry.clear()
        new_entry.extend(self._process_tag(tag, value) for tag, value in entry)
        return new_entry


def process_links(properties, entries, senses, examples):
    process_links_in_labels = set(properties.get(
        'process_links_in_labels',
        DEFAULT_PROCESS_LINKS_IN_LABELS))
    link_display_label = properties.get(
        'link_display_label',
        DEFAULT_LINK_DISPLAY_LABEL)
    id_regex = properties.get('entry_label_as_regex_for_link')

    if not process_links_in_labels:
        return
    if id_regex is None:
        raise ValueError('Missing property: entry_label_as_regex_for_link')

    link_index = LinkIndex(
        process_links_in_labels,
        link_display_label,
        id_regex)
    for entry in entries:
        link_index.add_entry(entry)

    entries.visit(link_index.process_entry)
    senses.visit(link_index.process_entry)
    examples.visit(link_index.process_entry)


def _single_spaces(s):
    s = s.strip().replace('\n', ' ')
    s = re.sub(' +', ' ', s)
    return s


def sfm_entry_to_cldf_row(table_name, mapping, refs, entry, language_id=None):
    # XXX What if the same tag appears multiple times?
    #  * Option 1: Overwrite old value for tag
    #  * Option 2: Ignore new value if tag is already there
    #  * Option 3: Collect values into semicolon-separated list (happening now)
    row = defaultdict(list)
    sources = []
    for tag, value in entry:
        if tag in refs:
            sources.extend(
                '{}[{}]'.format(s.strip(), refs[tag])
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

    # In the CLDF spec, the columns `Gloss` and `Analyzed_Word` are defined with
    # the property `separator="\t"`.  For these columns the `csvw` package
    # assumes that the value comes as a *list* not a string.
    # TODO Check the spec for other columns with separators
    if table_name == 'ExampleTable':
        if 'Gloss' in row:
            row['Gloss'] = row['Gloss'].split()
        if 'Analyzed_Word' in row:
            row['Analyzed_Word'] = row['Analyzed_Word'].split()
    elif table_name == 'EntryTable':
        for col in ['Main_Entry', 'Entry_IDs', 'Contains']:
            if col in row:
                row[col] = [eid.strip() for eid in row[col].split(';') if eid.strip()]
    return row


def _add_columns(dataset, table_name, columns, refs):
    for column in sorted(columns):
        if table_name == 'EntryTable' and column in ['Main_Entry', 'Entry_IDs', 'Contains']:
            dataset[table_name].tableSchema.foreignKeys.append(csvw.ForeignKey.fromdict(dict(
                columnReference=column,
                reference=dict(columnReference='ID', resource='entries.csv')
            )))
        if column == 'Media_IDs':
            dataset[table_name].tableSchema.foreignKeys.append(csvw.ForeignKey.fromdict(dict(
                columnReference=column,
                reference=dict(columnReference='ID', resource='media.csv')
            )))
        if column in SEPARATORS:
            column = {
                'name': column,
                'datatype': 'string',
                'separator': SEPARATORS[column]}
        try:
            dataset.add_columns(table_name, column)
        except ValueError:
            # ValueError means the column is already there
            pass

    if refs:
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
        entry_refs, sense_refs, example_refs):
    dataset = pycldf.Dictionary.in_dir(folder)
    dataset.add_component('ExampleTable')
    dataset.add_table('media.csv', 'ID', 'Language_ID', 'Filename')

    _add_columns(dataset, 'EntryTable', entry_columns, entry_refs)
    _add_columns(dataset, 'SenseTable', sense_columns, sense_refs)
    if example_columns:
        _add_columns(dataset, 'ExampleTable', example_columns, example_refs)
        # Manually mark Translated_Text as required
        ft = dataset['ExampleTable'].tableSchema.get_column('Translated_Text')
        if ft:
            ft.required = True

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
            log.error('no senses found for entry %s', entry_id)


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


def logger(name, stream=None):
    formatter = logging.Formatter('%(levelname)s %(message)s')
    to_stdout = logging.StreamHandler(sys.stdout)
    to_stdout.setFormatter(formatter)
    if stream is not None:
        to_stream = logging.StreamHandler(stream)
        to_stream.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(logging.INFO)
    logger.addHandler(to_stdout)
    logger.addHandler(to_stream)
    return logger
