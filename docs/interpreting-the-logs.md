Interpreting the Logs
=====================


The `check` and `process` subcommands output all kinds of warnings and/or error
messages.  This file aims to help interpreting the messages and provide hints
on how to fix any issues with a submission.


The `check` subcommand
----------------------

### `\lx <headword>: missing file [...]`

References to media files such as `\sf` or `\pc` must refer to a real file name
in the CDSTAR database.  This message indicates that a media file reference was
dropped from an entry, because the file name was not found in CDSTAR.

*How do I fix this?*

1. Check if there is a typo in the filename.  Be especially careful about
   characters that look very similar, but have different Unicode code points
   (such as Latin A vs. Cyrillic А vs. Greek Α, etc.).
2. Upload any actually missing files to CDSTAR

### `ERROR \lx <headword>: duplicate lemma

This message indicates that there are multiple entries sharing the same value
for the `\lx` and `\hm` markers.

Having multiple entries with the same `\lx` is not a problem in itself:  The
CLDF conversion process will add *all* the entries to the dictionary, giving
them unique identifiers in the process.  However it might still be a good idea
to double check the entries:

1. The entries might be proper duplicates.
2. Other entries might contain ambigue cross-references in their `\cf` etc.
   markers.

*How do I fix this?*

1. Delete any duplicate entries.
2. Add unique homonym numbers `\hm` to the entries to disambiguate them.  Also
   make sure to use the search feature of Your Editor of Choice to go through
   the dictionary and fix any cross-references.

### `ERROR \lx <headword>: no \de field`

Every entry needs a description, using the `\de` marker.  This message indicates
that an entry is lacking such a marker.

*How do I fix this?*

1. If the dictionary uses a different marker for the description *consistently
   throughout the entire database*, add it to the `marker_map` property in the
   `md.json`.
2. Otherwise manually fix the entry in the original database.

### `ERROR \lx <headword>: multiple \de but not matching \sn`

This message means that there is a discrepancy between the number of `\sn`
markers and the number of `\de` markers.  This could have multiple causes:

1. A sense is missing a `\de` marker
2. There are multiple `\de` markers within the same sense
3. There is an additional `\de` marker before the first sense

*How do I fix this?*

Manually fix the entry in the original database.

### `ERROR \lx <headword>: multiple conflicting \ps`

An entry cannot have more than one Part of Speech, therefore it should have only
one distinct `\ps` marker.  This message indicates that an entry contains
multiple `\ps` markers with different values.  `\ps` markers with identical
values are merged automatically.

*How do I fix this?*

1. Check the `\ps` marker for typos and correct them
2. If there are different `\ps` markers for different senses, split those senses
   off into a separate entry.  You might have to add a new homonym number `\hm`
   to the entry and fix any cross-references accordingly.

### `ERROR \lx <headword>: invalid ref: [...]`

This message indicates that cross-references in markers such as `\cf` or `\mn`
point to a non-existent entries.

*How do I fix this?*

Check the reference for typos and make sure the affected reference contains the
exact identifier or headword.  Pay extra attention to missing or wrong homonym
numbers.

### `ERROR \lx <headword>: invalid bibkey: \bibref [...]`

This message indicates that the `\bibref` marker of an entry contains a reference
to a bibliography entry not found in the `sources.bib`.

*How do I fix this?*

1. Check the entry for types.
2. Add any missing bibliography entries to you `sources.bib`

### `ERROR \lx <headword>: illegal marker: \se`

The `\se` marker is commonly used to create subentries.  Dictionaria does not
support subentries.

*How do I fix this?*

Split any subentries off into separate entries.  If you want to preserve the
notion that the subentry relates to the parent entry, specify a new marker in
the subentry and add a cross-reference to the parent entry.  Remember to add the
new marker to the `cross-references` property in the `md.json`.


`examples.log`
--------------

The `examples.log` file in the submission folder is created, when the processing
script extracts examples from the `db.sfm` (i.e. the examples were not provided
in a separate `examples.sfm` file).

### `# incomplete example in lx <headword> - missing xv/xe`

Every example must at least have a `\xv` and `\xe` field.  If any of those two
is missing the example is dropped.

*How do I fix this?*

Manually fix or delete the affected example in the original database.

### `# cannot merge [...] and [...]`

In SFM databases, examples are embedded directly in their respective dictionary entries.
As result, if multiple entries are exemplified by the same example, the example
has to be copied into every entry – in its entirety.

To avoid duplicates in the CLDF database, the processing script attempts to
merge any examples that share the same text and the same translation into one.
The error message means that the merging process failed.   In this case both
variants of the example will be added to the CLDF database as separate examples.

*How do I fix this?*

Edit the examples, such that none of the fields conflict with each other.

`cldf.log`
----------

The `cldf.log` file in the submission folder is created by the processing
script.  It contains warnings and errors that occurred on the way from the
original `db.sfm` to the final CLDF database.  The messages usually appear in
the same order as they are presented here.

### `WARNING No CLDF column defined for markers: [...]`

