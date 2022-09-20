How to Write the md.json File
=============================

Introduction
------------

This file describes the format of the `md.json` file and how to use the various
properties defined in it.  This description is structured as follows:

 - *List of `md.json` properties* – Documentation of every property supported in
   the `md.json` file
 - *How do I…* – Small tutorials on how to perform common tasks when submitting
   a dictionary, such as the addition of custom fields


List of `md.json` properties
----------------------------

### `cross_references`

The `cross_references` property contains a list of SFM markers, which contain
reference to other entries.

The following markers are considered cross-references by default: `an`, `cf`,
`cont`, `mn`, and `sy`.

Example:  Define that the `\my_ref` and `\my_other_ref` markers contain
cross-references:

    "cross_references": ["my_ref", "my_other_ref"]

### `custom_fields`

The `custom_fields` property contains a list of columns, which will be displayed
in the `Words` tab on the Dictionaria web app.  This property contains the
*labels* of each column as opposed to their CLDF column names (see the `labels`
and `metalanguages` properties).

If a column does not have an explicit label, the web app will use the CLDF column
name *with all underscores replaced by spaces*.

Note that the web app only allows for up to *two* custom fields in the `Words`
tab, otherwise table columns would get squished beyond readability on
non-widescreen devices.

Example:  Add the phonetic form and the semantic domain to the Words tab:

    "custom_fields": ["Phonetic Form", "Semantic Domain"]

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

### `entry_map`

The `entry_map` property specifies, which SFM markers are mapped to which
columns in the entry table in the CLDF data.  This is used to add custom SFM
markers to the entry table.

The following markers are mapped automatically:

 - `lx` → `Headword`
 - `ps` → `Part_Of_Speech`
 - `al` → `Alternative_Form`
 - `et` → `Etymology`
 - `hm` → `Homonym`
 - `lc` → `Citation_Form`
 - `mn` → `Main_Entry`
 - `cf` → `Entry_IDs`
 - `cont` → `Contains`
 - `va` → `Variant_Form`

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

Example:  Order the `Comment` column before the `Grammar_Note`.

    "example_custom_order": ["Grammar_Note", "Comment"]

### `example_map`

The `example_map` property specifies, which SFM markers are mapped to which
columns in the example table in the CLDF data.  This is used to add custom SFM
markers to the example table.

The following markers are mapped automatically:

 - `rf` → `Corpus_Reference`
 - `tx` → `Primary_Text`
 - `mb` → `Analyzed_Word`
 - `gl` → `Gloss`
 - `ot` → `alt_translation1`,
 - `ota` → `alt_translation2`,
 - `ft` → `Translated_Text`

Note that the example extraction process renames some of the markers internally.
This happens *after* the `marker_map` is applied, but *before* any other
processing steps.  The following markers are renamed:

 - `xv` → `tx`
 - `xvm` → `mb`
 - `xeg` → `gl`
 - `xo` → `ot`
 - `xn` → `ot`
 - `xr` → `ota`
 - `xe` → `ft`
 - `sfx` → `sf`

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

 - `cf` → `cf`
 - `syn` → `sy`
 - `ant` → `an`

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
        "cyr": "Cyrillic Form",
        "ps": "Phonetic Representation"
    }

### `link_label_marker`

The `link_label_marker` property defines the SFM marker that is used as a label
attached to a cross-reference (default: `lx`).

Example:  Use the `\phon` marker as the label.

    "link_label_marker": "phon"

### `link_regex`

The `link_regex` property defines a [regular expression][regex], which is used
to find links within SFM markers.  These are replaced with markdown-style links.

Example:  Consider words consisting of LX followed by some numbers
a cross-reference:

    "link_regex": "\\bLX\d+\\b"

### `marker_map`

The `marker_map` properties provides a way to rename markers in the database.
This is intended for cases, where the database contains standard markers under
a different name (e.g. in FLEx exports).

Note that the mapping is applied early in the process, meaning that other
properties in the `md.json` need to refer to the *new* names of the marker.

