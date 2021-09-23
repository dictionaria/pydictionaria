from collections import OrderedDict, ChainMap, defaultdict
import copy
from functools import partial
from itertools import chain
import logging
import os.path
import re
import sys

from clldutils import sfm

from pydictionaria import flextext
from pydictionaria.example import Corpus, Examples, concat_multilines
from pydictionaria.sfm_lib import (
    find_duplicate_examples,
    normalize,
    Files,
    Rearrange,
    ExampleExtractor,
    EXAMPLE_MARKER_MAP,
)
from pydictionaria.util import split_ids
import rfc3986


DEFAULT_ENTRY_SEP = r'\lx '
DEFAULT_ENTRY_ID = 'lx'
DEFAULT_SENSE_SEP = 'sn'
DEFAULT_EXAMPLE_ID = 'ref'

DEFAULT_MARKER_MAP = {
    'd_Eng': 'de',
    'g_Eng': 'ge',
    'ps_Eng': 'ps',
    'sc_Eng': 'sc',
    'sd_Eng': 'sd',
    'x_Eng': 'xe'}

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
    'zcom1': 'Comparison_Meaning'}

DEFAULT_EXAMPLE_MAP = {
    'rf': 'Corpus_Reference',
    'tx': 'Primary_Text',
    'mb': 'Analyzed_Word',
    'gl': 'Gloss',
    'ot': 'alt_translation1',
    'ota': 'alt_translation2',
    'ft': 'Translated_Text'}

DEFAULT_LABELS = {
    'va': 'Variant Form(s)'}

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


PROPERTY_URLS = {
    'Source': 'http://cldf.clld.org/v1.0/terms.rdf#source',
    'Description': 'http://cldf.clld.org/v1.0/terms.rdf#description',
    'Comment': 'http://cldf.clld.org/v1.0/terms.rdf#comment',
    'Concepticon_ID': 'http://cldf.clld.org/v1.0/terms.rdf#concepticonReference'}


def load_examples(examples_path):
    """Load examples from a separate SFM file."""
    if not examples_path.exists():
        return None
    examples = Examples()
    examples.read(examples_path, marker_map={'sf': 'sfx'})
    examples.visit(concat_multilines)
    return examples


def _add_default_mapping(mapping, defaults):
    values = set(mapping.values())
    return ChainMap(
        mapping,
        {k: v for k, v in defaults.items() if v not in values})


def _add_property_fallbacks(props):
    new_properties = copy.copy(props)

    new_properties['entry_map'] = _add_default_mapping(
        props.get('entry_map') or {},
        DEFAULT_ENTRY_MAP)
    new_properties['sense_map'] = _add_default_mapping(
        props.get('sense_map') or {},
        DEFAULT_SENSE_MAP)
    new_properties['example_map'] = _add_default_mapping(
        props.get('example_map') or {},
        DEFAULT_EXAMPLE_MAP)

    new_properties['entry_sep'] = props.get('entry_sep') or DEFAULT_ENTRY_SEP
    new_properties['entry_id'] = props.get('entry_id') or DEFAULT_ENTRY_ID
    new_properties['sense_sep'] = props.get('sense_sep') or DEFAULT_SENSE_SEP
    new_properties['example_id'] = (
        props.get('example_id') or DEFAULT_EXAMPLE_ID)

    new_properties['sources'] = ChainMap(
        props.get('sources', {}),
        DEFAULT_SOURCES)

    new_properties['flexref_map'] = ChainMap(
        props.get('flexref_map', {}),
        DEFAULT_FLEXREF_MAP)

    new_properties['link_label_marker'] = (
        props.get('link_label_marker') or DEFAULT_LINK_LABEL_MARKER)
    new_properties['process_links_in_markers'] = (
        set(props.get('process_links_in_markers') or ())
        | DEFAULT_PROCESS_LINKS_IN_MARKERS)

    new_properties['labels'] = ChainMap(
        props.get('labels') or {},
        DEFAULT_LABELS)

    return new_properties


