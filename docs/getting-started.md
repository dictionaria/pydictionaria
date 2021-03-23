Getting Started
===============


Prerequisites
-------------

 - If you do not know how to use the command-line read the file
   `intro-commandline.md`
 - If you do not know the ins and outs of `git`, read the file `intro-git.md`


Installing a text editor
------------------------

Submissions for dictionaria all come in some form of plain-text, be it an SFM
database or the `csv` and `json` files used by the CLDF format.  Because of this
it is highly recommended to use a good text editor.  This is especially true for
users of Microsoft Windows, since Notepad is… lacking in a few areas.

Here is a quick selection of popular free and open source text editors:

 - [Notepad++][notepadpp] by Don Ho (Windows only)
 - [Atom][atom] by Github
 - [Vim][vim] by Bram Moolenaar
 - [GNU Emacs][emacs] by the Free Software Foundation

[notepadpp]: https://notepad-plus-plus.org
[atom]: https://atom.io
[vim]: https://www.vim.org
[emacs]: https://www.gnu.org/software/emacs


Installing Python 3
-------------------

### Installation (Windows)

Go to [the download page][python-dl] on the Python website.  From there, go to
the "Stable Releases" section and download the installer for the latest version
of Python 3.  `pydictionaria` will *not* work with Python 2.

[python-dl]: https://www.python.org/downloads/windows/

However, note that Python 2 and 3 can coexist on the same system, meaning it is
not necessary to uninstall Python 2, if it is already there.

Run the installer, check the box that adds Python to your `PATH`, and click
"Install Now".  This does three things:

 1. Install a launcher called `py` and make it accessible for all users
 2. Install Python 3 into your user account, where `py` can find it
 3. Update your `PATH` variable, so you can run Python scripts like `cldfbench`
    directly from the command-line

To check, whether the installation was successful, open a command prompt and
run:

    py --version

If Python is installed properly, the command will show a short message
containing the version number.  If the number starts with 2 (e.g. `2.7`), then
the launcher starts Python 2 by default.  To make the launcher run Python 3, add
the option `-3` to the `py` command; like so:

    py -3 --version

### Installation (GNU/Linux)

In most (if not all) distributions, you can use the package managers to install
Python from the official software repositories.  However do make sure that you
have Python 3 installed.  `pydictionaria` will *not* work with Python 2.  Look
for package names with explicit version numbers such as `python3` or
`python3.7`, since versionless names like `python` might point to Python 2 on
some distributions.

Note that Python 2 and 3 can coexist on the same system, meaning it is not
necessary do uninstall Python 2, if it is already there (in fact, depending on
your system configuration uninstalling Python 2 might be flat-out impossible).

Example:  To install Python 3 on Ubuntu or other Debian-based systems, run:

    sudo apt install python3

To check, whether the installation was successful, run:

    python3 --version

If Python is installed properly, the command will show a short message
containing the version number.

### TODO Installation (macOS)


### Setting Python's `PATH` manually after the installation

If your Python installation did not add Python scripts to your `PATH`, you can
do so follow the corresponding section in
[docs/intro-commandline.md](docs/intro-commandline.md).  The exact path you need
to add depends on your operating system.

On Linux, Python scripts are installed to `$HOME/.local/bin`.

On Windows, the path you need is
`%USERPROFILE%\AppData\Local\Python\Python<VERSION>\Scripts`, where `<VERSION>`
needs to be replaced with Python's major and minor version, without the period.

For example, if you are using Python 3.8 (or 3.8.1, 3.8.2, etc.), the folder is
called:

    %USERPROFILE%\AppData\Local\Python\Python38\Scripts

However, if you are using Python 3.9 (or 3.9.1, 3.9.2, etc.), the folder is
called:

    %USERPROFILE%\AppData\Local\Python\Python39\Scripts

TODO macos?

If you still get ‘command not found’ errors after setting the path and
restarting your terminals, then you can always fall back to adding python
explicitly to the command.

