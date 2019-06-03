How to Write the md.json File
=============================

Introduction
------------

This file describes the format of the `md.json` file and how to use the various
properties defined in it.  This description is structured as follows:

 * *List of `md.json` properties* – Documentation of every property supported in
   the `md.json` file
 * *How do I…* – Small tutorials on how to perform common tasks when submitting
   a dictionary, such as the addition of custom fields

TODO put somewhere more sense-making

File name conventions:

 * `db.sfm` – Main SFM database containing the dictionary itself
 * `examples.sfm` – (Optional) SFM database containing examples
 * `glosses.flextext` – (Optional) Flextext containing glossed examples


List of `md.json` properties
----------------------------

### `custom_fields`

TODO

### `entry_custom_order`

The `entry_custom_order` property contains a list of CLDF column names
specifying the order, in which custom columns for an entry are displayed in the
Dictionaria web app.  By default, custom columns are sorted alphabetically.

Example:  Order the `Phonetic_Form` column before the `Morphemic_Form`.

    "entry_custom_order": ["Phonetic_Form", "Morphemic_Form"]

### `entry_id`

The `entry_id` property specifies an SFM marker, which serves as the identifier
for the dictionary entry (default: `lx`).

Example:  Use `\lxid` as the identifier:

    "entry_id": "lxid"

### `entry_label_as_regex_for_link`

The `entry_label_as_regex_for_link` property is used to find cross-references
within SFM markers.  It contains a [regular expression][regex] identifying the
cross-reference.  These cross-references are replaced with links.

Example:  Consider words consisting of LX followed by some numbers
a cross-reference:

    "entry_label_as_regex_for_link": "\\bLX\d+\\b"

### `entry_map`

The `entry_map` property specifies, which SFM markers are mapped to which
columns in the entry table in the CLDF data.  This is used to add custom SFM
markers to the entry table.

The following markers are mapped automatically:

 * `lx` → `Headword`
 * `ps` → `Part_Of_Speech`
 * `al` → `Alternative_Form`
 * `et` → `Etymology`
 * `hm` → `Homonym`
 * `lc` → `Citation_Form`
 * `mn` → `Main_Entry`
 * `cf` → `Entry_IDs`
 * `cont` → `Contains`
 * `va` → `Variant_Form`

Example:  Add the markers `\cyr` and `\phon` to the entry table:

    "entry_map": {
        "cyr": "Cyrillic",
        "phon": "Phonetic_Representation"
    }

### `entry_sep`

The `entry_sep` property specifies a string, which separates one entry in the
database from the next (default: `"\\lx "`).  Note that this string does not
necessarily need to be an SFM marker.

Example:  Split entries on empty lines:

    "entry_sep": "\n\n"

### `example_custom_order`

The `example_custom_order` property contains a list of CLDF column names
specifying the order, in which custom columns for an example are displayed in
the Dictionaria web app.  By default, custom columns are sorted alphabetically.

Example:  Order the `Comment` column before the `French_Translation`.

    "example_custom_order": ["French_Translation", "Comment"]

### `example_map`

The `example_map` property specifies, which SFM markers are mapped to which
columns in the example table in the CLDF data.  This is used to add custom SFM
markers to the example table.

The following markers are mapped automatically:

 * `rf` → `Corpus_Reference`
 * `tx` → `Primary_Text`
 * `mb` → `Analyzed_Word`
 * `gl` → `Gloss`
 * `ft` → `Translated_Text`

Note that the example extraction process renames some of the markers internally.
This happens *after* the `marker_map` is applied, but *before* any other
processing steps.  The following markers are renamed:

 * `xv` → `tx`
 * `xvm` → `mb`
 * `xeg` → `gl`
 * `xo` → `ot`
 * `xn` → `ot`
 * `xr` → `ota`
 * `xe` → `ft`
 * `sfx` → `sf`

Also note that this only applies to examples contained in the SFM database of
the dictionary itself.  Examples that are supplied using a separate SFM file are
not affected.

Example:  Add the markers `\nt` and `\ot` to the example table:

    "example_map": {
        "nt": "Example_Note",
        "ot": "Original_Translation"
    }

### `flexref_map`

The `flexref_map` property specifies, which of FLEx's `\lf`-style
cross-references are supported.  It maps the contents of the `\lv` marker to a
separate SFM marker.

