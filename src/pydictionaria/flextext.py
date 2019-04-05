from clldutils.misc import log_or_raise


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


def separate_examples(document):
    for text in document:
        title = get_item(text, 'title')
        vernacular, other_langs = get_languages(text)
        paragraphs = text.find('paragraphs') or ()
        if not paragraphs:
            log_or_raise("No paragraphs in interlinear text '{}'".format(text.attrib.get('guid', '???')))
        for paragraph in text.find('paragraphs') or ():
            phrases = paragraph.find('phrases') or ()
            if not phrases:
                log_or_raise("No phrases in paragraph '{}'".format(paragraph.attrib.get('guid', '???')))
            for phrase in phrases:
                segnum = get_item(phrase, 'segnum')
                yield {
                    'title': title,
                    'segnum': segnum,
                    'vernacular': vernacular,
                    'other_langs': other_langs,
                    'phrase': phrase}