The following markers are mapped automatically:

 - `d_Eng` → `de`
 - `g_Eng` → `ge`
 - `ps_Eng` → `ps`
 - `sc_Eng` → `sc`
 - `sd_Eng` → `sd`
 - `x_Eng` → `xe`

Example:  Map FLEx's language-specific `\lx_Ger` and `\et_Ger` to generic `\lx`
and `\et` respectively:

    "marker_map": {
        "lx_Ger": "lx",
        "et_Ger": "et"
    }

### `media_caption_marker`

The `media_caption_marker` defines an SFM marker which contains the caption to
media files (images, sound files, etc.).

Note that the captions need to follow *directly after* their corresponding media
file tag (`\pc`, `\sf`, etc.) to be recognised.

Example:  Specifiy that the captions for media files are stored in the `\cap`
SFM marker.

    "media_caption_marker": "cap"

### `media_lookup`

When looking for media files in *cdstar*, the processing script only considers
files associated with the current submission by default.  This behaviour can be
changed by specifying a list of submission IDs in the `media_lookup` property.

Example:  Include media files with the IDs `German` and IDs `German_LegalTerms`:

    "media_lookup": ["German", "German_LegalTerms"]

### `metalanguages`

The `metalanguages` property sets the labels for translations in languages other
than English.  It maps the SFM markers `gxx` and `gxy` to the first and second
meta language respectively.

Example:  Add Spanish and Quichua as meta languages.

    "metalanguages": {
        "gxx": "Spanish",
        "gxy": "Quichua"
    }

### `process_links_in_markers`

The `process_links_in_markers` property specifies, which SFM markers contain
cross-references that need to be converted into markdown-style links.

Example:  Process all cross-references in the `\de` marker:

    "process_links_in_markers": ["de"]

### `second_tab`

The `custom_fields` property contains a list of columns, which will be displayed
in the `Words extra` tab on the Dictionaria web app.  This property contains the
*labels* of each column as opposed to their CLDF column names (see the `labels`
and `metalanguages` properties).

If a column does not have an explicit label, the web app will use the CLDF column
name *with all underscores replaced by spaces*.

Note that the web app only allows for up to *three* custom fields in the `Words
extra` tab, otherwise table columns would get squished beyond readability on
non-widescreen devices.

Example:  Add the phonetic form and the semantic domain to the Words tab:

    "second_tab": ["French", "Phonetic Form", "Semantic Domain"]

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

 - `de` → `Description`
 - `nt` → `Comment`
 - `sc` → `Scientific_Name`
 - `sd` → `Semantic_Domain`
 - `sy` → `Synonym`
 - `an` → `Antonym`
 - `zcom1` → `Concepticon_ID`

Example:  Add the marker `\ge` to the sense table:

    "sense_map": {
        "ge": "Gloss"
    }

### `sense_sep`

The `sense_sep` property specifies an SFM marker, which determines, where a new
sense starts (default: `sn`).

Example:  Use the `\sn_id` marker to separate senses:

    "sense_sep": "sn_id"

### `sources`

The `sources` property specifies markers that provide the sources for other
markers.  This will be collected into the `Source` column of the respective
table.

Example:  Define that `\et_bibref` contains the source for the etymology.

    "sources": {
        "et_bibref": "et"
    }

### `title`

The `title` property specifies a custom title for the dictionary.
sense starts (default: "&lt;Language&gt; dictionary").

Example:  Set the title to "A dictionary for the Martian language.".

    "title": "A comprehensive dictionary for the Martian language."


How do I…
---------

### …give my dictionary a custom name?

Situation:  By default the dictionary is called "&lt;Language&gt; dictionary".

Solution:  Use the `title` property to customise the name of the dictionary.

Example:

    "properties": {
        "title": A comprehensive dictionary for the Martian language"
    }

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

### …add translations in languages other than English

Situation:  The dictionary provides translations in other meta languages in
addition to English.

