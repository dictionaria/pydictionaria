# coding: utf8
from __future__ import unicode_literals, print_function, division
from collections import Counter, defaultdict, OrderedDict
import re
import copy

from transliterate import translit
from clldutils.sfm import FIELD_SPLITTER_PATTERN, SFM
from clldutils.sfm import Entry as BaseEntry
from clldutils.path import md5, as_unicode, Path
from clldutils.misc import slug
from clldutils.text import split_text

from pydictionaria.util import split_ids
from pydictionaria.example import Example
from pydictionaria.log import warn, error


def split(s):
    return split_text(s, separators=FIELD_SPLITTER_PATTERN, strip=True)


def join(l):
    return ' ; '.join(l)


class Entry(BaseEntry):
    @property
    def id(self):
        return '{0} {1}'.format(self.get('lx') or '', self.get('hm') or '').strip()

    def upsert(self, marker, content, index=-1):
        for i, (k, _) in enumerate(self):
            if k == marker:
                break
        else:
            i = None
        if i is not None:
            self[i] = (marker, content)
        else:
            self.insert(index, (marker, content))


class Database(SFM):
    def __init__(self, fname, **kw):
        SFM.__init__(self)
        kw.setdefault('entry_sep', '\\lx ')
        self.read(fname, entry_impl=Entry, **kw)

    def visit(self, visitor):
        remove = []
        for i, entry in enumerate(self):
            res = visitor(entry)
            if res is False:
                remove.append(i)
            else:
                self[i] = visitor(entry) or entry
        for i in reversed(remove):
            del self[i]


class Stats(object):
    """
    SFM visitor collecting statistics
    """
    def __init__(self):
        self.count = Counter()
        self.total = Counter()
        self._mult_markers = defaultdict(int)
        self._implicit_mult_markers = set()

    def __call__(self, entry):
        if not entry.get('lx'):
            return
        entry_markers = entry.markers()
        self.total.update(entry_markers)
        for k, v in entry_markers.items():
            self.count.update([k])
            if v > self._mult_markers[k]:
                self._mult_markers[k] = v
        for k, v in entry:
            if FIELD_SPLITTER_PATTERN.search(v):
                self._implicit_mult_markers.add(k)


class ComparisonMeanings(object):
    def __init__(self, concepticon, marker='zcom2'):
        self.concepticon = concepticon
        self.marker = marker
        self.dot_pattern = re.compile(r'(?P<pre>[a-zA-Z])\.(?P<post>[a-zA-Z])')

    def __call__(self, entry):
        comps = set()
        for marker in ['de', 're']:
            for content in entry.getall(marker):
                for comp in split(content):
                    comps.add(comp.lower())
        if not comps:
            for content in entry.getall('ge'):
                for comp in split(content):
                    if self.dot_pattern.search(comp):
                        comp = comp.replace('.', ' ').strip()
                    if comp:
                        comps.add(comp.lower())
        if comps:
            comps = list(comps)
            matches = set()
            for matchset in self.concepticon.lookup(comps, similarity_level=9):
                for m in matchset:
                    matches.add(m[1])
            if matches:
                try:
                    matches = [
                        '{0.gloss} [{0.id}] "{0.definition}"'.format(
                            self.concepticon.conceptsets[m]) for m in sorted(matches)]
                    entry.append((self.marker, ' ; '.join(matches)))
                except KeyError:
                    print(matches)
        return entry


def normalize(entry):
    """
    SFM visitor, normalizing marker values.
    """
    new = Entry()
    for marker, content in entry:
        if marker in ['sd', 'ps']:
            content = re.sub(r'\s+', ' ', content.replace('_', ' ')).strip()
        new.append((marker, content))
    return new


def repair(sfm):
    entry_map = defaultdict(dict)

    for entry in sfm:
        lx = entry.get('lx')
        if lx in entry_map:
            if entry.get('hm') in entry_map[lx]:
                # a collision!
                hm = '{0}'.format(max(int(x or 0) for x in entry_map[lx]) + 1)
                entry.upsert('hm', hm, 1)
        entry_map[lx][entry.get('hm')] = entry


class CheckBibrefs(object):
    def __init__(self, refs):
        self.refs = refs

    def __call__(self, entry):
        for ref in entry.getall('bibref'):
            if ref.split('[')[0] not in self.refs:
                error(entry, 'invalid bibkey', 'bibref', ref)


