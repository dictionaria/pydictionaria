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


def extract_gloss(phrase):
    # TODO Handle invalid data
    analyzed_word = []
    for word in phrase.find('words').iter('word'):
        for morph in word.find('morphemes').iter('morph'):
            analyzed_word.append(get_item(morph, 'txt', ''))
    return {
        'Analyzed_Word': analyzed_word}
