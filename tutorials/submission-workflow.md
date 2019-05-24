How to Prepare a Submission
===========================


Workflow
--------

The editorial workflow to process dictionaries from submission to publication is
a series of automated or manual steps.  The automated steps are implemented as
sub-commands of the `dictionaria` command line interface.

### Initialising a new submission

Command:

    dictionaria new <submission-id>

This command creates a directory `submissions/<submission-id>` populated with
a skeletal `md.json`.

### Adding submitted content to the new directory.

Put the files for the submission directly into the `submissions/<submission-id>`
folder.

TODO what about CLDF input

⇒ See the `processing-sfm.md` tutorial file for the filename conventions for
SFM input.

### Editing the `md.json` metadata file

The metadata file uses the [JSON format][json], which is a widely
used plain-text format for exchanging data.  The file defines the following
metadata:

 - `authors` – List of all authors of the dictionary
 - `language` – Name, glottocode, and iso639-3 code of the language
 - `date_published` – year of publication, e.g. "2019"
 - `number` – A unique number for the dictionary; to be assigned by the managing
   editor
 - `properties` – A selection of properties needed to correctly process the
   idiosyncrasies of the dictionary (such as the definition of custom fields or
   the handling of cross-references).  See `processing-sfm.md` for a detailed
   description of the supported properties.

Example:  `md.json` for a fictious German dictionary.

    {
        "authors": "Erika Mustermann, Max Mustermann",
        "language": {
            "name": "German",
            "glottocode": "stan1295",
            "isocode": "deu"
        },
        "date_published": "2019",
        "number": {},
        "properties": {}
    }

[json]: https://json.org

### Writing the `intro.md`

The file `submissions/<submission-id>/intro.md` contains an introductory text to
be displayed on Dictionaria.  The file is written in the [Markdown format][md].
See section 'Writing the introduction' below for details.

### Adding comparison meanings to the dictionary.

TODO what and how?

### Validate the input files

Command:

    dictionaria check <submission-id>

This command outputs warnings about invalid data in the input files.

### Processing a submission

Command:

    dictionaria process <submission-id>

This command creates a directory `submissions/<submission-id>/processed`.  The
files in this directory will be read when importing the dictionary into
Dictionaria.

The actions performed when processing are input format dependent, but in all
cases

 - the input will be converted into the [Cross Linguistic Data Formats](cldf)
 - references to media files are switched from local filesystem paths to md5
   checksums of the file contents

[cldf]: https://cldf.clld.org

### Publishing a submission

    dictionaria release <submission-id> <...>

TODO


Common traps when editing JSON files
------------------------------------

The JSON file format is very particular about how the data is written.  At times
this makes editing a JSON file by hand a bit finicky.  This section attempts to
shed light at some common traps, people fall into when working with JSON.

### Use double quotes

Always use "double quotes" to denote text data – 'single quotes' will *not*
work.

Do:

    "property": "value"

Don't:

    'property': 'value'

### Use the right kind of bracket

Use square brackets `[…]` for lists of values.  Use curly braces `{…}` for
mappings from values to values.

Do:

    {
        "property 1": "value 1",
        "property 2": ["value 2a", "value 2b", "value 3b"]
    }

Don't:

    [
        "property 1": "value 1",
        "property 2": {"value 2a", "value 2b", "value 3b"}
    ]

### Beware of trailing commas

Make sure that there is one comma between every element in a list or mapping and
*no trailing or leading commas*.  Trailing commas tend to sneak in, when the
elements are arranged vertically for readability.

Do:

    {
        "property 1": "value 1",
        "property 2": "value 2",
        "property 3": "value 3"
    }

Don't:

    {
        "property 1": "value 1",
        "property 2": "value 2",
        "property 3": "value 3",
    }


Writing the introduction
------------------------

Every submission contains an `intro.md` file, which contains an introduction to
the dictionary and the language within it.

The file uses the [Markdown format][md].  It is a plain text format, designed to
achieve two properties:

 1. It is easy for a human being to read and write
 2. It is easy for a machine to convert into HTML

For the most part, documents written in Markdown read like regular plain text.
See [the official specification][md-syntax] for details on the syntax.

Note that the feature set in Markdown is kept quite small.  The format is meant
to make writing HTML less painful, but is was never intended as a full-fledged
replacement.  In some cases, this means that core features might be missing
– most notably tables.  However, any HTML included in a Markdown document is
kept intact during the conversion, so people often write files that contain both
Markdown and HTML.

Rule of thumb:

 - Use Markdown, wherever it is more convenient than HTML
 - Write in-line HTML anywhere else

[md]: https://daringfireball.net/projects/markdown
[md-syntax]: https://daringfireball.net/projects/markdown/syntax


The `dictionaria` command-line interface TODO
----------------------------------------

The `dictionaria` command is organised in a number of subcommands.  For a list
of all options and subcommands run the following command:

    dictionaria --help

For a short description of a specific subcommand run:

    dictionaria help <subcommand>
