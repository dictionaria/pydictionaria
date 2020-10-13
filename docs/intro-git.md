Brief introduction to Git
=========================


Introduction
------------

`git` is a distributed version control system, which allows collaborators to
manage and keep track of changes to a project.  Dictionaria uses `git` to manage
both the source code of its associated programs and the actual dictionary data.
This document gives a brief introduction to the concepts at work with git.

All the examples use `git`'s standard command-line interface.  Note that there
are several [graphical tools][git-guis], as well as plug-ins that integrate git
directly into many popular text editors/development environments.  However, at
the end of the day they're mostly just colourful buttons around the same core
principles described here.

[git-guis]: https://git-scm.com/downloads/guis

If you do not know how to work on the command-line, read the accompanying file
`intro-commandline.md` for a brief introduction.


Installation
------------

The git website provides [detailed instructions][git-inst] on how to install git
for all major operating systems.

[git-inst]: https://git-scm.com/book/en/v2/Getting-Started-Installing-Git


What is this `git` thing?
-------------------------

`git` is a *version control system* (VCS).  As the name suggests it is
a *system* that *controls* different *versions* of a project.  This actually
means two things:

1. Different versions over time:  VCS's keep a record of all changes made to
   a project and are able to roll back and forth between the different versions.

2. Different versions in parallel:  VCS's offer a mechanic called *branches*,
   which allow multiple versions of the same project to exist next to each
   other, each with their own history.  These branches can also merge changes from
   other branches to keep the whole project in sync.

`git` is also a *distributed* VCS.  This means that the project is not stored in
*one* singular place; instead, every collaborator keeps an independent copy of
the project on their computer.  And everyone *pulls* the changes to the project
from each other – in theory, at least.

In practice people often create a central repository somewhere on-line, which
serves as *the* copy of the project; the one that everybody pushes their changes
to and the one that everybody pulls from, if they want to get the most recent
version of the project.

Some bigger projects host their `git` repositories on their own website, for
example the [Linux kernel][linux-repos] or the [GNU project][gnu-savannah].
Many smaller projects on the other hand rely on third-party companies that offer
to host `git` repositories, such as [Github][github] or Atlassian's
[Bitbucket][bitbucket].  At the time of writing all of Dictionaria's code and
data reside on Github.

[linux-repos]: https://git.kernel.org
[gnu-savannah]: https://savannah.gnu.org
[github]: https://github.com
[bitbucket]: https://bitbucket.org

Note that remote `git` repositories do not need to be open to the public.  For
instance, while the Python code behind Dictionaria is [out in the
open][pydictionaria] under a [free software license][apache2], the repository
with all the unpublished data can only be accessed by project members.

[pydictionaria]: https://github.com/dictionaria/pydictionaria
[apache2]: https://github.com/dictionaria/pydictionaria/blob/master/LICENSE


Cloning a repository
--------------------

To receive your very own copy of a project, you need to create a ‘clone’ of the
remote repository on your computer.  To do this you can use the `clone`
subcommand of `git`:

    git clone <url>

This will create a new folder in the current working directory and fills it with
the most recent project files.  Note that this will also clone the entire
history of every branch of the project in one go, so if the project as a very
long and active history, this might take a while.

If you want a different name for your project folder, add it as an additional
argument to the `git` command:

    git clone <url> <foldername>

Example:  Cloning the `pydictionaria` repo.

    git clone https://github.com/dictionaria/pydictionaria


Exploring a project
-------------------

`git` knows everything about your project and is willing to share this
information with you.  To look at the current state of your project, run the
`status` subcommand:

    git status

Note that almost every `git` command aside from `clone` is run from within the
project folder – so, unless stated otherwise, `cd` into your project folder
before running any of the `git` commands.

If you just cloned a repository the output will most likely look something like
this:

    On branch master
    Your branch is up to date with 'origin/master'

    nothing to commit, working tree clean

Now what does any of this mean?

 - `On branch master`:
   We'll worry about branches later.  For now, just remember that `master` is
   usually the name used for the ‘main branch’ of the project.

 - `Your branch is up to date with 'origin/master'`:
   This means that there are no new changes to the remote repository *that this
   working copy knows of*.  This is important to remember:  The `status`
   subcommand does not actually connect to the internet and fetch any new
   changes – there is a separate command for that.

 - `nothing to commit, working tree clean`:
   This means, there are no changes to any of the project's files.

Another useful command is the `log` subcommand:

    git log

As the name suggests this command shows a list of all changes made to the
project starting at the most recent.  It also contains information about *who*
made the change and *when*.


Staying in sync with the remote repository
------------------------------------------

As mentioned before, `git` does not pull any changes from the remote repository
unless you specifically tell it to.  To do so run the `fetch` subcommand:

    git fetch

If you run `git status` after this, it will tell you how many commits were added
to the remote repository (a ‘commit’ is VCS-talk for a single change made to the
project):

    On branch master
    Your branch is behind 'origin/master' by 4 commits, and can be fast-forwarded.
      (use "git pull" to update your local branch)
    [...]

As this message suggests, none of the changes on the remote repositories have
actually been applied to your working copy, yet.  To do so, run the `merge`
subcommand without any further arguments:

    git merge

Since these two commands are commonly used together, there is also a shorthand:
the `pull` subcommand.  `pull` fetches the current state of the remote
repository and merges all changes to the current branch.  In practice people
tend to use `pull` almost exclusively and only really bother with `fetch` and
`merge` on some rare occasions.  However, it is still a good idea to remember
that getting changes from a remote repository is really a two-step process.

    git pull


Telling `git` about changes to the project
------------------------------------------


TODO staging and committing
 * what is the staging area
 * adding stuff
 * resetting the staging area
 * commits and commit messages

TODO what to do when vi pops up
TODO diffs?
TODO pushing
TODO branches
TODO merging
TODO merge conflicts
TODO pull requests
