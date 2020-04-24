import re

import xlrd

from csvw.dsv import UnicodeWriter
from clldutils.misc import lazyproperty
from clldutils.markup import Table
from clldutils.path import md5, path_component

from pydictionaria.formats import base
from pydictionaria.example import Example, Examples

"""
lemmas.csv - entries.csv
------------------------
Lemma - headword
PoS - part-of-speech

senses.csv
----------
belongs to lemma - entry ID
example ID - <missing>

examples.csv
------------
<missing> - sense ID
vernacular - example
morphemes - <missing>
gloss - <missing>
<missing> - source

questions
---------
- should we allow alternatives to relate examples and senses?
"""


class Dictionary(base.Dictionary):
    required_sheets = {'entries', 'senses', 'examples'}

    def __init__(self, submission):
        base.Dictionary.__init__(self, submission)
        files = list(submission.dir.glob('*.xlsx'))
        assert len(files) == 1
        self.xlsx = files[0]
        self._example_map = {}

    def _path_to_md5(self, maintype, fname):
        if fname:
            fname = self.submission.dir.joinpath(maintype, path_component(fname))
            if fname.exists():
                return md5(fname)
        return ''

    def process_row(self, row, header):
        res = []
        for col, cell in zip(header, row):
            if col == 'picture':
                cell = self._path_to_md5('image', cell)
            elif col == 'sound':
                cell = self._path_to_md5('audio', cell)
            res.append(cell)
        return res

    @classmethod
    def match(cls, submission):
        return bool(list(submission.dir.glob('*.xlsx')))

    def stat(self):
        table = Table('Type', 'Count')
        for sheet in self.sheets.values():
            table.append([sheet.name, len(sheet.rows)])
        print(table.render(tablefmt='simple', condensed=False))

    def check(self):
        return

    def _process(self, outdir):
        examples = Examples(list(self.iter_examples()))
        examples.write(outdir.joinpath('examples.sfm'))

        for sheet in self.sheets.values():
            if sheet.name != 'examples':
                sheet.write_csv(outdir, self._example_map, self.process_row)

    @lazyproperty
    def sheets(self):
        workbook = xlrd.open_workbook(self.xlsx.as_posix())
        _sheets = {s.name: s for s in [Sheet(sheet) for sheet in workbook.sheets()]}
        assert self.required_sheets.issubset(set(_sheets.keys()))
        return _sheets

    def iter_examples(self):
        for d in self.sheets['examples'].iter_dicts():
            if 'sense ID' in d:
                self._example_map[d['sense ID']] = d['ID']
            if 'example' not in d:
                d['example'] = d['vernacular']
            ex = Example()
            ex.set('id', d['ID'])
            ex.set('text', d['example'])
            ex.set('morphemes', d.get('morphemes'))
            ex.set('gloss', d.get('gloss'))
            ex.set('translation', d['translation'])
            yield ex


class Sheet(object):
    def __init__(self, sheet):
        self.name = sheet.name.lower()
        self._sheet = sheet
        self.header = []
        self.rows = []
        for i in range(sheet.nrows):
            row = [cell.value for cell in sheet.row(i)]
            if i == 0:
                self.header = self.normalized_header(row, self.name)
            else:
                if self.header[0] == 'ID' and set(row[1:]) == {''}:
                    continue
                self.rows.append(self.normalized_row(row, self.name))
        ids = [r[0] for r in self.rows]
        assert len(ids) == len(set(ids))

    def normalized_header(self, row, name):
        for i, col in enumerate(row[:]):
            row[i] = re.sub(
                r'(?P<c>[^\s])ID$', lambda m: m.group('c') + ' ID', col.strip())

        if 'ID' not in row:
            assert 'ID' in row[0]
            row[0] = 'ID'

        nrow = [''.join(r.lower().split()) for r in row]

        def repl(old, new):
            try:
                row[nrow.index(old)] = new
            except ValueError:
                pass

        if name == 'entries':
            repl('pos', 'part-of-speech')
            repl('lemma', 'headword')

        if name == 'senses':
            repl('meaningdescription', 'description')
            repl('belongstolemma', 'entry ID')

        return row

    def normalized_row(self, row, name):
        for i, head in enumerate(self.header):
            if 'ID' in head:
                val = row[i]
                if isinstance(val, (int, float)):
                    row[i] = '%s' % int(val)
        return row

    def iter_dicts(self):
        for row in self.rows:
            yield dict(zip(self.header, row))

    def write_csv(self, outdir, example_map=None, row_processor=None):
        with UnicodeWriter(outdir.joinpath('%s.csv' % self.name)) as writer:
            if example_map:
                assert 'example ID' not in self.header
                self.header.append('example ID')
                for row in self.rows:
                    row.append(example_map.get(row[self.header.index('ID')], ''))

            writer.writerow(self.header)
            for row in self.rows:
                if row_processor:
                    row = row_processor(row, self.header)
                writer.writerow(row)