def _local_mapping(mapping, marker_set, source_mapping):
    markers = set(mapping.keys()) & marker_set
    mapping = {
        marker: value
        for marker, value in mapping.items()
        if marker in markers}

    sources = {
        marker: mapping[target]
        for marker, target in source_mapping.items()
        if marker in marker_set and target in mapping}
    markers.update(sources)

    return markers, sources


def make_spec(properties, marker_set):
    properties = _add_property_fallbacks(properties)

    source_mapping = properties['sources']

    entry_markers, entry_sources = _local_mapping(
        properties['entry_map'],
        marker_set,
        source_mapping)
    # Note: entry_sep is a string like '\\TAG ' (required by clldutils)
    entry_sep = properties['entry_sep'].strip().lstrip('\\')
    entry_id = properties['entry_id']
    link_label_marker = properties['link_label_marker']
    entry_markers.update((
        link_label_marker, entry_sep, entry_id, 'hm', 'sf', 'lc'))

    sense_markers, sense_sources = _local_mapping(
        properties['sense_map'],
        marker_set,
        source_mapping)
    sense_sep = properties['sense_sep']
    sense_markers.update((sense_sep, 'xref', 'pc'))

    example_markers, example_sources = _local_mapping(
        properties['example_map'],
        marker_set,
        source_mapping)
    example_id = properties['example_id']
    example_markers.update((example_id, 'sfx'))
    if 'gloss_ref' in properties:
        example_markers.add(properties['gloss_ref'])

    return {
        'entry_markers': entry_markers,
        'sense_markers': sense_markers,
        'example_markers': example_markers,
    }


def _get_crossref_markers(properties):
    return set(chain(
        DEFAULT_CROSS_REFERENCES,
        properties.get('cross_references') or (),
        DEFAULT_FLEXREF_MAP.values(),
        (properties.get('flexref_map') or {}).values()))


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
    """Generator for sequential.

    This generates IDs by incrementing an integer number and adding a prefix
    to it, e.g. LX000001, LX000002, etc.
    """

    def __init__(self, prefix=''):
        """Create generator for generates sequential IDs with an added `prefix`."""
        self.prefix = prefix
        self._last_id = 0

    def next_id(self):
        """Return next ID in the sequence."""
        self._last_id += 1
        return '{}{:06d}'.format(self.prefix, self._last_id)


def prepare_examples(example_id, example_markers, database):
    """Add IDs to examples.

    :returns: a dictionary, which maps the original example IDs to the adapted
    examples.
    """
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

    This turns::

        \lf marker_name
        \lv content
        \le ...

    into::

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
    """Visitor for extracting Entry information from an SFM entry."""

    def __init__(self, entry_id, entry_markers):
        """Create an entry extractor.

        :arg entry_id: marker, which contains the entry's original ID
        :arg entry_markers: collection of markers, which make up an entry (as
            opposed to a sense or an example)
        """
        self.entry_id = entry_id
        self.entry_markers = entry_markers
        self._idgen = IDGenerator('LX')
        self._idset = set()

        self.entries = sfm.SFM()

    def __call__(self, entry):
        """Extract entry markers from `entry`.

        :returns: a modified version `entry` without any entry markers.
        """
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
        match = re.match(r'(.*) (\d+)', gloss_ref.strip())
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
    """Map glosses from flextext file to examples.

    :returns: a dictionary, which maps example ids to glosses.
    """
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
    r"""Visitor filtering out entries with invalid \ps markers.

    Enforces the following rules:
     1. There must be at least one non-empty \ps marker
     2. Multiple non-empty \ps markers must not contradict each other

    """
    ps = entry.getall('ps')
    if not ps:
        log.error(r'\lx %s: entry dropped due to missing \ps marker', entry.get('lx'))
        return False
    ps = [s for s in ps if s.strip()]
    if not ps:
        log.error(r'\lx %s: entry dropped due to empty \ps marker', entry.get('lx'))
        return False
    if len(set(ps)) > 1:
        log.error(
            r'\lx %s: entry dropped due to conflicting \ps markers: %s',
            entry.get('lx'),
            ', '.join(map(repr, ps)))
        return False
    return None


