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


Brief introduction to the Command-line
--------------------------------------

Using the command-line is a very easy and straight-forward way of interacting
with a computer.  However, for whatever reason the mere thought of using it
makes people feel uneasy or intimidated.

*But… I don't even know how to program!*  You don't need to.  The command-line
is used for *running* programs, not for making them.

*But… I don't know all the commands!*  Nobody does.  People working on the
command-line usually only remember the commands they use regularly.  For some,
this means they've memorised hundreds of commands over the years; other get by
with just two or three, including `cd`.  Yet others just have a list of commands
written down in a text file or a sheet of paper on their desk.  Also, there's
the internet -- an endless resource for looking up commands or asking for help.

*But… it looks so much harder to use than Graphical programs.*  It really isn't.
Typing a command is not really that different from looking through a menu to
click the right icon.  Changing configuration through a text file is not really
that more difficult than spending hours clicking through dialog boxes to find
the right box to tick.  It just needs some getting used to.  If anything, the
strictly text-based nature of the command-line makes the user experience more
consistent across different programs -- there are only so many ways a program
can say 'file not found'.

TODO revise

### Opening a terminal window

#### Windows

On Windows there are several options, e.g.:

 * Use the search field in your start menu and search for the term `Command
   Prompt`.
 * Use the `Run` dialog (e.g. by pressing `Windows Key + R`) to run the `cmd`
   command
 * Right click on the Start button or press `Windows Key + X` to open the "Power
   User Menu" and click `Command prompt` (or `Powershell`, depending on your
   system setup)
 * Manually navigate through your start menu looking for the `Command prompt`
   menu item.  The exact place differs across the different versions of Windows,
   but it is usually in a folder called `Accessories`, `System Utilities` or the
   like.

Note that at the time of writing this, Windows ships with two terminal
applications: `Command Prompt` (a.k.a. `cmd.exe`) and `Powershell`.  For the
purpose of this tutorial, either is fine.

#### GNU/Linux

Depending of your distribution, there is usually one or more terminal emulator
installed.  They are usually in the `System` category of your menu and have the
term 'terminal' or 'console' in their name (e.g. `GNOME Terminal`, `Konsole`,
`XTerm`, etc.).

#### macOS

There is a program called `Terminal` installed on your system.  Find it in the
`Utilities` folder, or search for it using Spotlight.

### The command-line shell

The *shell* is the program, that reads and interprets commands entered by the
user.  The workflow on the command-line is as follows:

 1. Wait for the user to enter a command
 2. Run the command
 3. Show the output of the command
 4. Rinse, repeat

Windows currently comes with two command-line shells, `cmd.exe` and
`PowerShell`, while on Unix-like systems there are countless options (`bash`,
`csh`, `fish`, to name a few).  However, at the end of the day they all work
pretty much the same way – so, when in doubt, stick with the default.

### The prompt

The *prompt* is a piece of text that signals to the user that the shell is
waiting for a command.  In many cases the prompt provides some context about the
current environment.  Many shells also end the prompt with some special
character such as `$`, `%`, or `>`.

Note that on Unix-like systems, a shell prompt ending on a hash symbol `#`
usually signifies that the current shell is running  with admin privileges.  Be
careful, when executing commands as an admin, since this may damage your system.
It is highly recommended to run shell commands as a regular user, whenever
possible.

Example 1:  The prompt of Windows' `cmd.exe` shows the current working directory
(see below) and a greater-than sign `>`.

    C:\Users\Bob\Desktop>

Example 2:  On Ubuntu, the prompt of `bash`, the default shell, shows the user
name, the computer name, the current working directory, and a dollar sign `$`.

    bob@work-pc:~/Desktop$

### Running a program

A command consists of the name of the command or program you want to run and
a list of arguments, which provide additional information for that command.
The name and the individual arguments are separated from each other using
spaces:

    myprogram arg1 arg2

If a command or argument contains spaces itself, put it into quotation marks:

    myprogram arg1 "argument 2"

### The working directory

Every program is running in a *working directory*.  This means that every file
or folder name that is not an absolute path is interpreted relative to the
working directory.  Usually the shell shows the current working directory within
the command prompt.  However it is also possible to show the working directory
using the `cd` command on Windows:

    C:\Users\Bob> cd
    C:\Users\Bob
    C:\Users\Bob>

Or the `pwd` command on Unix-like systems:

    bob@work-pc:~$ pwd
    /home/bob
    bob@work-pc:~$

The working directory can be changed using the `cd` ('change directory')
command.  The following command changes the directory to `C:\Users\Bob`.

    C:\Users\Bob> cd "C:\Program Files"
    C:\Program Files>

The `cd` command itself is run from the current working directory, which means
it is possible to change to a directory relative to the current directory.  The
following command changes to the directory

    C:\Users\Bob> cd Desktop
    C:\Users\Bob\Desktop>

There are two special folder names: single period `.`, which refers to the
current directory, and `..` which refers to the parent directory.  The latter
can be used to move up the directory tree:

    C:\Users\Bob\Desktop> cd ..\Documents
    C:\Users\Bob\Documents> cd ..
    C:\Users\Bob

Additionally, on Unix-like systems there is the special folder name tilde `~` to
refer to the current user's home directory:

    bob@work-pc:~$ pwd
    /home/bob
    bob@work-pc:~$ cd /etc
    bob@work-pc:/etc$ pwd
    /etc
    bob@work-pc:/etc$ cd ~/Desktop
    bob@work-pc:~/Desktop$ pwd
    /home/bob/Desktop


Brief introduction to Git
-------------------------


### What is what?

 * git: A version control system (VCS), which allows collaborators to manage and
   keep track of changes to a project.

 * git repository (*repo* for short): A repository holds all the project files,
   and a record of all changes.

 * GitHub: A website run by Microsoft, which hosts git repositories and provides
   means to collaborators for communication.

### Installation

The git website provides [detailed instructions](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
on how to install git for all major operating systems.

### TODO Cloning a repository

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

### Keeping a repository up-to-date

To download all new changes from the original repository, `cd` to the folder
containing the repository and run the `pull` subcommand:

    git pull

This will download all changes from the original remote repository.


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
