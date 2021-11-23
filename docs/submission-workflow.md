How to Prepare a Submission
===========================


Prerequisites
-------------

For instructions on how to get your system set up for using CLDF benches, refer
to the file `getting-started.md`.


Workflow
--------

The editorial workflow to process dictionaries from submission to publication is
a series of automated or manual steps.  The automated steps are implemented as
sub-commands of the `cldfbench` command-line program.

### Initialising a new submission

    cldfbench new --template=dictionaria

The creation process will ask you a few questions:

 - `id`: A unique id for the dictionary, also used as the folder name for the
   new submission – usually the name of the language in all lower case
 - `title`: A title for the dictionary (when left blank the title will be
   ‘&lt;Language&gt; dictionary’)
 - `license`: Usually `CC-BY-4.0`
 - `url`: URL of the dictionary; will be overwritten upon the dictionary's
   release
 - `citation`: How to cite the dictionary; you can leave this blank for now
   – this only becomes relevant when you know that the citation will actually be

### Creating the virtual environment

To create a new virtual environment for a CLDF bench, `cd` into the folder of
the CLDF bench and run the following command.

    virtualenv ENV

This will create the folder `ENV` and fill it with a separate Python
installation for your CLDF bench.  By the way, the folder name is completely
arbitrary.  You can also give the folder any other name by changing the command
above accordingly.  However, it is common convention to call it `ENV`, `env`,
`VENV`, `venv`, or something along those lines.

The rest of this document will assume the folder is named `ENV` (in all-caps).

*Note:*
Internally the virtual environment uses absolute paths to find python packages
within it.  This means you have to delete and recreate the virtual environment
every time, you move the CLDF bench to a different location.

To delete a virtual environment, all you need to do is delete its `ENV` folder.

### Activating the virtual environment

In order to ‘dive into’ the virtual environment, you have to *activate* it.
This is done by `cd`-ing into the folder of the CLDF bench and running the
following command.

On Windows, using the classic `cmd.exe` shell (recommended):

    ENV\Scripts\activate.bat

On Windows, using Powershell (might fail depending on system settings):

    ENV\Scripts\activate.ps1

On Unix-like operating systems (using `bash`, `zsh`, etc):

    . ENV/bin/activate

Note that a virtual environment is only activated *for the current shell*.  This
means this command only affects the terminal you are currently working in.  This
also means that you have to re-run the command every time you close and re-open
your terminal window.

After running this, Python will run the version from the virtual environment
instead of the system-wide installation and any package you install with `pip`
will be installed into the `ENV` folder.

### Installing the CLDF bench into the virtual environment

From a technical perspective, a CLDF bench is just a special kind of Python
package.  And because of that it can be installed like any other package.

The following command installs the CLDF bench into your virtual environment
(make sure the virtual environment is activated first).

    pip install -e .[test]

Quick explanation:

 * The `-e` option installs the CLDF bench in *editable mode*.  Without it you
   would have to rerun this command every time you change something in the
   CLDF bench.
 * The command uses `.` instead of a package name to signify that `pip` should
   install ‘whatever Python package is located in the current folder’
 * The `[test]` after the `.` tells pip to install additional packages that you
   can use to check the validity of the CLDF dictionary

### Adding submitted content to the new directory.

Put any files provided by the author of the dictionary into the `raw/` folder
within your CLDF bench.  For dictionaries in Toolbox's SFM format Dictionaria
expects the following file names:

 - `db.sfm` – Main SFM database containing the dictionary itself
 - `examples.sfm` – (Optional) SFM database containing examples
 - `glosses.flextext` – (Optional) Flextext containing glossed examples

### Editing the `md.json` metadata file

The metadata file uses the [JSON format][json], which is a widely
used plain-text format for exchanging data.  The file defines the following
metadata:

 - `authors` – List of all authors of the dictionary
 - `language` – Name, glottocode, and iso639-3 code of the language
 - `properties` – A selection of properties needed to correctly process the
   idiosyncrasies of the dictionary (such as the definition of custom fields or
   the handling of cross-references).  See `md-json-properties.md` for
   a detailed description of the supported properties.

Example:  `md.json` for a fictitious German dictionary.

    {
        "authors": ["Erika Mustermann", "Max Mustermann"],
        "language": {
            "name": "German",
            "glottocode": "stan1295",
            "isocode": "deu"
        },
        "properties": {}
    }

[json]: https://json.org

### Writing the `intro.md`

The file `raw/intro.md` contains an introductory text to be displayed on
Dictionaria.  The file is written in the [Markdown format][md].  See section
'Writing in markdown' below for details.

A few notes on the introduction itself:

1. Do not manually add a table of contents -- the webapp will generate its own
   based on the structure of your document

2. Do not manually add a heading for the document title -- the webapp will
   generate one from the `md.json`.  By default the title will be "[language
   name] Dictionary".  To set a custom title for your dictionary, the `title`
   property to the `md.json` file, e.g.:

    "properties": {
        "title": "A Comprehensive Dictionary of the Martian Language"
    }

### Adding comparison meanings to the dictionary.

TODO what and how?

### Processing a submission

To process a submission, first activate the virtual environment (see above) and
run the following command:

    cldfbench makecldf cldfbench_*.py

This command creates a new [CLDF](cldf) dataset in the `cldf/` folder.  The
files in this directory will be read when importing the dictionary into
Dictionaria.

*Beware:*
Do not manually add or edit any files in the `cldf/` folder.  Any changes you
make will be overwritten completely the next time you run `makecldf`.

The actions performed when processing are input format dependent, but in all
cases

 - the input will be converted into CLDF
 - references to media files are switched from local filesystem paths to md5
   checksums of the file contents

[cldf]: https://cldf.clld.org

### Generating the CLDF readme in `cldf/README.md`

`cldfbench` can generate a readme file in the `cldf/` folder, which contains
a human-readable version of the metadata in [Markdown][md].  This will also show
up nicely rendered if you look at the `cldf/` folder on Github.

The generate the `cldf/README.md` file, run:

    cldfbench cldfreadme cldfbench_*.py

### Preparing a submission for publication

The `dictionaria.release` subcommand prepares the submission for publication,
doing the following:

 - Generates the README.md for the entire project, which will also include the
   contents of the `intro.md`
 - Fills in some of the missing fields of the `metadata.json` (not to be
   confused with `etc/md.json`)
 - Creates the `.zenodo.json` file, which contains metadata, used by Zenodo

To start this process, run:

    cldfbench dictionaria.release cldfbench_*.py

### Publication workflow

 - Regenerate the dataset:

    cldfbench makecldf cldfbench_*.py

 - [Load the dictionary into the local webapp][rebuild-db] and look it over

 - Test the validity of the CLDF data:

    pytest

 - Prepare for release:

    cldfbench dictionaria.release cldfbench_*.py

 - Manually double-check the `.zenodo.json` and `metadata.json` files and add
   missing information (is the citation there etc.)

 - Create a new release on Github

 - Mark the dictionary as `published` in the `dictionaria-intern` repo

 - [Load published datasets into webapp db][rebuild-db]

 - Deploy

[rebuild-db]: https://github.com/dictionaria/dictionaria/blob/master/README.md


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


Writing in Markdown
-------------------

The introduction file uses the [Markdown format][md].  It is a plain text
format, designed to achieve two goals:

 1. To be easy for a human being to read and write
 2. To be easy for a machine to convert into HTML

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
