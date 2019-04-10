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
    # TODO Handle punctuation
    analyzed_word = []
    glosses = []
    gloss_pos = []
    lemmas = []

    for morph in _find_morphemes(phrase):
        analyzed_word.append(get_item(morph, 'txt', ''))
        glosses.append(get_item(morph, 'gls', ''))
        gloss_pos.append(get_item(morph, 'msa', ''))

        lemma = get_item(morph, 'cf', '')
        homonym = get_item(morph, 'hn')
        if lemma and homonym:
            lemma = '%s %s' % (lemma, homonym)
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
