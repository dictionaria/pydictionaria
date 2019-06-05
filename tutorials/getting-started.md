Getting Started
===============


Installing Python 3
-------------------

### Installation (Windows)

Go to [the download page](https://www.python.org/downloads/windows/) of the
Python website.  From there, go to the "Stable Releases" section and download
the installer for the latest version of Python 3.  `pydictionaria` will *not*
work with Python 2.

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
your system configuration uninstalling Python 2 might flat-out be impossible).

Example:  To install Python 3 on Ubuntu or other Debian-based systems, run:

    sudo apt install python3

To check, whether the installation was successful, run:

    python3 --version

If Python is installed properly, the command will show a short message
containing the version number.

### TODO Installation (macOS)


Installing `pydictionaria`
--------------------------

### Clone the repository

Clone the [pydictionaria repository](https://github.com/dictionaria/pydictionaria)
to a folder of your choice.

### Install `pydictionaria`

To install `pydictionaria`, `cd` into the folder containing the git repository.

    py setup.py install

on Windows, or

    python3 setup.py install

on Unix-like systems.

### Test your installation

Run the following command:

    dictionaria -h

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
account by adding the `--user` option to the end of the command-line, i.e.:

    py setup.py install --user

for Windows, and

    python3 setup.py install --user

for Unix-like operating systems.

Note that there is no real reason for `pydictionaria` to be installed
system-wide (also, installing random programs from the internet with admin
privileges is generally not a particularly safe idea).  If, however, for some
reason, you *really, really* have to, you can do the following:

On Windows, open a `Command Prompt` with admin privileges (right-click → `Run as
Administrator`) and run the installation from this command prompt.

On Unix-like operating systems, you can usually prepend `sudo` to a command to
grant 'super user' privileges to it.  For security reasons, `sudo` will ask you
for your user password before running the actual command.

    sudo python3 setup.py install

### TODO Running `dictionaria` shows the message `command not found`, even though the installation finished successfully

note: tell about $PATH
