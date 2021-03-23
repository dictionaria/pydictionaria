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

Run the installer and click "Install Now".  This does two things:

 1. Install a launcher called `py` and make it accessible for all users
 2. Install Python 3 into your user account, where `py` can find it

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
have Python 3 installed.  `pydictionaria` will not work with Python 2.  Look for
package names with explicit version numbers such as `python3` or `python3.7`,
since versionless names like `python` might point to Python 2 on some
distributions.

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


Installing `pydictionaria`
--------------------------

The latest release of pydictionaria can be installed using `pip`:

    pip install pydictionaria

### Test your installation

Run the following command:

    cldfbench -h

This shows the help page for `cldfbench`.  If `pydictionaria` was installed

If the installation is successful, this should show a message detailing all the
options supported by `pydictionaria`.

### Keeping `pydictionaria` up-to-date

Use `git pull` to download the newest version of the source code and re-run the
installation command.


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