Solution:  Map the respective markers to the `alt_translation1` and
`alt_translation2` columns and add the names of the meta language to the
`metalanguages` properties, using `gxx` for the first and `gxy` for the second
meta language.

Example:  A dictionary provides a Spanish translation in the `\d_es` marker and
a Quichua translation in the `\d_qu` marker:

    "sense_map": {
        "d_es": "alt_translation1",
        "d_qu": "alt_translation2"
    },
    "metalanguages": {
        "gxx": "Spanish",
        "gxy": "Quichua"
    }

### …display custom fields on the Dictionaria web app?

Situation:  There are some custom fields that should be displayed on the `Words`
and `Words extra` tabs on the web app.

Solution:  Use the `custom_fields` property to specify fields to be added to
the `Words` tab and the `second_tab` property to specify fields to be added to
the `Words extra` tab.  Note that these properties take the *labels* that are
displayed in the table header.

Example:  Add the phonetic form to the `Words` tab; add the Russian translation
and a Comment in Russian to the `Words extra` tab.

    "entry_map": {
        "ph": "Phonetic_Form"
    },
    "sense_map": {
        "gxx": "alt_translation1",
        "nt_ru": "Comment_Russian"
    },
    "metalanguages": {
        "gxx", "Russian"
    },
    "labels": {
        "Comment_Russian": "Comment (Russian)"
    },
    "custom_fields": ["Phonetic Form"],
    "second_tab": ["Russian", "Comment (Russian)"]

Note how the different table headers come about:

 1. `Comment (Russian)` was defined explicitly in the `labels` property.
 2. `Russian` was defined in the `metalanguages` property.
 3. `Phonetic Form` was automatically generated for the `Phonetic_Form` column
    (by replacing underscores `_` with spaces ` `).

### …specify the source for a field?

Situation:  There are SFM markers that contain a reference (e.g. a bibliography
key) to the source of other fields.

Solution:  Use the `sources` property to specify, which field a marker is
a reference for.

Example:  The dictionary contains a marker `\de_bibref`, containing the source
for the description `\de`, a marker `\sc_bibref`, containing the source for the
scientific name `\sc`, and a marker `\gl_bibref`, containing the source for
a gloss `\gl`:

    "properties": {
        "sources": {
            "de_bibref": "de",
            "sc_bibref": "sc",
            "gl_bibref": "gl"
        }
    }

This has the effect that the contents are `\de_bibref` and `\sc_bibref` fields
are stored in the `Source` column of the Sense Table.  The same happens with
`\gl_bibref`.   However, since the contents of the `\gl` marker are stored
in the Example Table the reference is stored in that table's `Source` column.

### …process cross-references?

Situation:  Some markers contain cross-references to other entries.

Solution:  Add these markers to the `cross_references` properties and map them
to a CLDF column.

Example:  Consider the following Russian dictionary, where imperfective verbs
contain a reference to the perfective counterparts and vice versa using the
`\cf_asp` marker:

    \lx rasskazyvat'
    \de tell (imperf.)
    \cf_asp rasskazat'

    \lx rasskazat'
    \de tell (perf.)
    \cf_asp rasskazyvat'

To process the references in the `\cf_asp` markers, define the following
properties:

    "properties": {
        "cross_references": ["cf_asp"],
        "sense_map": {
            "cf_asp": "Aspect_Counterpart"
        }
    }

### …process links within markers?

Situation:  Some entries in the dictionary contain in-line cross-references to
other entries, intended to be a link.

Solution:  Link processing requires the definition of two properties:
`process_links_in_markers` and `link_regex`.  The former lists all SFM markers,
which need to be scanned for links (none by default).  The latter contains
a [regular expression][regex], which defines what a reference looks like.

This works best for dictionaries with explicit entry ids (see next section
below) that follow a predictable and easily searchable pattern, e.g. single
words or numbers using a common prefix.

