from pycldf import Dictionary as CldfDictionary
from clldutils.path import md5, path_component, copy

from pydictionaria.formats import base


class Dictionary(base.Dictionary):
    def __init__(self, submission):
        base.Dictionary.__init__(self, submission)
        cldf_md = submission.dir.joinpath('cldf-md.json')
        if not cldf_md.exists():
            cldf_md.write_text(DEFAULT_METADATA, encoding='utf-8')
        self.cldf = CldfDictionary.from_metadata(cldf_md)

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
        return bool(list(submission.dir.glob('cldf-md.json'))) or \
            bool(list(submission.dir.glob('entries.csv')))

    def check(self):
        self.cldf.validate()

    def _process(self, outdir):
        copy(self.submission.dir / 'cldf-md.json', outdir / 'cldf-md.json')
        for table in self.cldf.tables:
            copy(self.submission.dir / table.local_name, outdir / table.local_name)


DEFAULT_METADATA = """\
{
    "@context": [
        "http://www.w3.org/ns/csvw",
        {
            "@language": "en"
        }
    ],
    "dc:format": "http://cldf.clld.org/v1.0/terms.rdf#v1.0",
    "dc:conformsTo": "http://cldf.clld.org/v1.0/terms.rdf#Dictionary",
    "dialect": {
        "doubleQuote": false,
        "commentPrefix": null,
        "trim": true
    },
    "tables": [
        {
            "url": "entries.csv",
            "dc:conformsTo": "http://cldf.clld.org/v1.0/terms.rdf#EntryTable",
            "tableSchema": {
                "columns": [
                    {
                        "name": "ID",
                        "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#id",
                        "datatype": {"base": "string"},
                        "required": true
                    },
                    {
                        "name": "headword",
                        "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#headword",
                        "datatype": "string",
                        "required": true
                    },
                    {
                        "name": "part_of_speech",
                        "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#partOfSpeech",
                        "datatype": "string"
                    }
                ]
            }
        },
        {
            "url": "senses.csv",
            "dc:conformsTo": "http://cldf.clld.org/v1.0/terms.rdf#SenseTable",
            "tableSchema": {
                "columns": [
                    {
                        "name": "ID",
                        "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#id",
                        "datatype": {"base": "string"},
                        "required": true
                    },
                    {
                        "name": "description",
                        "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#description",
                        "datatype": "string",
                        "separator": ";"
                    },
                    {
                        "name": "entry_ID",
                        "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#entryReference",
                        "datatype": "string"
                    }
                ],
               "foreignKeys": [
                   {
                        "columnReference": "entry_ID",
                        "reference": {
                            "resource": "entries.csv",
                            "columnReference": "ID"
                        }
                    }
               ]
            }
        },
        {
            "url": "examples.csv",
            "dc:conformsTo": "http://cldf.clld.org/v1.0/terms.rdf#ExampleTable",
            "tableSchema": {
                "columns": [
                    {
                        "name": "ID",
                        "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#id",
                        "datatype": {"base": "string"},
                        "required": true
                    },
                    {
                        "name": "primary_text",
                        "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#primaryText",
                        "datatype": "string",
                        "required": true
                    },
                    {
                        "name": "translation",
                        "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#translatedText",
                        "datatype": "string"
                    },
                    {
                        "name": "sense_ID",
                        "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#senseReference",
                        "datatype": "string",
                        "separator": ";"
                    }
                ],
                "foreignKeys": [
                    {
                        "columnReference": "sense_ID",
                        "reference": {
                            "resource": "senses.csv",
                            "columnReference": "ID"
                        }
                    }
                ]
            }
        }
    ]
}
"""
