# coding: utf8
from __future__ import unicode_literals, print_function, division
from collections import OrderedDict
from hashlib import md5

from clldutils.sfm import Entry, SFM
from clldutils.misc import slug, UnicodeMixin, lazyproperty


class Example(Entry, UnicodeMixin):
    markers = OrderedDict([
        ('ref', 'id'),
        ('lemma', None),
        ('rf', 'corpus_ref'),
        ('tx', 'text'),
        ('mb', 'morphemes'),
        ('gl', 'gloss'),
        ('ft', 'translation'),
        ('ot', 'alt_translation'),
        ('ota', 'alt_translation2'),
        ('sf', 'soundfile'),
    ])
    name_to_marker = {v: k for k, v in markers.items()}

    @staticmethod
    def normalize(morphemes_or_gloss):
        """
        Normalize aligned words by replacing whitespace with single tab, and removing
        ELAN comments.
        """
        if morphemes_or_gloss:
            return '\t'.join(
                [p for p in morphemes_or_gloss.split() if not p.startswith('#')])

    @property
    def id(self):
        res = self.get('ref')
        if not res:
            res = md5(slug((self.text or '') + (self.translation or '')).encode('utf'))\
                .hexdigest()
            self.insert(0, ('ref', res))
        return res

    def set(self, key, value):
        assert (key in self.markers) or (key in self.name_to_marker)
        key = self.name_to_marker.get(key, key)
        for i, (k, v) in enumerate(self):
            if k == key:
                if key == 'lemma':
                    if not value or not v:
                        continue
                    value = ' ; '.join([v, value])
                self[i] = (key, value)
                break
        else:
            self.append((key, value))

    @property
    def lemmas(self):
        return [l.strip() for l in (self.get('lemma') or '').split(';') if l.strip()]

    @property
    def corpus_ref(self):
        return self.get('rf')

    @property
    def text(self):
        return self.get('tx')

    @property
    def translation(self):
        return self.get('ft')

    @property
    def alt_translation(self):
        return self.get('ot')

    @property
    def alt_translation2(self):
        return self.get('ota')

    @property
    def soundfile(self):
        return self.get('sf')

    @property
    def morphemes(self):
        return self.normalize(self.get('mb'))

    @property
    def gloss(self):
        return self.normalize(self.get('gl'))

    def __unicode__(self):
        lines = []
        for key in self.markers:
            value = self.get(key) or ''
            if key in ['mb', 'gl']:
                value = self.normalize(value) or ''
            else:
                value = ' '.join(value.split())
            if value:
                value = ' %s' % value
            lines.append('%s%s' % (key, value))
        return '\n'.join('\\' + l for l in lines)


class Examples(SFM):
    def read(self, filename, **kw):
        return SFM.read(self, filename, entry_impl=Example, **kw)

    def concat_multilines(self):
        def _fix(entry):
            new = Example()
            for marker in new.markers:
                if marker in ['tx', 'mb', 'gl']:
                    new.append((marker, '\t'.join(entry.getall(marker))))
                else:
                    new.append((marker, entry.get(marker)))
            return new
        self.visit(_fix)

    @lazyproperty
    def _map(self):
        return {entry.get('ref'): entry for entry in self}

    def get(self, item):
        return self._map.get(item)


class Corpus(object):
    """
    ELAN corpus exported using the Toolbox exporter

    http://www.mpi.nl/corpus/html/elan/ch04s03s02.html#Sec_Exporting_a_document_to_Toolbox
    """
    def __init__(self, examples):
        self.examples = examples

    @classmethod
    def from_dir(cls, dir_):
        examples = Examples()
        marker_map = {
            'utterance_id': 'ref',
            'utterance': 'tx',
            'gramm_units': 'mb',
            'rp_gloss': 'gl',
        }
        for path in dir_.glob('*.eaf.sfm'):
            examples.read(path, marker_map=marker_map, entry_sep='\\utterance_id')
        return cls(examples)

    def get(self, key):
        res = self.examples.get(key)
        if not res:
            # We try to correct the lookup key. If a key like 'Abc.34' is used and not
            # found, we try 'Abc.034' as well.
            try:
                prefix, number = key.split('.', 1)
                res = self.examples.get('%s.%03d' % (prefix, int(number)))
            except ValueError:
                pass
        return res