def get_item(node, key, default=None):
    for item in node.iter('item'):
        if item.attrib.get('type') == key:
            return item.text
    return default


def get_languages(node):
    languages = node.find('languages')
    if not languages:
        raise ValueError('Missing <languages> tag')

    vernacular = None
    other = []
    for lang in languages:
        if not vernacular and lang.attrib.get('vernacular') == 'true':
            vernacular = lang.attrib.get('lang')
        elif 'lang' in lang.attrib:
            other.append(lang.attrib['lang'])

    other.sort()
    return vernacular, other


def separate_examples(document, log=None):
    if not document.find('interlinear-text'):
        if log:
            log.warn('XML data does not contain any interlinear texts.')
        return

    for text in document.iter('interlinear-text'):
        title = get_item(text, 'title')
        vernacular, other_langs = get_languages(text)
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

            for phrase in phrases.iter('phrase'):
                segnum = get_item(phrase, 'segnum')
                yield {
                    'title': title,
                    'segnum': segnum,
                    'vernacular': vernacular,
                    'other_langs': other_langs,
                    'phrase': phrase}