For instance, if you want to run `pip install pydictionaria` this way on
Unix-like operating systems, you can prepend `python3 -m ` to your command, like
so:

    python3 -m pip install pydictionaria

On Windows, add `py -m ` instead:

    py -m pip install pydictionaria


Installing `pydictionaria`
--------------------------

The latest release of pydictionaria can be installed using `pip`:

    pip install pydictionaria

### Test your installation

Run the following command:

    cldfbench -h

This shows the help page for `cldfbench`, including a full list of supported
subcommands.  If `pydictionaria` was installed successfully, this list should
include subcommands starting with `dictionaria.` (e.g. `dictionaria.release`).

### Keeping `pydictionaria` up-to-date

You can update `pydictionaria` to the latest version using `pip`.

    pip install --upgrade pydictionaria


Installing `virtualenv`
-----------------------

It is also recommended to place each CLDF bench into its own so-called *Virtual
Environment*.  This means that all python packages used for processing a CLDF
bench will be installed locally in the CLDF bench's folder.  This has two major
advantages:

 1. You avoid unnecessary clutter in your system-wide Python installation
 2. You avoid problems with CLDF benches or other Python projects that require
    conflicting versions of the same package
 3. If something happens to mess up your Python installation, it will only break
    the one inside the virtual environment.  This doesn't happen all that often,
    but when it does, it is nice to be able to just delete the environment and
    start over.

For that you need the `virtualenv` program.  If your Python installation does
not ship with a version of `virtualenv`, you can also install it using `pip`:

    pip install virtualenv

[pydictionaria]: https://github.com/dictionaria/pydictionaria



Troubleshooting
---------------

### `pydictionaria`'s installation failed: `[Errno 13] Permission denied`

This error message occurs, when the installation process tries to install
`pydictionaria` system-wide, but lacks the necessary admin privileges to make
changes to your system.

You can tell the installation to install `pydictionaria` locally for your user
account by adding the `--user` option to the command-line, i.e.:

    pip install --user pydictionaria

Note that there is no real reason for `pydictionaria` to be installed
system-wide (also, installing random programs from the internet with admin
privileges is generally not a particularly safe idea).  If, however, for some
reason, you *really, really* have to, you can do the following:

On Windows, open a `Command Prompt` with admin privileges (right-click → `Run as
Administrator`) and run the installation from this command prompt.

On Unix-like operating systems, you can usually prepend `sudo` to a command to
grant 'super user' privileges to it.  For security reasons, `sudo` will ask you
for your user password before running the actual command.

    sudo pip install pydictionaria

### `pydictionaria`'s installation failed: `Could not find a version that satisfies the requirement […]`

The most likely explanation for this is, that `pip` is running on an older
version of Python.  The tools surrounding CLDF all require at least Python 3.6.
Run `py --version` or `python3 --version` 

Some systems have Python 2 and Python 3 installed alongside each other.  More
and more operating systems set Python 3 as the default installation, but
occasionally you'll find that `pip` runs on Python 2 instead.  If that is the
case, you can run the Python 3 version of `pip` explicitly and install
`pydictionaria` as follows.

On Windows:

    py -3 -m pip install pydictionaria

On Unix-like operating systems:

    pip3 install pydictionaria

Or:

    python3 -m pip install pydictionaria

### Running `cldfbench` shows the message `command not found`, even though the installation finished successfully

If your shell is unable to find `dictionaria`, it might mean that you need to add
its installation folder to your `PATH` (read the file `intro-commandline.md` if
you don't know how to add folders to your `PATH`).

On Windows Python puts its scripts in the following folder:

    %USERPROFILE%\AppData\Local\Programs\Python37\Scripts

Be sure to replace the version number in the `Python37` folder with the right
version for your Python installation (e.g. `Python38` for Python 3.8):

On Unix-like systems Python puts its scripts in the following folder:

    $HOME/.local/bin