This is just a list of every SFM marker, which has not been processed in any
way.

*How do I fix this?*

Edit the `md.json` file to map the SFM markers to their respective table
columns.  Note that some markers are just time stamps, ‘notes to self’, or other
supplementary information.  Those can safely be ignored.

### `ERROR \lx <headword>: entry dropped due to missing/empty \ps marker`

Every entry needs a Part of Speech.  If the `\ps` marker is missing or empty,
the entry will be dropped.

*How do I fix this?*

Edit the original entry and add content to the `\ps` marker.  If the part of
speech of entry is uncertain at your stage of language documentation set the value of the `\ps` marker to `uncertain`.

### `ERROR \lx <headword>: entry dropped due to conflicting \ps markers: [...]`

This message occurs, when an entry has multiple `\ps` markers with different
values.

*How do I fix this?*

See section above on the message
`ERROR \lx <headword>: multiple conflicting \ps`
in the section above on the `check` subcommand.

### `WARNING \lx <headword>: sense markers before first \sn: [...]`

Every sense needs to start with an `\sn` marker – the sole exception being
entries with exactly one `\sn` marker.

*How do I fix this?*

Check the original entry for typos or missing `\sn` markers and edit it
accordingly.

### `WARNING senses refer to non-existent examples: [...]`

This message occurs, when a sense contains a reference to an example.  This is more
likely to happen, if examples are provided in a separate `examples.sfm` file.

*How do I fix this?*

Check the reference for typos or remove the reference.

### `WARNING unknown media files: [...]`

This message accumulates all files referred to in the database, which were not
found in the CDSTAR database.

*How do I fix this?*

Run the `check` subcommand to get a list of all `missing files`.  See the
respective section above for more information.

### `WARNING could not process links: missing property: link_regex`

Link processing requires the definition of two `md.json` properties:
`process_links_in_markers` and `link_regex`.  If the former is empty or missing,
the script just assumes that link processing is not desired and moves on.
However, if `process_links_in_markers` is present, but no `link_regex` was
defined, the script indicates that using this error message.

*How do I fix this?*

Add the appropriate `link_regex` property to the `md.json` file.

### `ERROR <table name>: Could not add column: [...]`

This message occurs, when the CLDF database is initialised.  It means that the
script was unable to add a table column to a table in the database.  This can
be caused for instance, by an invalid column name (containing spaces etc.).
Read the reason at the end of the message for more information.

*How do I fix this?*

Edit the `md.json`.  The exact fix depends on the actual error message.

### `ERROR <table name>: row dropped due to missing required fields: [...]`

The CLDF specification marks several table columns as `required`, meaning their
value must not be empty.  If it *is* empty, the entire row is dropped from the
table.

*How do I fix this?*

Below the error message you find a list of the fields, that *are* defined.  Use
this information to find the original entry in the `db.sfm` and/or
`examples.sfm`.  Also, you might find it helpful to re-run the `check`
subcommand, as it catches common cases such as `\de` or `\ps`.

### `ERROR \lx <headword>: entry dropped since there aren't any senses referring to it`

Every entry needs at least one sense, otherwise it is dropped.  Note that there
might be senses that were removed due to previous errors.

*How do I fix this?*

Look for the original entry and fix it.  Also, run the `check` subcommand and
look for entries with missing `\de` fields.

### CLDF validation errors

After the CLDF dataset is created the processing script validates the created
CLDF to find problems that might have slipped through the processing above.  Any
warnings produced by the validator are appended at the bottom of the `cldf.log`
file.  These messages follow the following shape:

    WARNING/ERROR <table file>:<lineno> <message>


`glosses.log`
-------------

The `glosses.log` file is created, when glosses are provided in a separate
`glosses.flextext` file.  The file may contain errors from the parsing process,
although *technically*, these that should never occur in FLEx exports (unless
FLEx decides to randomly change their output format).  Other than that there are
a few possible messages:

### `ERROR md.json does not specify 'gloss_ref' marker`

The `gloss_ref` property specifies the SFM marker, FLEx uses in examples to
store the reference to its gloss.  Because FLEx defines a different marker for
every dictionary – which is outside of the control of the user – there is no
default value to this property.  As a result, glosses cannot be processed if the
`gloss_ref` property is missing.

*How do I fix it?*

Look through the examples in the `db.sfm` and find out, which marker contains
a reference to the gloss and edit your `md.json` accordingly.

### `ERROR Gloss '\\?? <gloss id> not found (ex: <example id>)`

This means that an example refers to a gloss, which was not found in the
`glosses.flextext`.  Since the association between the two is done
automatically,

*How do I fix it?*

1. Double-check the `md.json`, if you have set the right `gloss_ref` marker.
   FLEx defines like a dozen different markers named `\z...`, so it is easy to
   mix them up.
2. The `db.sfm` and the `glosses.flextext` files might be out of sync.  Have
   FLEx re-export both files.
3. If the reference is truly wrong, fix it from within FLEx and re-export.