class Check(object):
    def __init__(self, sfm):
        self.lexemes = set()
        for entry in sfm:
            try:
                if entry.id in self.lexemes:
                    error(entry, 'duplicate lemma')
            except:
                print(entry.__class__)
                print(entry)
            self.lexemes.add(entry.id)

    def __call__(self, entry):
        if not entry.get('de'):
            error(entry, 'no \\de field')
        if len(entry.getall('de')) > 1 and len(entry.getall('de')) != len(entry.getall('sn')):
            error(entry, 'multiple \\de but not matching \\sn')
        if len(entry.getall('ps')) > 1:
            if len(set(entry.getall('ps'))) > 1:
                error(entry, 'multiple different \\ps')
            else:
                error(entry, 'multiple \\ps')
        for marker, content in entry:
            if marker in ['cf', 'mn', 'an', 'sy']:
                for lx in split_ids(content):
                    if lx not in self.lexemes:
                        warn(entry, 'invalid ref', marker, lx)
            elif marker in ['se']:
                error(entry, 'illegal marker', marker)


class Files(object):
    """
    SFM visitor, checking/editing media references
    """
    def __init__(self, submission, mode='edit'):
        self.mode = mode
        self.file_sep = re.compile(',|;')
        self.missing_files = set()
        self.files = defaultdict(dict)
        self.marker_to_mtypes = {
            'pc': ['image'],
            'sf': ['audio'],
            'sfx': ['image', 'audio'],
        }
        for mtype, files in submission.media.items():
            for p in files:
                self.files[mtype][as_unicode(p.name)] = p
                # and just in case, add transliterated variants of file names:
                try:
                    nname = translit(as_unicode(p.name), b'ru', reversed=True)
                    if nname not in self.files[mtype]:
                        self.files[mtype][nname] = p
                except:
                    continue
                self.files[mtype][as_unicode(p.stem) + p.suffix.lower()] = p
                self.files[mtype][as_unicode(p.stem) + p.suffix.upper()] = p
                self.files[mtype][as_unicode(p.stem)] = p
        #
        # FIXME: must also take files from cdstar.json into account! use
        # - submission id
        # - mimetype
        # - path name
        # as lookup!
        #
        for checksum, spec in submission.cdstar.items.items():
            if spec['sid'] in submission.media_sids:
                self.files[spec['type']][spec['fname']] = checksum
                self.files[spec['type']][as_unicode(Path(spec['fname']).stem)] = checksum

    def __call__(self, entry):
        e = Entry()
        for marker, content in entry:
            mtypes = self.marker_to_mtypes.get(marker)
            if mtypes:
                normalized = []
                for fname in split_ids(content, self.file_sep):
                    fname = re.split(r'/|\\', fname)[-1]
                    for mtype in mtypes:
                        p = self.files[mtype].get(fname)
                        if p:
                            normalized.append(md5(p) if isinstance(p, Path) else p)
                            break
                    else:
                        self.missing_files.add((entry.id, marker, fname))
                content = ' ; '.join(normalized)
            e.append((marker, content))
        if self.mode == 'edit':
            return e


def move_marker(entry, m, before):
    reorder_map = []
    last_m = 0

    for index, (marker, content) in enumerate(entry):
        if marker == m:
            # search for the preceding 'before' marker, but make sure we do not go
            # back before the last 'm' marker.
            for i in range(index - 1, last_m, -1):
                if entry[i][0] == before:
                    reorder_map.append((i, content, index))
                    break
            else:
                entry[index] = (m, content)
            last_m = index

    for insert, content, delete in reorder_map:
        del entry[delete]
        entry.insert(insert, (m, content))


