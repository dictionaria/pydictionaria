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
2. Otherwise manually edit the entry in the `db.sfm`.

### `ERROR \lx <headword>: multiple \de but not matching \sn`

This message means that there is a discrepancy between the number of `\sn`
markers and the number of `\de` markers.  This could have multiple causes:

1. A sense is missing a `\de` marker
2. There are multiple `\de` markers within the same sense
3. There is an additional `\de` marker before the first sense

*How do I fix this?*

Manually edit the entry in the `db.sfm`.

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
numbers.  Also make sure there is a single space ` ` between a lemma and its
homonym number.

### `ERROR \lx <headword>: invalid bibkey: \bibref [...]`

This message indicates that the `\bibref` marker of an entry contains a reference
to a bibliography entry not found in the `sources.bib`.

*How do I fix this?*

1. Check the entry for types.
2. Add any missing bibliography entries to you `sources.bib`


`examples.log`
--------------

### `# incomplete example in lx <headword> - missing [...]` TODO

### `# cannot merge [...] and [...]` TODO


`cldf.log`
----------

### `WARNING No CLDF column defined for markers: [...]` TODO

### `ERROR \lx <headword>: entry dropped due to missing \ps marker` TODO

### `ERROR \lx <headword>: entry dropped due to empty \ps marker` TODO

### `ERROR \lx <headword>: entry dropped due to conflicting \ps markers: [...]` TODO

### `WARNING senses refer to non-existent examples: [...]` TODO

### `WARNING unknown media files: [...]` TODO

### `WARNING could not process links: missing property: link_regex` TODO

### `ERROR <table name>: Could not add column: [...]` TODO

### `ERROR <table name>: row dropped due to missing required fields: [...]` TODO

### `ERROR <entry id>: entry dropped since there aren't any senses referring to it` TODO

TODO messages in dataset validation – is there a place I can tell people to go to?


`glosses.log` TODO
-------------