def merge_pos(entry):
    r"""Merge all unique \ps markers of an entry into one."""
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
    """Visitor for extracting Sense information from an SFM entry."""

    def __init__(self, sense_sep, sense_markers, crossref_markers, log):
        """Create an entry extractor.

        :arg sense_sep: marker, which separates senses from each other.
        :arg sense_markers: collection of markers, which make up a sense.
        :arg crossref_markers: collection of markers, which refer to other
            entries
        """
        self.sense_sep = sense_sep
        self.sense_markers = sense_markers
        self.log = log
        self.crossrefs = crossref_markers
        self._idgen = IDGenerator('SN')

        self.senses = sfm.SFM()

    def __call__(self, entry):
        """Extract sense markers from `entry`.

        :returns: a modified version `entry` without any sense markers.
        """
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
    """Visitor, which links examples to the senses they illustrate."""

    def __init__(self, example_index):
        """Create an example referencer.

        :arg example_index: dictionary, which maps the original example IDs to
           to the examples themselves.
        """
        self.example_index = example_index
        self.invalid_example_ids = set()

    def __call__(self, sense):
        """Add references to `sense` to the examples.

        :returns: the `sense` (unchanged)
        """
        # FIXME Hardcoded SFM marker: xref
        for example_ref in sense.getall('xref'):
            if example_ref in self.example_index:
                example = self.example_index[example_ref]
                example.sense_ids.append(sense.id)
            else:
                self.invalid_example_ids.add(example_ref)

        # Note: This is a no-op on the senses themselves
        return sense


def _bigrams(iterable):
    i = iter(iterable)
    try:
        prev = next(i)
    except StopIteration:
        return
    for elem in i:
        yield prev, elem
        prev = elem


class CaptionFinder:
    """Visitor, which links captions to media files.

    It looks for SFM markers containing file names and checks if the adjacent
    marker contains a caption.
    """

    def __init__(self, media_markers, caption_marker):
        """Create a caption finder.

        :args media_markers: markers, which contain media file names.
        :args caption_marker: marker, which contains the caption.
        """
        self.media_markers = media_markers
        self.caption_marker = caption_marker
        self.captions = {}

    def __call__(self, entry):
        """Extract captions for media files.

        :returns: `entry` (unchanged)
        """
        for pair1, pair2 in _bigrams(entry):
            marker1, content1 = pair1
            marker2, content2 = pair2
            if marker1 in self.media_markers and marker2 == self.caption_marker:
                for file_id in re.split(r'\s*;\s*', content1):
                    self.captions[file_id] = content2

        # no-op on the actual entry
        return entry


class MediaExtractor(object):
    """Visitor, which turns media file names into CDSTAR IDs."""

    def __init__(self, tag, id_index, cdstar_items):
        """Create media extractor.

        :arg tag: marker, which contains the media file name.
        :arg id_index: dictionary ``filename`` -> ``checksum``
        :arg cdstar_items: dictionary ``checksum`` -> ``media item``
        """
        self.tag = tag
        self.id_index = id_index
        self.cdstar_items = cdstar_items

        self.orphans = set()
        self.files = set()

    def __call__(self, entry):
        """Add CDSTAR IDs to `entry.media_ids`.

        :returns: `entry`

        .. warning:: `entry` is mutated in-place.
        """
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
    r"""Map original IDs for entries to new IDs.

    This includes variants wuch as '<\lx> <\hm>' or '<\lx><\hm>'
    """
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
    """Visitor, which points cross references to new entry IDs."""

    def __init__(self, id_index, crossref_markers):
        """Create crossref processor.

        :arg id_index: dictionary ``old entry id`` -> ``new entry id``
        :arg crossref_markers: collection of markers, which contain cross
            references.
        """
        self._index = id_index
        self.markers = crossref_markers

    def _process_tag(self, tag, value):
        if tag not in self.markers:
            return tag, value
        refs = split_ids(value)
        refs = [self._index.get(ref, ref) for ref in refs]
        return tag, ' ; '.join(refs)

    def __call__(self, entry):
        """Swap references to old IDs out for references to new IDs.

        :returns: a copy of `entry` with fixed cross references.
        """
        # Preserve both the type and any potential attributes of the entry
        new_entry = copy.copy(entry)
        new_entry.clear()
        new_entry.extend(self._process_tag(tag, value) for tag, value in entry)
        return new_entry


