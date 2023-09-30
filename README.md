# Alfeios

### Enrich your command-line shell with Herculean cleaning capabilities
___

![full](doc/augias.jpg)

As fifth Labour, Heracles was charged with cleaning the [Augean stables
](https://en.wikipedia.org/wiki/Labours_of_Hercules#Fifth:_Augean_stables).
The beautiful stables had not been cleaned for thirty years and were 
overshadowed in filth.
Instead of turning to the mop and bucket,
Heracles used a radically innovative tool:
the [Alfeios river](https://en.wikipedia.org/wiki/Alfeios) waters 
and managed to wash everything in just one day.

Let's do a comparison with the data on your hard drives.
Backups have been made, files have been renamed, directories have been moved 
... Slowly but surely things have diverged significantly,
up to a point where you did not feel safe to delete anything.
That is where things got worse as you started accumulating
duplicates, sacrificing all hopes to control your data.
As a result cleaning your hard drives now appears to you as the fifth labour
of Heracles, humanly impossible.

Alfeios is an innovative tool that makes this overwhelming task feasible.
It recursively indexes the content of your hard drives, going inside zip, tar, 
gztar, bztar and xztar compressed files.
Its index is content-based, meaning that two files with different names and 
different dates will be identified as duplicate if they share the same content.
This will tell you when files can safely be removed, 
gaining space and cleaning data on your hard drives.

## Install
```
pip install alfeios
```

## Run
Alfeios is a software that operates from a
[command-line interface](https://en.wikipedia.org/wiki/Command-line_interface)
in a shell.

Upon installation, on any operating system thanks to the magic of [Python 
entry points](https://amir.rachum.com/blog/2017/07/28/python-entry-points),
three commands are added to your shell.
One low-level command: `alfeios index` and two high-level
commands: `alfeios duplicate` and `alfeios missing`.

### `alfeios index`
Index content of a root directory:

- Index all file and directory contents in a root directory
  including the inside of zip, tar, gztar, bztar and xztar compressed files
- Contents are identified by their hash-code, type (file or directory) and
  size
- It saves two files tagged with the current time in a .alfeios folder 
in the root directory:
    - A tree.json.file that is a dictionary: path -> content
    - A forbidden.json file that lists paths with no access

Example:
```
alfeios index
alfeios idx D:/Pictures
alfeios i
```

`alfeios idx` and `alfeios i` can be used as aliases for `alfeios index`

If no positional argument is passed, the root directory is 
defaulted to the current working directory.

### `alfeios duplicate`
Find duplicate content in a root directory:

- List all duplicated files and directories in a root directory
- Save result as a duplicate_listing.json file tagged with the current time
 in a .alfeios folder in the root directory
- Print the potential space gain

Example:
```
alfeios duplicate
alfeios dup -s D:/Pictures
alfeios d D:/Pictures/.alfeios/2020_01_29_10_29_39_listing.json
```

`alfeios dup` and `alfeios d` can be used as aliases for `alfeios duplicate`

If no positional argument is passed, the root directory is 
defaulted to the current working directory.

The '-s' or '--save-index' optional flag saves the tree.json and forbidden.json
files tagged with the current time in a .alfeios folder in the root directory.

If a tree.json file is passed as positional argument instead of a root
directory, the tree is deserialized from the json file
instead of being generated, which is significantly quicker but of course
less up to date.

### `alfeios missing`
Find missing content in a new root directory from an old root directory:

- List all files and directories that are present in an old root directory
  and that are missing in a new one
- Save result as a missing_listing.json file tagged with the current time 
in a .alfeios folder in the old root directory
- Print the number of missing files

Example:
```
alfeios missing D:/Pictures E:/AllPictures
alfeios mis -s D:/Pictures E:/AllPictures
alfeios m D:/Pictures/.alfeios/2020_01_29_10_29_39_listing.json E:/AllPics
```

`alfeios mis` and `alfeios m` can be used as aliases for `alfeios missing`

The '-s' or '--save-index' optional flag saves the tree.json and forbidden.json
files tagged with the current time in a .alfeios folder in the 2 root
directories.

If a tree.json file is passed as positional argument instead of a root
directory, the corresponding tree is deserialized from the json file
instead of being generated, which is significantly quicker but of course
less up to date.

## For developers
```
git clone https://github.com/hoduche/alfeios
```
Then from the newly created alfeios directory, run:
```
pip install -e .
```
And in a Python file, call:
```python
import pathlib

import alfeios.api

folder_path = pathlib.Path('D:/Pictures')
alfeios.api.index(folder_path)
```

To build:
```
flake8 -v alfeios tests
pytest -vv
python3 -m build
python3 -m twine upload dist/*
```



## Areas for improvement

### Viewer
For the moment Alfeios output are raw json files that are left at the user 
disposal.
A dedicated json viewer with graph display could be a better decision support
 tool.

### File Manager
For the moment Alfeios is in read-only mode. It could be enriched with other 
file manager 
[CRUD](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete) 
functions, in particular duplicate removal possibilities.

### File System
For the moment Alfeios is only a add-on to the command line shell.
Its content-based index could be further rooted in the file system and 
refreshed incrementally after each file system operation, supporting the 
[copy-on-write principle
](https://en.wikipedia.org/wiki/Copy-on-write#In_computer_storage).
