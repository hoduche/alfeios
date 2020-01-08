----------------------------------------------------------------
-- Alfeios
----------------------------------------------------------------
Enrich your command-line shell [or file system / file manager] with Herculean cleaning capabilities.

Alfeios is a command line program ie a program that operates from the command line or from a shell


Have you ever felt overhelmed with all your hard drive backups that have diverged significantly
files have been renamed, folders have been moved and it is humanly impossible to rationalize
So you keep all your backups, just in case,

Alfeios can ...


Alfeios recursively indexes the content of a directory.
It goes inside zip, tar, gztar, bztar and xztar compressed files




to check duplicate or missing files

You need space on your hard drive ?
Fs-walker can walk your file system and list all duplicated files you can safely remove as well as the space you can gain.

You want to give a new life to your old hard drive but you are not sure all its content has been saved on your new hard drive ?
Fs-walker can walk your two drives and list all files on the old one that are not present on the new one. 

Upon installation, Fs-walker adds three commands to your command line (interface) shell `missing`, `duplicate` and `walk`

This works on all Operating Systems thanks to the magic of Python entry points


----------------------------------------------------------------
`alfeios index` or `alfeios index-content`:
index /usr/pictures

walk the filesystem directory passed as positional argument
by default current directory
write listing + tree + forbidden (otherwise it is useless) in the directory passed as positional argument
if no write access write them in a temp folder of the filesystem with a unique id and print the info to the console
by default display a progress bar + write info, -q --quiet displays nothing

----------------------------------------------------------------
`alfeios duplicate` or `alfeios find-duplicate-content`:



Running `duplicate` will:
1. List all duplicated files and directories in a root directory passed as the --path (or -p) argument
2. Save the duplicate listing as a duplicate_listing.json file in the root directory
3. Print the potential space gain in Gigabytes

It can also dump the full listing.json and tree.json files in the root directory with the --dump-listing (or -d) argument.
And if a listing.json file is passed as the --path (or -p) argument instead of a root directory, the listing is deserialized from the json file instead of being generated.

duplicate -p E:/AllPictures -d


----------------------------------------------------------------
`alfeios missing` or `alfeios find-missing-content`:



Running `missing` will:
1. List all files and directories that are present in an old root directory passed as the --old-path (or -o) argument and that are missing in a new one passed as the --new-path (or -n) argument
2. Save the missing listing as a missing_listing.json file in the new root directory

It can also dump the full listing.json and tree.json files in the two root directories with the --dump-listing (or -d) argument.
And if a listing.json file is passed as the --old-path (or -o) argument or as the --new-path (or -n) argument, instead of a root directory, the corresponding listing is deserialized from the json file instead of being generated.

missing -o D:/Pictures -n E:/AllPictures -d

----------------------------------------------------------------
Improvements axis:

- Viewer: For the moment Alfeios output are raw json files that are left at the user disposal. A dedicated json viewer with graph display could be a better decision support tool.

- File Manager: For the moment Alfeios is in read-only mode. It could be enriched with other file manager [CRUD](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete) functions, in particular duplicate removal possibilities.

- File System: For the moment Alfeios is only a add-on to the command line shell. Its content-based index could be further rooted in the file system and refreshed incrementally after each file system operation, supporting the [copy-on-write principle](https://en.wikipedia.org/wiki/Copy-on-write#In_computer_storage).
