from collections import OrderedDict
import xml.etree.ElementTree as ET


def get_item(node, key, default=None):
    for item in node.iter('item'):
        if item.attrib.get('type') == key:
            return item.text
    return default


def _extract_languages(node):
    languages = set()
    vernacular = None

    for language in node.iter('language'):
        lang_name = language.attrib.get('lang')
        if not lang_name:
            continue

        if not vernacular and language.attrib.get('vernacular') == 'true':
            vernacular = language.attrib.get('lang')

        languages.add(lang_name)

    return languages, vernacular


def _extract_text_id(node, vernacular):
    abbr_items = [
        item.text
        for item in node.iter('item')
        if item.text and item.attrib.get('type') == 'title-abbreviation']

    if abbr_items:
        return abbr_items[0]

    title_items = [
        (item.attrib.get('lang', ''), item.text)
        for item in node.iter('item')
        if item.text and item.attrib.get('type') == 'title']

    if not title_items:
        return None

    for lang, item_text in title_items:
        if lang == vernacular:
            return item_text

    return title_items[0][1]


def separate_examples(document, log=None):
    """Iterate over examples contained in flextext XML document."""
    if not document.find('interlinear-text'):
        if log:
            log.warn('XML data does not contain any interlinear texts.')
        return

    for text in document.iter('interlinear-text'):
        languages, vernacular = _extract_languages(text)
        if not languages:
            if log:
                log.warn("Missing languages in interlinear text '{}'".format(
                    text.attrib.get('guid', '???')))
            continue
        if not vernacular:
            if log:
                log.warn("Missing vernacular in interlinear text '{}'".format(
                    text.attrib.get('guid', '???')))
            continue

        text_id = _extract_text_id(text, vernacular)
        if not text_id:
            if log:
                log.warn("Missing title in interlinear text '{}'".format(
                    text.attrib.get('guid', '???')))
            continue

        paragraphs = text.find('paragraphs')
        if not paragraphs:
            if log:
                log.warn("No paragraphs in interlinear text '{}'".format(
                    text.attrib.get('guid', '???')))
            continue

        for paragraph in paragraphs.iter('paragraph'):
            phrases = paragraph.find('phrases')
            if not phrases:
                if log:
                    log.warn("No phrases in paragraph '{}'".format(
                        paragraph.attrib.get('guid', '???')))
                continue

            examples = OrderedDict()
            for phrase in phrases.iter('phrase'):
                segnum = get_item(phrase, 'segnum')
                if not segnum:
                    if log:
                        log.warn("Missing segnum in phrase '{}'".format(
                            phrase.attrib.get('guid', '???')))
                    continue

                prefix = segnum.split('.')[0] or segnum
                if prefix not in examples:
                    examples[prefix] = []
                examples[prefix].append(phrase)

            for segnum, phrases in examples.items():
                yield {
                    'text_id': text_id,
                    'segnum': segnum,
                    'languages': languages,
                    'vernacular': vernacular,
                    'example': phrases}


class ItemIndex:

    def __init__(self, items=None):
        self._index = {}
        if items:
            self.add_items(items)

    def add_item(self, item):
        item_type = item.attrib.get('type')
        if not item_type:
            return
        if item_type not in self._index:
            self._index[item_type] = []
        self._index[item_type].append(item)

    def add_items(self, items):
        for item in items:
            self.add_item(item)

    def get_items(self, item_type, default=()):
        """Return all items with the attribute type=item_type."""
        return self._index.get(item_type, default)

    def get_text(self, item_type, default=''):
        """Return text of the first item with the attribute type=item_type."""
        try:
            return self.get_items(item_type)[0].text
        except (KeyError, IndexError):
            return default


def _find_morphemes(phrase):
    for word in phrase.find('words').iter('word'):
        morphemes = word.find('morphemes')
        if morphemes:
            for morph in morphemes.iter('morph'):
                yield morph
        else:
            yield word


def _column_name(name, lang):
    lang_suffix = ''
    if lang != 'en':
        lang_suffix = '_{}{}'.format(lang[0].upper(), lang[1:])
    return '{}{}'.format(name, lang_suffix)


def _parse_morph(morph):
    gloss = {}

    item_index = ItemIndex(morph.iter('item'))

    mb = item_index.get_text('txt')
    puncts = item_index.get_items('punct')

    if puncts and not mb:
        mb = puncts[0].text
    if mb:
        gloss['Analyzed_Word'] = mb

    for gl_item in item_index.get_items('gls'):
        lang = gl_item.attrib.get('lang', 'en')
        gloss[_column_name('Gloss', lang)] = gl_item.text or ''

    for ps_item in item_index.get_items('msa'):
        lang = ps_item.attrib.get('lang', 'en')
        gloss[_column_name('Gloss_POS', lang)] = ps_item.text or ''

    return gloss


def extract_gloss(phrase, log=None):
    """Extract IGT from example."""
    if not phrase.find('words'):
        if log:
            log.warn("No words in phrase '{}'".format(phrase.attrib.get('guid', '???')))
        return {}

    morph_glosses = list(map(_parse_morph, _find_morphemes(phrase)))

    gloss = {k: [] for g in morph_glosses for k in g}
    for g in morph_glosses:
        for k in gloss:
            gloss[k].append(g.get(k, ''))

    # remove empty glosses
    gloss = {k: l for k, l in gloss.items() if any(l)}

    return gloss


def merge_glosses(glosses):
    """Merge sequence of `glosses` into a single gloss.

    Note: Since this loops over the `glosses` twice, they need to be
    a *sequence*, not an iterator.
    """
    all_keys = {
        key
        for gloss in glosses
        for key in gloss}

    combo = {key: [] for key in all_keys}
    for gloss in glosses:
        max_len = max(map(len, gloss.values()))
        for key in all_keys:
            combo[key].extend(gloss.get(key) or [''] * max_len)
    return combo


def parse_flextext(file_name, log=None):
    """Iterate over glossed examples contained in a flextext file."""
    gloss_db = ET.parse(file_name)
    for example in separate_examples(gloss_db.getroot(), log):
        example['example'] = merge_glosses(
            [extract_gloss(e, log) for e in example['example']])
        yield example