The process script searches through every of the specified markers, look for
identifiers using the regular expression, and replace the identifiers with
[markdown-style links][md-link], which follow the form `[target](anchor)`.  The
target of the link is filled with the identifier for the respective row in the
Entry Table.  The anchor of the link is filled with a human readable label.

By default the human readable label comes from the content of the `\lx` marker.
This can be changed by specifying a different marker in the `link_label_marker`
property.

Note that the original id of the dictionary entry may differ from the CLDF
identifier of the table row.  The script tries to use the original identifiers
whenever possible, but any identifiers that are not unique or otherwise
incompatible with the CLDF specification will be rejected and replaced with
newly generated ones.

Example:  Consider the following dictionary:

    \lx branne
    \id ENTRY00001
    \phon branə
    \de house

    \lx brannemanne
    \id ENTRY00002
    \phon branəmanə
    \de front door; door of a house (ENTRY00001)

The entry for `brannemanne` contains a reference to `branne` within the `\de`
marker.  To process this link, we define the following properties:

    "properties": {
        "entry_id": "id",
        "process_links_in_markers": ["de"],
        "link_regex": "\\bENTRY\\d+\\b"
    }

This replaces any occurrence of the word `ENTRY` followed by at least one digit
with a link.  In this case the reference `ENTRY00001` is turned into a link like
`[branne](ENTRY00001)`.  Note the identifier in the link is identical to the
original id, but only because `ENTRY00001` *happens* to be a valid id in CLDF.

To make the label show the contents `\phon` marker instead (e.g.
`[branə](ENTRY00001)`), the properties would change as follows:

    "properties": {
        "entry_id": "id",
        "process_links_in_markers": ["de"],
        "link_regex": "\\bENTRY\\d+\\b",
        "link_label_marker": "phon"
    }

### …use explicit entry ids?

Situation:  The dictionary uses a special SFM marker to store an identifier for
each entry, which is referenced in other places.

Solution:  By default the processing script will identify entries using their
`\lx` and `\hm` markers.  This behaviour can be changed by setting the
`entry_id` property.

Example:  A dictionary uses the marker `\id` to store identifiers for entries.

    "properties" : {
        "entry_id": "id"
    }

### …provide examples in a separate SFM file?

Situation:  Examples are stored in a separated SFM database.

Solution:  Provide the examples as part of the submission using the file name
`examples.sfm`.  The conv

 - In `examples.sfm`: Each example should specify a unique identifier in the
   `\ref` marker.
 - In `db.sfm`: The senses should refer to their examples by specifying the
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

### …process FLEx's `\lf`, `\lv`, and `\le` markers?

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

### …add glosses in the flextext format?

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

### …specify the order, in which the fields are displayed in the web app?

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

### …add captions to my images/sound files?

Situation:  There is some information that needs to be displayed alongside
a media file (description, speaker info, copyright info, etc.).

Solution:  Specify an SFM marker for the captions using the
`media_caption_marker` property and make sure the captions follow *immediately
after* the media file they are describing.

Example:  Adding a caption to media files using the SFM marker `\cap`:

    "properties": {
        "media_caption_marker": "cap"
    }

The corresponding `db.sfm` might look something like this:

    \lx Haus
    \ps n
    \de house
    \pc haus.jpg
    \cap Depiction of a traditionally built house
    \xv Wir bauen ein Haus
    \xe We are building a house
    \sfx wir-bauen-ein-haus.mp3
    \cap Speaker: Max Mustermann, recorded on 20 Feb 2020

Example 2:  What if there is an existing database, which uses different caption
markers for different file types (e.g. `\pc_caption` for images and
`\sf_caption` for sound files)?

Answer:  Pick one of the markers as the `media_caption_marker` and use the
`marker_map` to convert the others.  The properties might look as follows:

    "properties": {
        "marker_map": {
            "sf_caption": "pc_caption",
            "sfx_caption": "pc_caption"
        },
        "media_caption_marker": "pc_caption"
    }

[md-link]: https://daringfireball.net/projects/markdown/syntax#link

[regex]: https://docs.python.org/3/howto/regex.html
