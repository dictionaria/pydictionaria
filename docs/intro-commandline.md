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
of paper on their desk.  Also, there's the internet – an endless resource for
looking up commands or asking for help.

### I don't want to break my computer!

Command-line programs aren't generally any more or less dangerous than their
graphical counterparts.  The biggest concern might be data loss, since
command-line programs tend to provide fewer safeguards, when it comes to
changing or deleting files.

In general, follow the following guide lines:

 - Proof-read any command before hitting `Enter`
 - Back up your data regularly
 - Don't run programs with admin privileges
 - Don't copy-paste commands from the internet.  Always look up, what part of
   a command does what and then type the command by hand.


Operating System
----------------

Note that a lot of the details depend on the operating system you are using.
Luckily a lot of operating systems (such as GNU/Linux, BSD, macOS, etc.) are
either heavily inspired by or direct descendants of the Unix operating system,
which means they share a lot of the same commands.  The most notable exception
to this rule is Microsoft Windows.

Long story short, this document splits most operating-system-dependent advice
into two categories:

 1. Microsoft Windows
 2. Unix-like operating systems


Starting the command-line
-------------------------

### Windows

On Windows there are several options, e.g.:

 - Use the search field in your start menu and search for the term `Command
   Prompt`.
 - Use the `Run` dialog (e.g. by pressing `Windows Key + R`) to run the `cmd`
   command
 - Right click on the Start button or press `Windows Key + X` to open the ‘Power
   User Menu’ and click `Command prompt` (or `Powershell`, depending on your
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
words ‘terminal’ or ‘console’ somewhere in their name (e.g. `GNOME Terminal`,
`Konsole`, `XTerm`, etc.).

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

Note:  Make sure you use the proper plain-text quotation mark `"` symbol.
Anything else, like forward- or backticks, or typographical quotation marks (“”
or ‘’) are not considered quotation marks as far as the command-line is
concerned.  The only exceptions is that Unix-like systems also allow single
quotes (using the apostrophe key on your keyboard) `'`.  This does not work on
Windows, however.


What is what?
-------------

### The command-line shell

The *shell* is the program, that reads and interprets commands entered by the
user.  This program in itself is not very complicated.  Its functionality
usually boils down to the following steps:

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
(more on that later) and a greater-than sign `>`.

    C:\Users\Bob\Desktop>

Example 2:  On Ubuntu, the prompt of `bash`, the default shell, shows the user
name, the computer name, the current working directory, and a dollar sign `$`.

    bob@work-pc:~/Desktop$


What's in a path?
-----------------

In many cases, the arguments passed into a program, are the names of files or
folders.  This section describes how to tell a program how to find the file
(some of which may seem obvious, others not so much).

Everybody, who has used a computer before, is probably aware that the files on
a computer are organised in folders; and folders within the folders; and folders
within *these* folders; and so on.  On the command-line – and in many graphical
programs – the position of a file is written by spelling out the path across the
folder tree separating each element in the path with `\` on Windows or `/` on
Unix-like systems.

### Absolute paths

A path, which traces all the way to the top of the file system is called an
*absolute path* and the folder that makes up the top of the file system is
called the *root folder*.  Absolute paths are indicated by the fact that there
is a folder separator (`\` or `/`) in front of the first folder/file in the
path.

Note:  On Windows the file system has several folder trees, each with their own
root folder.  They are identified using the drive letters `a:` to `z:` (although
`a:` and `b:` are reserved for floppy drives, which are somewhat rare nowadays).

Example of an absolute path on Windows:

    C:\Users\Bob\Documents\Projects\Thesis\text-file.txt

Example of an absolute path on Unix-like systems:

    /home/bob/Documents/Projects/Thesis/text-file.txt

Also note:  On Unix-like systems, programs like to use the tilde `~` as
a shorthand for the current user's home directory, meaning the example above
can also be shortened as follows:

    ~/Documents/Projects/Thesis/text-file.txt

Reminder:  The command-line uses spaces to separate arguments from each other.
This means, if any element in a path contains a space, the whole path needs to
be put in quotation marks, to make sure it is interpreted as one entity:

    "C:\Users\Bob\Documents\My Projects\text file.txt"

### Relative paths and the working directory

The opposite of an absolute path is a *relative* path.  A relative starts with
the name of a file or folder, without the path separator in front of it.
Relative paths are always interpreted relative to the current *working
directory*.

When a program gets started, it gets assigned a working directory by whoever
started it.  In our case that's the shell:  Whenever you run a command from the
command-line, the shell assigns ‘the folder that you are currently in’ as that
command's working directory.

Side note:  Windows actually assigns *multiple* working directories to a program
– one for each drive letter.  However, we're going to ignore this in this
introduction.

Example of a relative path on Windows:

    Thesis\text-file.txt

Example of a relative path on Unix-like systems:

    Thesis/text-file.txt

### Dot and double-dot

There are two special path names, defined by the operating system: a single dot
`.` and double dot `..`.  The double dot `..` refers to the parent directory of
a folder, while the single `.` refers to the directory itself.  Consider the
following example (Windows version):

    ..\Thesis\text-file.txt

This path refers to a text file, in a folder called `Thesis`, which is in the
folder one level above the current working directory.

If the example were to use a single dot `.` instead, the path would refer to
a text file in the folder `Thesis` *within* the current working directory:

    .\Thesis\text-file.txt

Note that these shorthands also work *within* a path.  It is entirely possible
to specify the following path:

    C:\Users\Bob\.\Music\..\Documents\Projects\..\..\Desktop\text-file.txt

If we tried to find `text-file.txt` by following the path literally, we would
take the following steps:

 - Start at the root of drive `C:`
 - Step into `Users`
 - Step into `Bob`
 - Step into the current directory of `Bob` (i.e. do nothing)
 - Step into `Music`
 - Step into the parent directory of `Music` (i.e. back to `Bob`)
 - Step into `Documents`
 - Step into `Projects`
 - Step into the parent directory of `Projects` (i.e. back to `Documents`)
 - Step into the parent directory of `Documents` (i.e. back to `Bob` again)
 - Step into `Desktop`
 - Look for `text-file.txt` in there

Long story short, the path can be rewritten as follows:

    C:\Users\Bob\Documents\Desktop\text-file.txt

Using `.` and `..` like in the middle of a path is rarely useful when writing
paths by hand.  However it is something to be aware of, since you might
encounter paths like this in the wild, especially if they were generated
automatically by a program.


Navigating between folders
--------------------------

### Windows

To move to a different folder, use the `cd` (‘change directory’) command and
give it the path of the new working directory.  `cd` accepts both absolute and
relative paths:

    C:\Users\Bob> cd Documents
    C:\Users\Bob\Documents> cd C:\Users\Bob\Desktop
    C:\Users\Bob\Desktop>

If `cd` is run without any arguments, it will just output the current working
directory:

    C:\Users\Bob\Desktop> cd
    C:\Users\Bob\Desktop
    C:\Users\Bob\Desktop>

To move up a folder, run `cd` and give it the double dot `..` as an argument.

    C:\Users\Bob\Desktop> cd ..
    C:\Users\Bob> cd ..\..
    C:\>

If you are unsure, where to go next, it might be helpful to look at the contents
of the current folder.  To do so, run the `dir` (‘directory content’) command.

    C:\Users\Bob\Desktop> dir
     Volume in C is OS
     Volume serial number is ....-....

     Directory of C:\Users\Bob

    dd/mm/yyyy  hh:mm    <DIR>           .
    dd/mm/yyyy  hh:mm    <DIR>           ..
    dd/mm/yyyy  hh:mm    <DIR>           backups
    dd/mm/yyyy  hh:mm    <DIR>           photos
    dd/mm/yyyy  hh:mm            632.000 text-file (Copy).txt
    dd/mm/yyyy  hh:mm            712.000 text-file.txt
                   2 files
                   4 dirs

Note (a) that `dir` marks all directories in the list using the word `<DIR>` and
(b) that the list also contains the special names dot `.` and double-dot `..`.

### Unix-like systems

To move to a different folder, use the `cd` (‘change directory’) command and
give it the path of the new working directory.  `cd` accepts both absolute and
relative paths:

    bob@work-pc:~$ cd Documents
    bob@work-pc:~/Documents$ cd /usr/share
    bob@work-pc:/usr/share$ cd ~/Desktop
    bob@work-pc:~/Desktop$

If `cd` is run without any arguments, it will move to the current user's home
directory:

    bob@work-pc:~/Desktop$ cd
    bob@work-pc:~$

To output the current working directory, use the `pwd` (’print working
directory’) command.

    bob@work-pc:~/Desktop$ pwd
    /home/bob/Desktop
    bob@work-pc:~/Desktop$

To move up a folder, run `cd` and give it the double dot `..` as an argument.

    bob@work-pc:~/Desktop$ cd ..
    bob@work-pc:~$ cd ../..
    bob@work-pc:/$

If you are unsure, where to go next, it might be helpful to look at the contents
of the current folder.  To do so, run the `ls` (‘list directory content’)
command.

    bob@work-pc:~/Desktop$ ls
    backup   photos  'text-file (Copy).txt'   text-file.txt
    bob@work-pc:~/Desktop$


Wildcard characters
-------------------

Sometimes you want to run a program on multiple files, but typing out every file
name is tedious and error-prone.  This is where *wildcard characters* come in.
Wildcard characters are metacharacters that stand in for one or more unknown
characters.  The two most common examples are the question mark `?` and the
asterisk `*`:

 - `?` serves as a placeholder for a single unkown character.
 - `*` serves as a placeholder for any number of characters (or none).

Example 1:  The following command moves files like `text-01.txt`, `text-02.txt`,
`text-xy.txt`, etc. into the folder `backup` (Windows version):

    move text-??.txt backup

Example 2:  The following command deletes every file ending with the extension
`.exe` from the current working directory (Windows version):

    del *.exe

Note: Be extra careful with commands that delete or change files.  Always
double-check that the wildcard does not apply to any files you don't want
affected.  The command-line does not have an undo button nor a trash bin, so any
file you accidentally delete will be gone forever.

Also note: On Unix-like systems, wildcards are usually resolved by the shell,
before a program is run.  On Windows, wildcards are resolved by the programs
themselves.  Although this difference rarely matters in practice, it is
something to be aware of.


What's in a `PATH`?
-------------------

This section aims to answer two questions:

 1. Where are all those commands coming from?
 2. How do I add new commands to the command-line?


### Where are the commands?

Some commands are separate programs installed on your computer, others are built
directly into the shell.  For instance, on a Unix-like operating system using
the `bash` shell, the `cd` and `pwd` commands are built-in commands provided by
`bash` itself, but `ls` is its own program.

Now where does the shell look for programs to run?

For this the operating system defines an environment variable called `PATH`.

*Environment variables* are named pieces of information that are defined by the
operating system and that can be accessed from any program.  There is for
instance a variable called `USERNAME` on Windows, or just `USER` on Unix-like
systems, which holds the user name of the current user; or another called
`USERPROFILE` (Windows) or `HOME` (Unix-like), which contains the name of the
current user's home directory; and so on.  And of course, aforementioned `PATH`
variable.

The `PATH` variable contains a list of directories.  Whenever you type in the
bare name of a program, the shell will look through these directories in order
and when the directory contains a program of the same name, execute it.

Note:  On Windows you can omit file extensions like `.exe` or `.bat`.  The shell
will look for those extensions automatically.

However, what if the program you want to run is not in any of the directories
listed in `PATH`?  Then there are two options:

First, type in the path to the program – either as an absolute path or as a path
relative to your working directory.  For example, to run `7zip`'s command-line
tool on Windows you might run the following command-line (notice the quotation
marks because of the space in the name of the `Program Files` folder):

    C:\Users\Bob>"C:\Program Files\7-Zip\7z.exe" --help

Note:  On Unix-like systems, relative paths need *at least one folder name*,
otherwise the shell only look for programs in the `PATH`.   Luckily, this folder
name may also be a single dot `.`, so if you want to run a program in the
current working directory, you can run the following command:

    bob@work-pc:~$ ./my-program --help

The second option involves adding the directory of the program to your `PATH`,
so the shell knows where to find the program.

### Changing the `PATH` on Windows

First of all, you can look at the current value of the path variable using the
command-line.  To do this we make use of the `echo` command.  The `echo` command
simply outputs its own command-line arguments directly to the terminal:

    C:\Users\Bob> echo Hello
    Hello

In addition to this the `echo` command is able to expand environment variables
like `PATH`.  The exact syntax is different for `cmd.exe` and Powershell.  If
you are unsure, which one you are using, you can easily tell them apart by their
default colour scheme:

1. `cmd.exe` uses white letters on a black background
2. The Powershell is very blue

On the `cmd.exe` shell the name of the variable has to be enclosed in percentage
signs `%`, for example:

    C:\Users\Bob> echo %PATH%
    C:\Windows\System32;C:\Windows;C:\Windows\System32\Wbem;[...]

On Powershell put the string `$Env:` directly in front of the variable name, for
example:

    PS C:\Users\Bob> echo $Env:PATH
    C:\Windows\System32;C:\Windows;C:\Windows\System32\Wbem;[...]

As you can see the variable contains a list of absolute paths, separated by
*semicolons*.

To change the variable you can use the `Environment Variables` dialog in
Windows.  There are different ways to get to the dialog depending on the version
of Windows you are using.

1. Find the `System` dialog in the Control Centre
2. Open the `Advanced system settings` dialog
3. Go to the `Advanced` tab
4. Click on `Environment Variables`

On Windows 8 or 10 you can also use the Windows Search in your start menu to
look for something along the lines of ‘Change environment variables for you user
account’.  Note that you do not have to type out the whole thing.  The search
will incrementally offer you results.

In this dialog there are two sections:  `User Variables` and `System Variables`.
It is recommended to leave the system-wide settings alone and only change the
variables for your user account.

To change the `PATH` variable click on its respective line in the list and press
the `Edit…` button.  Add the absolute paths of the folders with the programs you
want to run to the back of the list, separated using semicolons.

If there is no `PATH` variable in the `User Variables` section of the dialog,
you can use the `New…` button to create it.  Don't worry about the fact that
there different `PATH` variables in the user and system-wide section of the
dialog.  Windows will automatically combine the two internally.

Note that the `PATH` variable itself can contain other environment variables,
enclosed in percentage signs `%` just like on `cmd.exe`.  This means you can
use the `USERPROFILE` variable to point to paths with your home directory
without typing it out directly every time.

Example:  Say you have installed the `7zip` program to `C:\Program Files\7-Zip`,
and you have a bunch of little programs in a folder `Programs` in your
`Documents` folder.  To add both to your path, add the following text to your
`PATH` variable:

    C:\Program Files\7-Zip;%USERPROFILE%\Documents\Programs

To reiterate:

 - `C:\Program Files\7-Zip` is an absolute path to the `7zip` program
 - The semicolon `;` separates the two paths
 - `%USERPROFILE%\Documents\Programs` uses the `USERPROFILE` variable to refer
   to the current user's home directory, meaning the path is interpreted as
   something like `C:\Users\Bob\Documents\Programs`

Also note that changes to environment variables only apply to newly started
programs, meaning you may have to restart your terminal window.

### Changing the `PATH` on Unix-like systems

First of all, you can look at the current value of the path variable using the
command-line.  To do this we make use of the `echo` command.  The `echo` command
simply outputs its own command-line arguments directly to the terminal:

    bob@work-pc:~$ echo Hello
    Hello

In addition to this the `echo` command is able to expand environment variables
like `PATH`.  To do so put a dollar sign `$` in front of the variable name:

    bob@work-pc:~$ echo $PATH
    /usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games

As you can see the variable contains a list of absolute paths, separated by
*colons*.

To change environment variables, go to your home directory and open the file
`.profile` in your text editor of choice.  If the file does not exit, create it.
Note that many file managers hide files starting with a dot `.` by default, so
you might have to turn on the ‘show hidden files‘ option – it's often under
`View` in the menu bar.

Note that some shells might use a different name for the file.  If you're using
the `bash` shell (default on most GNU/Linux or macOS systems), the file might be
called `.bash_profile` instead.  For the `zsh` shell (default on macOS 10.15
‘Catalina’ or higher) it is called `.zprofile`.  Also, if you are using a less
common shell such as `csh` or `fish`, read the documentation for your shell on
how to set environment variables permanently.

To find out which shell you are running, run the following command (that is
a dollar sign `$` followed by the number zero `0`):

    bob@work-pc:~$ echo $0
    /bin/bash

Variables are changed by adding a new line to the profile file like so:

    export MY_VARIABLE="new value"

This will set the variable `MY_VARIABLE` to the value `new value`.  Note that
this completely replaces any old value the variable might have had.  Luckily you
can include environment variables within the new value – including the old value
of the same variable.  To include the value of an environment variable, put a
dollar sign `$` in front of its name – just like in the `echo` command.

For example, you put can put another line below the line above like so:

    export MY_VARIABLE="this is not a $MY_VARIABLE anymore"

Then the value of `MY_VARIABLE` becomes the following:

    "this is not a new value anymore"

This behaviour can be used to add new paths to the `PATH` variable.  Say, you
installed Firefox manually into the folder `/opt/firefox` and want to add it to
your `PATH`.  Then you can add the folder to the back of the list by adding the
following line to your `~/.profile`:

    export PATH="$PATH:/opt/firefox"

This sets the `PATH` variable to a new value:

 - The old `PATH`
 - A colon `:` as a separator
 - The absolute path `/opt/firefox`

In other words the value of `PATH` changes from this:

    /usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games

To this:

    /usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games:/opt/firefox

It is also possible to create a similar line, where the new path is added at the
front of the list:

    export PATH="/opt/firefox:$PATH"

This would result in the following new value:

    /opt/firefox:/usr/local/bin:/usr/bin:/bin:/usr/local/games:/usr/games

*However:*  Remember that the shell starts searches the folders for programs *in
order*.  If there are two programs with the same name in both `/opt/firefox` and
`/usr/bin` the shell will run whatever comes first in the list.  This means that
a third-party program you installed after the fact, might actually overshadow
a program from your operating system.  Changes you make in `~/.profile` only
affect your current user account, so you are unlikely to do any real harm to
your computer, *buuut* overshadowing pre-installed software with random programs
from the internet is still not a particularly safe idea.  So don't do it.

Long story short, always add new paths to the *back* of the list.

After changing the file, save it, log off your user account and log back in
again, to apply the changes.


Getting help
------------


### Self-documenting programs

Some command-line programs include a brief description of all their options and
arguments in the program itself.  You can usually access this description by
specifying a special argument.

The command-line tools included in Windows usually use the `/?` argument
(forward slash and a question mark).  This means, if you want to look up some
help on how to use the `dir` command, you can run the following command:

    C:\Users\Bob> dir /?

On Unix-like systems, programs tend to use either `-h` (one dash and the letter
`h`) or `--help` (two dashes and the word `help`), for example:

    bob@work-pc:~$ ls --help

Note that third-party programs tend to favour the Unix way, including
`dictionaria`:

    C:\Users\Bob> dictionaria --help

### Unix manual pages

Unix-like systems traditionally come pre-installed with a comprehensive
reference manual that documents a lot of the commands, file formats, programming
libraries, etc. the operating ships with.  This manual is organised as
a collection of separate manual pages – a.k.a. `manpages`.  Each manpage talks
about one subject, e.g. a specific program and, despite being called a ‘page’,
they go into far more detail about a program than most built-in help messages.

Manpages can be accessed using a program called `man`.  For instance, to read
the manpage for the `ls` command, run the following command:

    bob@work-pc:~$ man ls

If you are unsure about the exact name of a manpage, you can use the `apropos`
program to output a list of related manual pages, each with a short summary.

    bob@work-pc:~$ apropos pwd

Note the `apropos` program also includes the summaries in its search.  This
means you can look for , like so:

    bob@work-pc:~$ apropos working directory

If you want to find out more about the manual in detail, the manual also
contains a page for the `man` program itself:

    bob@work-pc:~$ man man

### The Internet

This seems obvious, but people sometimes can't see the forest for the trees
– especially when they're stuck:  There are a lot of people working on the
command-line and there are a lot of people learning how to work on the
command-line.  And many of them have asked questions on-line, answered questions
on-line, written blog-posts, etc.  So whenever you're faced with a problem, no
matter how stupid you think your question might be, don't be shy to type it into
your search engine of choice.  You're unlikely to be the first.
