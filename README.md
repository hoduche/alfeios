# Fs-walker

### Walk your file system to check duplicate or missing files
___

>You need space on your hard drive ?

Fs-walker can walk your file system and list all duplicated files you can safely remove as well as the space you can gain.

>You want to give a new life to your old hard drive but you're not sure all its content has been saved on your new hard drive ?

Fs-walker can walk your two drives and list all files on the old one that are not present on the new one. 

## Install

#### From PyPI
To install Fs-walker from PyPI, just run:

```
pip install fs-walker
```

#### From GitHub
To install Fs-walker from GitHub:
1. Run:
    ```
    git clone https://github.com/hoduche/fs-walker
    ```
2. Inside the newly created fs-walker folder, run (with Python 3 and setuptools):
    ```
    python setup.py install
    ```

## Run

#### As a command
Upon installation, Fs-walker adds two commands to the command line: `duplicate` and `missing`.

Running `duplicate` will:
1. List all duplicated files and directories in a root directory passed as the --path (or -p) argument
2. Save the duplicate listing as a duplicate_listing.json file in the root directory
3. Print the potential space gain in Gigabytes

It can also dump the full listing.json and tree.json files in the root directory with the --dump-listing (or -d) argument.
And if a listing.json file is passed as the --path (or -p) argument instead of a root directory, the listing is deserialized from the json file instead of being generated.

Example:
```
duplicate -p E:/AllPictures -d
```

Running `missing` will:
1. List all files and directories that are present in an old root directory passed as the --old-path (or -o) argument and that are missing in a new one passed as the --new-path (or -n) argument
2. Save the missing listing as a missing_listing.json file in the new root directory

It can also dump the full listing.json and tree.json files in the two root directories with the --dump-listing (or -d) argument.
And if a listing.json file is passed as the --old-path (or -o) argument or as the --new-path (or -n) argument, instead of a root directory, the corresponding listing is deserialized from the json file instead of being generated.

Example:
```
missing -o D:/Pictures -n E:/AllPictures -d
```

#### As a Python module

```python
import pathlib

import fs_walker.walker as fsw

folder_path = pathlib.Path('D:/Pictures')
listing, tree, forbidden = fsw.walk(folder_path)
```
