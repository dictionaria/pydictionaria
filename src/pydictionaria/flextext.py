from collections import OrderedDict


def get_item(node, key, default=None):
    for item in node.iter('item'):
        if item.attrib.get('type') == key:
            return item.text
    return default


def get_languages(node):
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


def separate_examples(document, log=None):
    if not document.find('interlinear-text'):
        if log:
            log.warn('XML data does not contain any interlinear texts.')
        return

    for text in document.iter('interlinear-text'):
        title = get_item(text, 'title')
        if not title:
            if log:
                log.warn("Missing title in interlinear text '{}'".format(text.attrib.get('guid', '???')))
            continue

        languages, vernacular = get_languages(text)
        if not languages:
            if log:
                log.warn("Missing languages in interlinear text '{}'".format(text.attrib.get('guid', '???')))
            continue
        if not vernacular:
            if log:
                log.warn("Missing vernacular in interlinear text '{}'".format(text.attrib.get('guid', '???')))
            continue

        paragraphs = text.find('paragraphs')
        if not paragraphs:
            if log:
                log.warn("No paragraphs in interlinear text '{}'".format(text.attrib.get('guid', '???')))
            continue

        for paragraph in paragraphs.iter('paragraph'):
            phrases = paragraph.find('phrases')
            if not phrases:
                if log:
                    log.warn("No phrases in paragraph '{}'".format(paragraph.attrib.get('guid', '???')))
                continue

            examples = OrderedDict()
            for phrase in phrases.iter('phrase'):
                segnum = get_item(phrase, 'segnum')
                if not segnum:
                    if log:
                        log.warn("Missing segnum in phrase '{}'".format(phrase.attrib.get('guid', '???')))
                    continue

                prefix = segnum.split('.')[0] or segnum
                if prefix not in examples:
                    examples[prefix] = []
                examples[prefix].append(phrase)

            for segnum, phrases in examples.items():
                yield {
                    'title': title,
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


def extract_gloss(phrase):
    # TODO Handle invalid data
    analyzed_word = []
    glosses = []
    gloss_pos = []
    lemmas = []

    for morph in _find_morphemes(phrase):
        item_index = ItemIndex(morph.iter('item'))
        mb = item_index.get_text('txt')
        gl = item_index.get_text('gls')
        ps = item_index.get_text('msa')

        if not mb:
            puncts = item_index.get_items('punct')
            if puncts:
                mb = puncts[0].text
                ps = 'punct'

        lemma = item_index.get_text('cf')
        homonym = item_index.get_text('hn')
        if lemma and homonym:
            lemma = '%s %s' % (lemma, homonym)

        analyzed_word.append(mb)
        glosses.append(gl)
        gloss_pos.append(ps)
        lemmas.append(lemma)

    return {
        'Analyzed_Word': analyzed_word,
        'Gloss': glosses,
        'Gloss_POS': gloss_pos,
        'Lexical_Entries': lemmas}


def merge_glosses(glosses):
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
