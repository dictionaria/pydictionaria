Brief introduction to the Command-line
======================================

Using the command-line is a very easy and straight-forward way of interacting
with a computer.  However, for whatever reason people feel uneasy or
intimidated, when confronted with command-line interfaces.  This document aims
to alleviate this uneasiness by introducing the basic concepts at work.


Frequently Uttered Concerns
---------------------------

### I don't even know how to program!

You don't need to.  The command-line is used for *running* programs, not for
making them.

### I don't know all the commands!

Nobody does.  People working on the command-line usually only remember the
commands they use regularly.  For some, this means they've memorised hundreds of
commands over the years; others get by with just two or three, including `cd`.
Yet others just have a list of commands written down in a text file or a sheet
of paper on their desk.  Also, there's the internet -- an endless resource for
looking up commands or asking for help.

### I don't want to break my computer!

Command-line programs aren't generally any more or less dangerous than their
graphical counterparts.  The biggest concern might be data loss, since
command-line programs tend to provide fewer save guards, when it comes to
changing or deleting files.

In general, follow the following guide lines:

 - Proof-read any command before hitting `Enter`
 - Back up your data regularly
 - Don't run programs with admin privileges
 - Don't copy-paste commands from the internet.  Always look up, what part of
   a command does what and then type the command by hand.


What is what?
-------------

### The command-line shell

The *shell* is the program, that reads and interprets commands entered by the
user.  The workflow on the command-line is as follows:

 1. Wait for the user to enter a command
 2. Run the command
 3. Show the output of the command
 4. Rinse, repeat

Windows currently comes with two command-line shells, `cmd.exe` and
`PowerShell`, while on Unix-like systems there are countless options (`bash`,
`csh`, `fish`, to name a few).  However, at the end of the day they're all doing
the same thing – so, when in doubt, stick with the default.

### The prompt

The *prompt* is a piece of text that signals to the user that the shell is
waiting for a command.  In many cases the prompt provides some context about the
current environment.  Many shells also end the prompt with some special
character such as `$`, `%`, or `>`.

Note that on Unix-like systems, a shell prompt ending on a hash symbol `#`
usually signifies that the current shell is running  with admin privileges.  Be
careful when executing commands as an administrator!  You might damage your
system.  It is highly recommended to run shell commands (or any program for that
matter) as a regular user, whenever possible.

Example 1:  The prompt of Windows' `cmd.exe` shows the current working directory
(see below) and a greater-than sign `>`.

    C:\Users\Bob\Desktop>

Example 2:  On Ubuntu, the prompt of `bash`, the default shell, shows the user
name, the computer name, the current working directory, and a dollar sign `$`.

    bob@work-pc:~/Desktop$


Opening a terminal
------------------

### Windows

On Windows there are several options, e.g.:

 - Use the search field in your start menu and search for the term `Command
   Prompt`.
 - Use the `Run` dialog (e.g. by pressing `Windows Key + R`) to run the `cmd`
   command
 - Right click on the Start button or press `Windows Key + X` to open the "Power
   User Menu" and click `Command prompt` (or `Powershell`, depending on your
   system setup)
 - Manually navigate through your start menu looking for the `Command prompt`
   menu item.  The exact place differs across the different versions of Windows,
   but it is usually in a folder called `Accessories`, `System Utilities` or the
   like.

Note that at the time of writing this, Windows ships with two terminal
applications: `Command Prompt` (a.k.a. `cmd.exe`) and `Powershell`.  For the
purpose of this tutorial, either is fine.

### GNU/Linux

Depending of your distribution, there is usually one or more terminal emulator
installed.  They are usually in the `System` category of your menu and have the
term 'terminal' or 'console' in their name (e.g. `GNOME Terminal`, `Konsole`,
`XTerm`, etc.).

### macOS

There is a program called `Terminal` installed on your system.  Find it in the
`Utilities` folder, or search for it using Spotlight.


Running a command
-----------------

A command consists of the name of the command or program you want to run and
a list of arguments, which provide additional information for that command.
The name and the individual arguments are separated from each other using
spaces:

    myprogram arg1 arg2

If a command or argument contains spaces itself, put it into quotation marks:

    myprogram arg1 "argument 2"


The working directory
---------------------

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

Wildcard characters
-------------------

Sometimes you want to run a program on multiple files, but typing out every
file name is tedious and error-prone.  For this one can use wildcard characters

TODO

The two most common wildcard characters are the question mark `?` and the
asterisk `*`:

 - `?` is a placeholder for a single unkown character.
 - `*` is a placeholder for any number of characters (or none).

Example 1:  The following command moves files like `text-01.txt`, `text-02.txt`,
`text-xy.txt` into the folder `backup` (on Windows):

    move text-??.txt backup

Example 2:  The following command deletes every file ending with the extension
`.exe` from the current working directory (on Windows):

    del *.exe

Note: Be extra careful with commands that delete or change files.  Always
double-check that the wildcard does not apply to any files you don't want to
affect.  The command-line does not have an undo button nor a trash bin, so any
file you accidentally delete will be gone forever.

Also note: On Unix-like systems, wildcards are usually resolved by the shell,
before a program is run.  On Windows, wildcards are resolved by the programs
themselves.  Although this difference rarely matters in practice, it is
something to be aware of.


Getting help TODO
------------


Some useful commands
--------------------

This section is just a small cheat sheet for some common commands, separated by
operating system (or rather by Windows vs. not Windows, since Unix-like
operating systems tend to use the same names for basic programs).

### Windows

Change the current working directory:

    cd <foldername>

Output the name of the current working directory:

    cd

Show the contents of the current working directory:

    dir

Rename a file:

    move <filename> <new filename>

Move a file to a different folder:

    move <filename> <foldername>

Copy a file (does not work with folders):

    copy <filename> <destination>

Create a new folder:

    md <foldername>

Delete a file:

    del <filename>

Delete an empty folder:

    rd <foldername>

### Unix-like systems

Change the current working directory:

    cd <foldername>

Output the name of the current working directory:

    pwd

Show the contents of the current working directory:

    ls

Rename a file:

    mv <filename> <new filename>

Move a file to a different folder:

    mv <filename> <foldername>

Copy a file (does not work with folders):

    cp <filename> <destination>

Copy an entire folder recursively:

    cp -r <foldername> <destination>

Create a new folder:

    mkdir <foldername>

Delete a file:

    rm <filename>

Delete an empty folder:

    rmdir <foldername>