class Rearrange(object):
    """
    SFM visitor rearranging the order of markers within an entry.
    """
    #
    # Teop preprocess: \rf comes *after* the example, when the value is in square
    # brackets! So when \rf [xxx] is encountered immediately after \xe, it must be moved
    # before the corresponding \xv!
    #
    in_brackets = re.compile(r'\[+\s*(?P<text>[^\]]+)\s*\]+$')

    def __call__(self, entry):
        reorder_map = []
        last_rf = 0

        for index, (marker, content) in enumerate(entry):
            if marker == 'rf':
                content = content.strip()
                match = self.in_brackets.match(content)
                if match:
                    if entry[index - 1][0] == 'xe':
                        # search for the preceding xv marker, but make sure we do not go
                        # back before the last rf marker.
                        for i in range(index - 2, last_rf, -1):
                            if entry[i][0] == 'xv':
                                reorder_map.append((i, match.group('text'), index))
                                break
                    else:
                        entry[index] = ('rf', match.group('text'))
                last_rf = index

        for insert, content, delete in reorder_map:
            del entry[delete]
            entry.insert(insert, ('rf', content))

        move_marker(entry, 'xsf', 'xe')
        move_marker(entry, 'xo', 'xe')
        move_marker(entry, 'xr', 'xe')


class ExampleExtractor(object):
    """
    SFM visitor to extract examples
    """
    def __init__(self, corpus, log):
        """
        :param corpus: A pydictionaria.example.Corpus instance to lookup morphems and \
        glosses in an ELAN corpus.
        :param log:
        """
        self.example_props = {
            'rf': 'rf',
            'xv': 'tx',
            'xvm': 'mb',
            'xeg': 'gl',
            'xo': 'ot',
            'xn': 'ot',
            'xr': 'ota',
            'xe': 'ft',
            'sfx': 'sf',
        }
        self.examples = OrderedDict()
        self.corpus = corpus
        self.log = log

    def __call__(self, entry):
        example = None
        lx = entry.get('lx')
        rf = None
        xvm = None
        xeg = None
        new_entry = entry.__class__()

        for marker, content in entry:
            if marker not in self.example_props:
                new_entry.append((marker, content))
                continue

            if marker == 'rf':
                rf = content
            elif marker == 'xvm':
                xvm = '%s %s' % (xvm, content) if xvm else content
            elif marker == 'xeg':
                xeg = '%s %s' % (xeg, content) if xeg else content

            elif marker == 'xv':
                if xvm is None and xeg is None:
                    # new example starts
                    if example:
                        # but last one is unfinished
                        self.log.write(
                            '# incomplete example in lx: %s - missing xe:\n%s\n\n'
                            % (lx, example))
                    example = Example([('tx', content)])
                else:
                    example.set(
                        'tx',
                        '%s %s' % (example.get('tx', ''), content))
                assert example

            elif marker == 'xe':
                # example ends
                if example:
                    if rf:
                        example.insert(0, ('rf', rf))
                    if xvm:
                        example.set('mb', xvm)
                    if xeg:
                        example.set('gl', xeg)
                    example.append(('ft', content))
                    example.set('lemma', lx)
                    new_entry.append(('xref', self.xref(example)))
                    rf = None
                    xvm = None
                    xeg = None
                    example = None
                else:
                    self.log.write(
                        '# incomplete example in lx: %s - missing xv\n' % lx)

            else:
                if not example:
                    self.log.write('incomplete example in lx: %s - missing xv\n' % lx)
                else:
                    example.append((self.example_props[marker], content))

        return new_entry

    def merge(self, ex1, ex2):
        merged_ex = copy.copy(ex1)
        for prop in 'rf tx mb gl ft ot'.split():
            p1 = merged_ex.get(prop)
            p2 = ex2.get(prop)
            if p1:
                if p2:
                    try:
                        assert slug(p1) == slug(p2)
                    except AssertionError:
                        self.log.write(
                            '# cannot merge \\%s:\n%s\n# and\n%s\n\n' % (prop, ex1, ex2))
                        raise
            else:
                if p2:
                    merged_ex.set(prop, p2)
        merged_ex.set(
            'lemma',
            ' ; '.join(sorted(set(ex2.lemmas) - set(merged_ex.lemmas))))
        return merged_ex

    def xref(self, example):
        if example.corpus_ref:
            from_corpus = self.corpus.get(example.corpus_ref)
            if from_corpus:
                try:
                    example = self.merge(example, from_corpus)
                except AssertionError:
                    pass

        orig = example.id
        count = 0
        while example.id in self.examples:
            try:
                example = self.merge(self.examples[example.id], example)
                break
            except AssertionError:
                count += 1
                example.set('ref', '%s---%s' % (orig, count))

        self.examples[example.id] = example
        return example.id

    def write_examples(self, fname):
        examples = SFM(self.examples.values())
        examples.write(fname)