class LinkProcessor:
    """Visitor, which points *in-line references* to new entry IDs.

    This creates markdown-style links (like ``[human-readable label](ID)``).
    """

    def __init__(self, id_index, label_index, link_markers, link_regex):
        """Create link processor.

        :arg id_index: dictionary ``old entry id`` -> ``new entry id``
        :arg label_index: dictionary ``new entry id`` -> ``human-readable label``
        :arg link_regex: regular expression for finding in-line cross
            references.
        """
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
        """Swap in-line links for markdown-style links.

        :returns: a modified copy of `entry`
        """
        # Preserve both the type and any potential attributes of the entry
        new_entry = copy.copy(entry)
        new_entry.clear()
        new_entry.extend(self._process_tag(tag, value) for tag, value in entry)
        return new_entry


def make_label_index(link_display_label, entries):
    """Map entry IDs to human-readable labels.

    :arg link_display_label: Marker, which contains the label.
    :arg entries: Collection of entries.
    """
    return {
        entry.id: entry.get(link_display_label, entry.id)
        for entry in entries}


def make_link_processor(properties, id_index, entries):
    """Factory function for `LinkProcessor`'s."""
    link_markers = properties['process_links_in_markers']
    link_regex = properties.get('link_regex')

    if not link_markers:
        return None
    if link_regex is None:
        raise ValueError('Missing property: link_regex')

    link_labels = make_label_index(properties['link_label_marker'], entries)
    return LinkProcessor(id_index, link_labels, link_markers, link_regex)


def _single_spaces(s):
    s = s.strip().replace('\n', ' ')
    s = re.sub(' +', ' ', s)
    return s


def sfm_entry_to_cldf_row(
    table_name, mapping, source_refs, cross_ref_columns, entry, language_id=None
):
    """Convert SFM entry into a CLDF row.

    :arg table_name: Name of the CLDF table/component.
    :arg mapping: dictionary ``SFM marker`` -> ``CLDF column name``
    :arg source_refs: markers, which contain a row's ``Source``
    :arg cross_ref_columns: CLDF column names, which denote cross references.
    :arg entry: SFM entry
    :arg language_id: value for the ``Language_ID`` column

    :returns: dictionary ``CLDF column name`` -> ``value``
    """
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

    if row.get('Source') and isinstance(row.get('Source'), str):
        row['Source'] = [src.strip() for src in row['Source'].split(';') if src.strip()]

    return row


def _amend_columns(cldf, table_name, entry_cols, crossrefs):
    for colname in entry_cols:
        if colname in PROPERTY_URLS:
            col = PROPERTY_URLS[colname]
        elif table_name == 'ExampleTable' and colname.startswith('Gloss'):
            col = {
                'name': colname,
                'datatype': 'string',
                'separator': '\t',
            }
        elif table_name == 'Media_IDs':
            col = {
                'name': 'Media_IDs',
                'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#mediaReference',
                'separator': DEFAULT_SEPARATOR,
            }
        elif colname in SEPARATORS or colname in crossrefs:
            col = {
                'name': colname,
                'datatype': 'string',
                'separator': SEPARATORS.get(colname, DEFAULT_SEPARATOR),
            }
        else:
            col = colname

        try:
            cldf.add_columns(table_name, col)
        except ValueError as error:
            msg = str(error)
            # Ignore columns that are already there
            if not msg.startswith('Duplicate column name:'):
                print('{}:'.format(table_name), 'Could not add column:', msg)

        if colname in crossrefs:
            cldf.add_foreign_key(table_name, colname, 'EntryTable', 'ID')
        elif colname == 'Media_IDs':
            cldf.add_foreign_key(table_name, colname, 'MediaTable', 'ID')
        elif colname == 'Sense_IDs':
            cldf.add_foreign_key(table_name, colname, 'SenseTable', 'ID')