Note:  Any non-standard markers defined in the `flexref_map` need to be mapped
to CLDF columns manually, using the `entry_map`, `sense_map`, etc. properties.

The following cross references are defined automatically:

 * `cf` → `cf`
 * `syn` → `sy`
 * `ant` → `an`

Example:  Map a cross-reference named `min. pair` to the marker `\minpair`.

    "flexref_map": {
        "min. pair": "minpair"
    }

Since, `\minpair` is not a standard marker, it needs to be mapped to a CLDF
column, e.g.:

    "sense_map": {
        "minpair": "Minimal_Pair"
    }

### `gloss_ref`

The `gloss_ref` property specifies an SFM marker, which contains the reference
to a flextext gloss.

Example:  Examples store the reference to their gloss in the `\z5` marker.

    "gloss_ref": "z5"

### `labels`

The `labels` property specifies a human-readable label for an SFM-Marker.  These
will be used as headers for the respective table columns in CLDF.

Example:  Adding labels to the `\cyr` and `\phon` markers:

    "labels": {
        "cyr": "cyrillic form",
        "ps": "phonetic representation"
    }

### `link_display_label`

The `link_display_label` property defines the SFM marker that is used as a label
attached to a cross-reference (default: `lx`).

Example:  Use the `\phon` marker as the label.

    "link_display_label": "phon"

### `marker_map`

The `marker_map` properties provides a way to rename markers in the database.
This is intended for cases, where the database contains standard markers under
a different name (e.g. in FLEx exports).

Note that the mapping is applied early in the process, meaning that other
properties in the `md.json` need to refer to the *new* names of the marker.

The following markers are mapped automatically:

 * `d_Eng` → `de`
 * `g_Eng` → `ge`
 * `ps_Eng` → `ps`
 * `sc_Eng` → `sc`
 * `sd_Eng` → `sd`
 * `x_Eng` → `xe`

Example:  Map FLEx's language-specific `\lx_Ger` and `\et_Ger` to generic `\lx`
and `\et` respectively:

    "marker_map": {
        "lx_Ger": "lx",
        "et_Ger": "et"
    }

### `process_links_in_labels`

The `process_links_in_labels` property specifies, which SFM markers contain
cross-references that need to be converted into links.

Example:  Process all cross-references in the `\de` and `\cf` markers:

    "process_links_in_labels": ["de", "cf"]

### `references`

The `references` properties specifies markers that provide the sources for other
markers.  This will be collected into the `Source` column of the respective
table.

Example:  Define that `\et_bibref` contains the source for the etymology.

    "references": {
        "et_bibref": "et"
    }

### `sense_custom_order`

The `sense_custom_order` property contains a list of CLDF column names
specifying the order, in which custom columns for a sense are displayed in the
Dictionaria web app.  By default, custom columns are sorted alphabetically.

Example:  Order the `Gloss` column before the `Alternative_Translation`.

    "sense_custom_order": ["Gloss", "Alternative_Translation"]

### `sense_map`

The `sense_map` property specifies, which SFM markers are mapped to which
columns in the sense table in the CLDF data.  This is used to add custom SFM
markers to the sense table.

The following markers are mapped automatically:

 * `de` → `Description`
 * `nt` → `Comment`
 * `sc` → `Scientific_Name`
 * `sd` → `Semantic_Domain`
 * `sy` → `Synonym`
 * `zcom1` → `Concepticon_ID`

Example:  Add the marker `\gr` to the sense table:

    "sense_map": {
        "gr": "Russian_Translation"
    }

### `sense_sep`

The `sense_sep` property specifies an SFM marker, which determines, where a new
sense starts (default: `sn`).

Example:  Use the `\sn_id` marker to separate senses:

    "sense_sep": "sn_id"


How do I…
---------

### …fix standard markers with the wrong name?

Situation:  The dictionary uses different names for common markers like `\lx` or
`\de`.

Solution:  Use the `marker_map` property to rename the markers.  The mapping
happens early on in the process, so any other properties need to refer to the
*new* name.

Example:  FLEx attaches language codes to standard markers, when exporting to
SFM.

    "properties": {
        "marker_map": {
            "x_Ger": "xv",
            "et_Ger": "et"
        }
    }

See the section on `marker_map` for the markers mapped by default.

### …define custom fields for my dictionary?

Situation:  The dictionary contains custom SFM markers, which need to be
included in the CLDF database.

