from collections import defaultdict, OrderedDict

from clldutils.misc import lazyproperty
from csvw.dsv import reader, UnicodeWriter
from clldutils.markup import Table

from pydictionaria.formats import base
from pydictionaria.example import Example, Examples

FORMAT_MAP = {
    'entries': (
        'entries.csv',
        {
            'entry_ID': 'ID',
            'PoS': 'part-of-speech',
        }),
    'senses': (
        'senses.csv',
        {
            'sense_ID': 'ID',
            'sense': 'description',
            'entry_ID': 'entry ID',
        }),
}


class Dictionary(base.Dictionary):  # pragma: no cover
    def __init__(self, submission):
        base.Dictionary.__init__(self, submission)
        self._enc = self.submission.md.properties.get('encoding', 'utf8')
        self._lsep = self.submission.md.properties.get('linesep', '\n').encode(self._enc)

    @classmethod
    def match(cls, submission):
        return submission.dir.joinpath('FIELDS.txt').exists()

    @lazyproperty
    def headers(self):
        return [(fname, cols) for fname, cols in self._iter_headers() if fname]

    def stat(self):
        table = Table('Type', 'Count')
        for fname, cols in self.headers:
            table.append([fname.stem, len(list(self._iter_items(fname, cols)))])
        print(table.render(tablefmt='simple', condensed=False))

    def check(self):
        pass

    def _process(self, outdir):
        examples = Examples(list(self.iter_examples()))
        examples.write(outdir.joinpath('examples.sfm'))
        #
        # TODO:
        # - inline assoc table data
        # - include associations.csv as col "associated lemma" in entries.csv!
        #
        name2path = {fname.stem: fname for fname, _ in self.headers}
        associations = defaultdict(list)
        for s, t in self._iter_items(name2path['associations']):
            associations[s].append(t)

        examples = defaultdict(list)
        for s, t in self._iter_items(name2path['senses_examples']):
            examples[s].append(t)

        for fname, header in self.headers:
            if fname.stem in FORMAT_MAP:
                name, col_map = FORMAT_MAP[fname.stem]
                header = [col_map.get(col, col) for col in header]
                with UnicodeWriter(outdir.joinpath(name)) as fp:
                    if name == 'entries.csv':
                        header.append('associated lemma')
                    elif name == 'senses.csv':
                        header.append('example ID')
                    assert header[0] == 'ID'
                    fp.writerow(header)
                    for row in self._iter_items(fname):
                        if name == 'entries.csv':
                            row.append(' ; '.join(associations.get(row[0], [])))
                        elif name == 'senses.csv':
                            row.append(' ; '.join(examples.get(row[0], [])))
                        fp.writerow(row)

    # -------------------------------------------------------------------
    def iter_examples(self):
        for row in self._iter_items(self.submission.dir.joinpath('examples.csv')):
            id_, text, translation, sense = row
            ex = Example()
            ex.set('id', id_)
            ex.set('text', text)
            ex.set('translation', translation)
            yield ex

    def _iter_headers(self):
        def path(name):
            if name:
                _path = self.submission.dir.joinpath(name + '.csv')
                if _path.exists():
                    return _path

        fname, cols = None, []
        for line in self.submission.dir.joinpath('FIELDS.txt').open(encoding=self._enc):
            line = line.strip()
            if line.endswith(':'):
                yield path(fname), cols
                fname, cols = line[:-1], []
            elif line:
                assert fname
                cols.append(line)
        yield path(fname), cols

    def _iter_items(self, name, cols=None):
        lines = []
        for line in name.open('rb').read().split(self._lsep):
            lines.append(line.replace(b'\x00', b''))
        for row in reader(lines, encoding=self._enc):
            if row:
                yield OrderedDict(list(zip(cols, row))) if cols else row