def make_cldf_schema(cldf, properties, entries, senses, examples, media):
    """Add Dictionaria's tables and columns to a CLDF dataset.

    :arg cldf: CLDF dataset
    :arg properties: ``md.json`` properties
    :arg entries: collection of CLDF rows for the entries
    :arg senses: collection of CLDF rows for the senses
    :arg examples: collection of CLDF rows for the examples
    :arg media: collection of CLDF rows for media files
    """
    properties = _add_property_fallbacks(properties)

    if not cldf.get('ExampleTable'):
        cldf.add_component('ExampleTable')
    if not cldf.get('MediaTable'):
        cldf.add_component(
            'MediaTable',
            'http://cldf.clld.org/v1.0/terms.rdf#languageReference',
            {'name': 'size', 'datatype': 'integer'})
    if not cldf.get('LanguageTable'):
        cldf.add_component('LanguageTable')

    crossref_markers = _get_crossref_markers(properties)

    _amend_columns(
        cldf,
        'EntryTable',
        sorted({col for row in entries for col, val in row.items() if val}),
        {c for m, c in properties['entry_map'].items() if m in crossref_markers})
    _amend_columns(
        cldf,
        'SenseTable',
        sorted({col for row in senses for col, val in row.items() if val}),
        {c for m, c in properties['sense_map'].items() if m in crossref_markers})
    _amend_columns(
        cldf,
        'ExampleTable',
        sorted({col for row in examples for col, val in row.items() if val}),
        {c for m, c in properties['example_map'].items() if m in crossref_markers})
    _amend_columns(
        cldf,
        'MediaTable',
        sorted({col for row in media for col, val in row.items() if val}),
        ())


def add_gloss_columns(cldf, glosses):
    """Add columns for glosses to the ``ExampleTable``.

    :arg cldf: CLDF dataset
    :arg glosses: dictionary `example id` -> `gloss`
    """
    gloss_columns = {
        column
        for gloss in glosses.values()
        for column in gloss['example']}
    for column in sorted(gloss_columns):
        try:
            cldf.add_columns(
                'ExampleTable',
                {'name': column, 'datatype': 'string', 'separator': r'\t'})
        except ValueError:
            # ValueError means the column is already there
            pass


def _add_labels_to_table(table, mapping, labels):
    label_map = {
        mapping[marker]: label
        for marker, label in labels.items()
        if marker in mapping}
    for col in table.tableSchema.columns:
        if str(col) in label_map:
            col.titles = label_map[str(col)]


def attach_column_titles(cldf, properties):
    """Add custom column titles to CLDF dataset."""
    properties = _add_property_fallbacks(properties)

    labels = properties['labels']
    _add_labels_to_table(cldf['EntryTable'], properties['entry_map'], labels)
    _add_labels_to_table(cldf['SenseTable'], properties['sense_map'], labels)
    _add_labels_to_table(cldf['ExampleTable'], properties['example_map'], labels)


