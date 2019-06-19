Brief introduction to Git
=========================


What is this `git` thing?
-------------------------

`git` is a distributed version control system, which allows collaborators to
manage and keep track of changes to the project.  Dictionaria uses `git` to
manage both the source code of its associated programs and the actual
dictionaray data.  This document gives a brief introduction to the concepts at
work with git.

All the examples here use `git`'s standard command-line interface.  Note that
there are several [graphical tools][git-guis], as well as plug-ins that
integrate git directly into many popular text editors/development environments.
However, at the end of the day they're mostly just colourful buttons around the
same core principles described in this document.

[git-guis]: https://git-scm.com/downloads/guis

If you do not know how to work on the command-line, read the accompanying file
`intro-commandline.md` for a brief introduction.


Installation
------------

The git website provides [detailed instructions][git-inst] on how to install git
for all major operating systems.

[git-inst]: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git


What is `git`?
--------------

`git` is a *version control system* (VCS).  As the name suggests it is
a *system* that *controls* different *versions* of a project.  This actually
means two things:

1. Different versions over time:  VCS's keep a record of all changes made to
   a project and are able to roll back and forth between the different versions.

2. Different versions in parallel:  VCS's offer a mechanic called *branches*,
   which allow multiple versions of the same project to exists next to each
   other, each with their own history.  These branches can also merge changes
   from other branches to keep the whole project in sync.

`git` is also a *distributed* VCS.  This means that the project is not stored in
*one* singular place; instead, every collaborator keeps an independent copy of
the project on their computer.  And everyone *pulls* the changes to the project
from each other – in theory, at least.

In practice people instead create a central repository somewhere on-line, which
serves as *the* copy of the project; the one that everybody pushes their changes
to and the one that everybody pulls from, if they want to get the most recent
version of the project.  Some bigger projects host their `git` repositories on
their own website, for example the [Linux kernel][linux-repos] or the [GNU
project][gnu-savannah].  Many smaller projects on the other hand rely on
third-party companies that offer to host `git` repositories, such as
[Github][github] or Atlassian's [Bitbucket][bitbucket].  At the time of writing
all of Dictionaria's code and data reside on Github.

[linux-repos]: https://git.kernel.org
[gnu-savannah]: https://savannah.gnu.org
[github]: https://github.com
[bitbucket]: https://bitbucket.org

Note that remote `git` repositories do not need to by open to the public.  For
instance, while the Python code behind Dictionaria is [out in the
open][pydictionaria] under a [free software license][apache2], the repository
with all the unpublished data can only be accessed by project members.

[pydictionaria]: https://github.com/dictionaria/pydictionaria
[apache2]: https://github.com/dictionaria/pydictionaria/blob/master/LICENSE


TODO Cloning a repository
-------------------------

Because git is a *distributed* VCS every collaborator contains a full copy
('clone') of the repository on their computer.

    git clone <url>

This will create a new folder with the same name as the repo in the current
working directory.  This folder will contain a complete copy of the repository.

    git clone <url> <folder name>

This will do the same, but specify a different name for the folder.  Remember to
put folder names in "quotation marks", if they contain spaces.

Example:  Cloning the `pydictionaria` repo.

    git clone https://github.com/dictionaria/pydictionaria


Keeping a repository up-to-date
-------------------------------

To download all new changes from the original repository, `cd` to the folder
containing the repository and run the `pull` subcommand:

    git pull

This will download all changes from the original remote repository.
