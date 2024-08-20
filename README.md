pydictionaria
=============

Companion library to the [Dictionaria][dictionaria] journal.

[dictionaria]: https://dictionaria.clld.org

## Set up

Pydictionaria can be installed using pip:

    $ pip install pydictionaria

Refer to [`docs/getting-started.md`](docs/getting-started.md) for more
details.

## Basic usage

*pydictionaria* is meant to be used in conjunction with [cldfench][cldfbench].
You can set up a *pydictionaria* project using the provided project template:

    $ cldfbench new --template=dictionaria

For a more thorough description of working with a *pydictionaria* project, refer
to [`docs/submission-workflow.md`](docs/submission-workflow.md).

## Major version updates

### Breaking changes from pydictionaria 1.x to 2.x

Data is not stored in a central repository anymore.  Individual data
repositories are now managed using [cldfbench][cldfbench].  pydictionaria
provides a cldfbench template for creating new projects:

    $ cldfbench new --template=dictionaria

[cldfbench]: https://pypi.org/project/cldfbench/
