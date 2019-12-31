import pathlib

import fs_walker.walker as fsw


def duplicate(path, dump_listing=False):
    """
    List all duplicated files and directories in
    a root directory passed as the path argument.
    Save the duplicate listing as a duplicate_listing.json file in the root directory.
    Print the potential space gain in Gigabytes.
    Can also dump the full listing.json and tree.json files in the root directory
    with the dump_listing argument.
    If a listing.json file is passed as the path argument instead of a root
    directory, the listing is deserialized from the json file instead of being generated.

    :param path: path of the root directory to parse
                 or the listing.json file to deserialize
    :type path: str or pathlib.Path

    :param dump_listing: flag to dump the full listing.json and tree.json files
                         in the root directory
                         default is False
    :type dump_listing: bool
    """

    path = pathlib.Path(path)
    if path.name == 'listing.json':
        listing = fsw.load_json_listing(path)
        folder_path = path.parent
    elif path.is_dir():
        listing, tree = fsw.walk(path)
        folder_path = path
        if dump_listing:
            fsw.dump_json_listing(listing, folder_path / 'listing.json')
            fsw.dump_json_tree(tree, folder_path / 'tree.json')
    else:
        return

    duplicate_listing, size_gain = fsw.get_duplicate(listing)
    fsw.dump_json_listing(duplicate_listing, folder_path / 'duplicate_listing.json')
    print(f'you can gain {size_gain / 1E9:.2f} Gigabytes space by going through duplicate.json')


def missing(old_path, new_path, dump_listing=False):
    """
    List all files and directories that
    are present in an old root directory passed as the old_path argument
    and that are missing in a new one passed as the new_path argument.
    Save the missing listing as a missing_listing.json file in the new root directory.
    Can also dump the full listing.json and tree.json files in the two root directories
    with the dump_listing argument.
    If a listing.json file is passed as the old-path argument
    or as the new-path argument instead of a root directory,
    the corresponding listing is deserialized from the json file instead of being generated.


    :param old_path: path of the old root directory to parse
                     or the listing.json file to deserialize
    :type old_path: str or pathlib.Path

    :param new_path: path of the new root directory to parse
                     or the listing.json file to deserialize
    :type new_path: str or pathlib.Path

    :param dump_listing: flag to dump the full listing.json and tree.json files
                         in the two root directories
                         default is False
    :type dump_listing: bool
    """

    old_path = pathlib.Path(old_path)
    if old_path.name == 'listing.json':
        old_listing = fsw.load_json_listing(old_path)
    elif old_path.is_dir():
        old_listing, old_tree = fsw.walk(old_path)
        old_folder_path = old_path
        if dump_listing:
            fsw.dump_json_listing(old_listing, old_folder_path / 'listing.json')
            fsw.dump_json_tree(old_tree, old_folder_path / 'tree.json')
    else:
        return

    new_path = pathlib.Path(new_path)
    if new_path.name == 'listing.json':
        new_listing = fsw.load_json_listing(new_path)
        new_folder_path = new_path.parent
    elif new_path.is_dir():
        new_listing, new_tree = fsw.walk(new_path)
        new_folder_path = new_path
        if dump_listing:
            fsw.dump_json_listing(new_listing, new_folder_path / 'listing.json')
            fsw.dump_json_tree(new_tree, new_folder_path / 'tree.json')
    else:
        return

    missing_listing = fsw.get_missing(old_listing, new_listing)
    fsw.dump_json_listing(missing_listing, new_folder_path / 'missing_listing.json')