def _ensure_required_columns(cldf, table_name, rows, log):
    required_cols = [
        col.name
        for col in cldf[table_name].tableSchema.columns
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


def ensure_required_columns(cldf, table_name, rows, log):
    """Drop all rows that lack required column values.

    :arg cldf: CLDF dataset
    :arg table_name: CLDF table name
    :arg rows: collection of CLDF rows
    :arg log: log for error messages

    :returns: list of wellformed rows.
    """
    return list(_ensure_required_columns(cldf, table_name, rows, log))


def _remove_senseless_entries(sense_rows, entry_rows, log):
    referenced_entries = {
        row['Entry_ID']
        for row in sense_rows
        if 'Entry_ID' in row}
    for entry in entry_rows:
        if entry.get('ID', '').strip() in referenced_entries:
            yield entry
        else:
            log.error(
                "\\lx %s: entry dropped since there aren't any senses referring to it",
                entry['Headword'])


def remove_senseless_entries(sense_rows, entry_rows, log):
    """Drop entries that do not have any senses.

    :arg sense_rows: collection of senses
    :arg entry_rows: collection of entries
    :arg log: log for error messages

    :returns: list of wellformed entries.
    """
    return list(_remove_senseless_entries(sense_rows, entry_rows, log))


def merge_gloss_into_example(glosses, example_row):
    """Add IGT to an example.

    :arg glosses: dictionary `example id` -> `gloss`
    :arg example_row: CLDF example.
    """
    if example_row['ID'] in glosses:
        return ChainMap(glosses[example_row['ID']]['example'], example_row)
    return example_row


def _author_is_primary(a):
    return not isinstance(a, dict) or a.get('primary', True)


def format_authors(authors):
    """Return human-readable string of `authors`.

    Takes the form ``Primary Author and Primary Author with Secondary Author``.
    """
    primary = ' and '.join(
        a['name'] if isinstance(a, dict) else a
        for a in authors
        if _author_is_primary(a))
    secondary = ' and '.join(
        a['name']
        for a in authors
        if not _author_is_primary(a))
    if primary and secondary:
        return '{} with {}'.format(primary, secondary)
    else:
        return primary or secondary


def extract_concepticon_id(sense_row):
    if sense_row.get('Concepticon_ID'):
        return sense_row

    comp_meaning = sense_row.get('Comparison_Meaning') or ''
    match = re.fullmatch(r'\w+ \[(\d+)\]', comp_meaning)
    if match:
        return ChainMap(sense_row, {'Concepticon_ID': match.group(1)})
    else:
        return sense_row


def add_media_metadata(media_catalog, media_row):
    """Add metadata to media file.

    :arg media_catalog: CDstar catalog.
    :arg media_row: Media item.
    """
    if media_row.get('ID') in media_catalog:
        metadata = {
            'Download_URL': rfc3986.uri.URIReference.from_string(
                'https://cdstar.eva.mpg.de/bitstreams/{0[objid]}/{0[original]}'.format(
                    media_catalog[media_row['ID']])),
            'Media_Type': media_catalog[media_row['ID']]['mimetype'],
            'size': media_catalog[media_row['ID']]['size'],
        }
        return ChainMap(media_row, metadata)
    else:
        return media_row


class LogOnlyBaseNames(logging.LoggerAdapter):

    def process(self, msg, kwargs):
        """Reduce path names for CLDF tables to basename for more
        machine-independent error messages."""
        msg = re.sub(
            r'^.*?\.csv(?=:)',
            lambda m: os.path.basename(m.group()),
            msg)
        return msg, kwargs


def make_log(name, stream=None):
    """Factory function for an error log."""
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


def _source_mapping(sources, column_map):
    return {
        m: column_map[t]
        for m, t in sources.items()
        if t in column_map}


def process_dataset(
    sid, language_id, properties,
    sfm, examples, media_catalog,
    glosses_path, examples_log_path, glosses_log_path,
    cldf_log
):
    """Turn an SFM database into CLDF data.

    :arg sid: submission id
    :arg language_id: ID of the dictionary language
    :arg properties: properties from the ``md.json`` metadata file
    :arg sfm: SFM database (see `pydictionaria.sfm_lib.Database`)
    :arg examples: SFM examples (see `pydictionaria.sfm_lib.Database`)
    :arg media_catalog: CDSTAR media catalog.
    :arg glosses_path: Path to ``flextext`` glosses.
    :arg examples_log_path: Path where errors regarding example extraction are
      logged.
    :arg glosses_log_path: Path where error regarding gloss extraction are
      logged.
    :arg cldf_log: Logger object

    :returns: a tuple containing:
      * a list of EntryTable rows
      * a list of SenseTable rows
      * a list of ExampleTable rows
      * a list of MediaTable rows
    """
    properties = _add_property_fallbacks(properties)

    # Run generic normalization of sFM:
    sfm.visit(normalize)
    sfm.visit(Rearrange())

    # Replace media references with md5 sums of referenced files:
    media_sids = properties.get('media_lookup') or sid
    if not isinstance(media_sids, list):
        media_sids = [media_sids]
    files = Files(media_catalog, media_sids)
    sfm.visit(files)

    caption_marker = properties.get('media_caption_marker')
    caption_finder = CaptionFinder(
        ['pc', 'sf', 'sfx'], caption_marker)
    if caption_marker:
        sfm.visit(caption_finder)

    # Process FLEx's cross-references in \lf markers
    flexref_map = properties['flexref_map']
    sfm.visit(partial(preprocess_flex_crossrefs, flexref_map))

    if not examples:
        with open(examples_log_path, 'w', encoding='utf8') as example_log:
            # FIXME This should go into make_spec
            example_markers = set(properties['example_map'])
            example_markers.add('sfx')
            if 'gloss_ref' in properties:
                example_markers.add(properties['gloss_ref'])
            # FIXME I don't think `Corpus` is used anywhere to begin with...
            extractor = ExampleExtractor(
                example_markers, Corpus.from_dir(examples_log_path.parent), example_log)
            sfm.visit(extractor)
            examples = Examples(extractor.examples.values())
            for dups in find_duplicate_examples('tx', examples):
                print('# potential duplicate w.r.t. \\xe', file=example_log)
                print('\n# and\n'.join(map(str, dups)), file=example_log)
                print(file=example_log)
            for dups in find_duplicate_examples('ft', examples):
                print('# potential duplicate w.r.t. \\xv', file=example_log)
                print('\n# and\n'.join(map(str, dups)), file=example_log)
                print(file=example_log)

    original_amount = len(examples)
    cited = {
        xref
        for example in sfm
        for xref in example.getall('xref')}
    examples = Examples(
        example
        for example in examples
        if example.id in cited)
    if original_amount - len(examples):
        print('pruning', original_amount - len(examples), 'examples from', original_amount)

    all_markers = {
        marker
        for entry in chain(sfm, examples)
        for marker, _ in entry}
    spec = make_spec(properties, all_markers)

    all_markers -= spec['entry_markers']
    all_markers -= spec['sense_markers']
    all_markers -= spec['example_markers']
    all_markers -= set(EXAMPLE_MARKER_MAP.values())
    all_markers -= {'lf', 'lv', 'le', caption_marker}
    if all_markers:
        marker_list = ', '.join(sorted(all_markers))
        cldf_log.warning('No CLDF column defined for markers: %s', marker_list)

    example_index = prepare_examples(
        properties['example_id'],
        spec['example_markers'],
        examples)
    examples = Examples(example_index.values())

    glosses = {}
    if glosses_path.exists():
        gloss_logname = '%s.glosses' % sid
        with open(glosses_log_path, 'w', encoding='utf-8') as gloss_logfile:
            gloss_log = make_log(gloss_logname, gloss_logfile)
            gloss_ref_marker = properties.get('gloss_ref')
            if gloss_ref_marker:
                glosses = prepare_glosses(
                    glosses_path, gloss_ref_marker, examples, gloss_log)
            else:
                gloss_log.error("no 'gloss_ref' marker specified")
            check_for_missing_glosses(
                gloss_ref_marker, glosses, examples, gloss_log)

    sfm.visit(lambda e: validate_ps(e, cldf_log))
    sfm.visit(merge_pos)

    crossref_markers = _get_crossref_markers(properties)

    entry_extr = EntryExtractor(
        properties['entry_id'],
        spec['entry_markers'])
    sense_extr = SenseExtractor(
        properties['sense_sep'],
        spec['sense_markers'],
        crossref_markers,
        cldf_log)

    rest = [entry_extr(entry) for entry in sfm]
    rest = [sense_extr(entry) for entry in rest if entry]

    entries = entry_extr.entries
    senses = sense_extr.senses

    ex_ref = ExampleReferencer(example_index)
    senses.visit(ex_ref)

    if ex_ref.invalid_example_ids:
        example_list = ', '.join(
            sorted(map(repr, ex_ref.invalid_example_ids)))
        cldf_log.warning('senses refer to non-existent examples: %s', example_list)

    media_sids = properties.get('media_lookup') or sid
    if not isinstance(media_sids, list):
        media_sids = [media_sids]

    media_id_index = {
        entry['fname']: checksum
        for checksum, entry in media_catalog.items()
        if entry['sid'] in media_sids}
    for fname in list(media_id_index.keys()):
        media_id_index[fname.split('.')[0]] = media_id_index[fname]
    media_extr = MediaExtractor(
        'sf',
        media_id_index,
        media_catalog)

    entries.visit(media_extr)
    media_extr.tag = 'pc'
    senses.visit(media_extr)
    media_extr.tag = 'sfx'
    examples.visit(media_extr)

    if media_extr.orphans:
        file_list = ', '.join(sorted(map(repr, media_extr.orphans)))
        cldf_log.warning('unknown media files: %s', file_list)

    id_index = make_id_index(entries)

    crossref_processor = CrossRefs(id_index, crossref_markers)
    entries.visit(crossref_processor)
    senses.visit(crossref_processor)
    examples.visit(crossref_processor)

    try:
        link_processor = make_link_processor(
            properties, id_index, entries)
        if link_processor is not None:
            entries.visit(link_processor)
            senses.visit(link_processor)
            examples.visit(link_processor)
    except ValueError as e:
        cldf_log.warning('could not process links: %s', str(e))

    # XXX can I get rid of these lines?
    entry_crossref_cols = {c for m, c in properties['entry_map'].items() if m in crossref_markers}
    sense_crossref_cols = {c for m, c in properties['sense_map'].items() if m in crossref_markers}
    example_crossref_cols = {
        c for m, c in properties['example_map'].items() if m in crossref_markers}

    entry_rows = [
        sfm_entry_to_cldf_row(
            'EntryTable',
            properties['entry_map'],
            _source_mapping(properties['sources'], properties['entry_map']),
            entry_crossref_cols,
            entry,
            language_id)
        for entry in entries]
    sense_rows = [
        sfm_entry_to_cldf_row(
            'SenseTable',
            properties['sense_map'],
            _source_mapping(properties['sources'], properties['sense_map']),
            sense_crossref_cols,
            sense)
        for sense in senses]
    example_rows = [
        sfm_entry_to_cldf_row(
            'ExampleTable',
            properties['example_map'],
            _source_mapping(properties['sources'], properties['example_map']),
            example_crossref_cols,
            example,
            language_id)
        for example in examples]
    media_rows = [
        {
            'ID': fileid,
            'Language_ID': language_id,
            'Name': filename,
            'Description': caption_finder.captions.get(fileid)
        }
        for filename, fileid in sorted(media_extr.files)]

    sense_rows = list(map(extract_concepticon_id, sense_rows))
    media_rows = [add_media_metadata(media_catalog, row) for row in media_rows]

    if glosses:
        example_rows = [
            merge_gloss_into_example(glosses, row)
            for row in example_rows]

    return entry_rows, sense_rows, example_rows, media_rows
