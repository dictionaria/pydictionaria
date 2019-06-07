Brief introduction to Git
=========================


What is what?
-------------

 - git: A version control system (VCS), which allows collaborators to manage and
   keep track of changes to a project.

 - git repository (*repo* for short): A repository holds all the project files,
   and a record of all changes.

 - GitHub: A website run by Microsoft, which hosts git repositories and provides
   means to collaborators for communication.


Installation
------------

The git website provides [detailed instructions](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
on how to install git for all major operating systems.


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