Solution:  Use the `entry_map`, `sense_map`, and `example_map` properties to
define, which column names the markers should be mapped to.  Note that column
names may only contain the letters a–z (small or capital), numbers and the
underscore `_`.

Example:  Defining custom columns for `\cyr`, `\phon`, `\gr`, and `\ot`.

    "properties": {
        "entry_map": {
            "cyr": "Cyrillic",
            "phon": "Phonetic_Representation"
        },
        "sense_map": {
            "gr": "Russian_Translation"
        },
        "example_map": {
            "ot": "Original_Translation"
        }
    }

See the sections on the `entry_map`, `sense_map`, and `example_map` properties
for markers, which are mapped by default.

### …specify the source for a field?

Situation:  There are SFM markers that contain a reference (e.g. a bibliography
key) to the source of other fields.

Solution:  Use the `references` property to specify, which field a marker is
a reference for.

Example:  The dictionary contains a marker `\de_bibref`, containing the source
for the description `\de`, a marker `\sc_bibref`, containing the source for the
scientific name `\sc`, and a marker `\gl_bibref`, containing the source for
a gloss `\gl`:

    "properties": {
        "references": {
            "de_bibref": "de",
            "sc_bibref": "sc",
            "gl_bibref": "gl"
        }
    }

This has the effect that the contents are `\de_bibref` and `\sc_bibref` fields
are stored in the `Source` column of the Sense Table.  The same happens with
`\gl_bibref`.   However, since the contents of the `\gl` marker are stored
in the Example Table the reference is stored in that table's `Source` column.

### …process cross-references within markers?

Situation:  Some entries in the dictionary contain cross-references to other
entries, intended to be a link.

Solution:  Link processing requires the definition of two properties:
`process_links_in_labels` and `entry_label_as_regex_for_link`.  The former lists
all SFM markers, which need to be scanned for links (none by default).  The
latter contains a [regular expression][regex], which defines what a reference
looks like.

This works best for dictionaries with explicit entry ids (see next section
below) that follow a predictable and easily searchable pattern, e.g. single
words using a common prefix.

The process script will look through every of the specified markers, look for
identifiers using the regular expression, and replace the identifiers with
[markdown-style links][md-link], which follow the form `[target](anchor)`.  The
target of the link is filled with the identifier for the respective row in the
Entry Table.  The anchor of the link is filled with a human readable label.

Note that there is a small set of markers markers, which are treated differently
(currently `\mn`, `\cf`, `\cont`, `\sy`, and `\an`).  In these cases the
identifiers are just replaced with the bare CLDF identifiers.

Also note that the original id of the dictionary entry may differ from the CLDF
identifier of the table row.  The script tries to use the original identifiers
whenever possible, but any identifiers that are not unique or otherwise
incompatible with the CLDF spec will be rejected and replaced with newly
generated ones.

By default the human readable label comes from the content of the `\lx` marker.
This can be changed by specifying a different marker in the `link_display_label`
property.

Example:  Consider the following dictionary:

    \lx branne
    \id ENTRY00001
    \phon branə
    \de house

    \lx brannemanne
    \id ENTRY00002
    \phon branəmanə
    \de front door; door of a house (ENTRY00001)
    \cf ENTRY00001

The entry for *brannemanne* contains a reference to *branne* in both the `\de`
and `\cf` fields.  To process these links, we define the following properties:

    "properties": {
        "entry_id": "id",
        "process_links_in_labels": ["de", "cf"],
        "entry_label_as_regex_for_link": "\\bENTRY\\d+\\b"
    }

In the `\de` field this replaces the `ENTRY00001` with `[branne](ENTRY00001)`.
In the `\cf` field, however, the reference is only replaced with a bare link
like `ENTRY00001`.  Note that in both cases, the identifiers in the links are
identical to the original ids, but only because `ENTRY00001` and `ENTRY00002`
are both valid in CLDF.

To make the label show the contents `\phon` marker instead (e.g.
`[branə](ENTRY00001)`), the properties would change as follows:

    "properties": {
        "entry_id": "id",
        "process_links_in_labels": ["de", "cf"],
        "entry_label_as_regex_for_link": "\\bENTRY\\d+\\b",
        "link_display_label": "phon"
    }

### …use explicit entry ids

Situation:  The dictionary uses a special SFM marker to store an identifier for
each entry, which is referenced in other places.

Solution:  By default the processing script will identify entries using their
`\lx` and `\hm` markers.  This behaviour can be changed by setting the
`entry_id` property.

Example:  A dictionary uses the marker `\id` to store identifiers for entries.

    "properties" : {
        "entry_id": "id"
    }

### …provide examples in a separate SFM file

Situation:  Examples are stored in a separated SFM database.

Solution:  Provide the examples as part of the submission using the file name
`examples.sfm`.  The conv

 * In `examples.sfm`: Each example should specify a unique identifier in the
   `\ref` marker.
 * In `db.sfm`: The senses should refer to their examples by specifying the
   example ID in the `\xref` marker.

Example for an `examples.sfm` file:

    \ref ex.001
    \tx Leute, Klaus hat Schnitten mitgebracht!
    \ft Guys, Klaus brought sandwiches!

    \ref ex.002
    \tx Kann ich eine Schnitte mit Käse haben?
    \ft Can I have a cheese sandwich?

Example for the corresponding `db.sfm` file:

    \lx Käse
    \ps n
    \de cheese
    \xref ex.002

    \lx Schnitte
    \ps n
    \de sandwich
    \xref ex.001
    \xref ex.002

### …process FLEx's `\lf`, `\lv`, and `\le` markers`

Situation:  In FLEx exports, cross-references are stored in a `\lf`, `lv`, `\le`
triplet like so:

    \lf <name>
    \lv <lemma> <sense no>
    \le <label>

Solution:  This is a two step process:

 1. Use the `flexref_map` property to map the name defined in `\lf` to an SFM
    marker.
 2. Use the `entry_map`, `sense_map`, etc. property to map that SFM marker to
    a CLDF table column.

Example:  The database contains a field called 'min. pair', which contains
a reference to another entry.  A FLEx export of this might look like this:

    \lf min. pair
    \lv Grund2 1
    \le Grund

To process this reference and add it to a new column in the Sense Table, define
the following properties:

    "properties": {
        "flexref_map": {
            "min. pair": "minpair"
        },
        "sense_map": {
            "minpair": "Minimal_Pair"
        }
    }

### …add glosses in the flextext format

Situation:  In FLEx exports the `db.sfm` only contains unglossed examples, while
the glosses are exported in a separate file, using the `flextext` format.

Solution:  Dictionaria is able to extract glosses from the `flextext` file and
merge them into the corresponding examples.

TODO What needs to be done on the FLEx side to make this happen?

FLEx will store a reference to the gloss in an SFM marker, which FLEx usually
calls `\zXX`, where `XX` stands for a number (`\z1`, `\z2`, etc.).   Note that
(a) the user has no control over the name of this marker and (b) the name might
be different from database to database.  To tell Dictionaria about the exact
marker, use the `gloss_ref` property in the `md.json`:

    "properties": {
        "gloss_ref": "z5"
    }

### …specify the order, in which the fields are displayed in the web app

Situation:  When the Dictionaria web app displays entries with custom fields,
the fields are shown in alphabetical order by default.  This might not be
desirable in all cases.

Solution:  The properties `entry_custom_order`, `sense_custom_order`, and
`example_custom_order` specify explicitly, in what order the columns of an
entry, sense, or example should be displayed.

Example:  Consider a dictionary defining three custom fields in the Entry Table:

    "properties": {
        "entry_map": {
            "cyr": "Cyrillic",
            "phon": "Phonetic_Form",
            "pd": "Inflection_Class"
        }
    }

In the web app, entries using these fields might look something like this:

    solnce `sun'

    Cyrillic: солнце
    Inflection_Class: neuter
    Phonetic_Form: sónce

In this example, the inflection class is put in between the Cyrillic and
phonetic representations of the head word.  To keep the two representations next
to each other, one can specify the order explicitly using the
`entry_custom_order` property:

    "properties": {
        "entry_map": {
            "cyr": "Cyrillic",
            "phon": "Phonetic_Form",
            "pd": "Inflection_Class"
        },
        "entry_custom_order": ["Cyrillic", "Phonetic_Form", "Inflection_Class"]
    }

Now the entry renders as follows:

    solnce `sun'

    Cyrillic: солнце
    Phonetic Form: sónce
    Inflection_Class: neuter

[md-link]: https://daringfireball.net/projects/markdown/syntax#link

[regex]: https://docs.python.org/3/howto/regex.html
