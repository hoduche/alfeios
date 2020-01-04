import pathlib

import fs_walker.walker as fsw


def duplicate(path, dump_listing=False):
    """
    List all duplicated files and directories in
    a root directory passed as the path argument.
    Save the duplicate listing as a duplicate_listing.json file in the root directory.
    Print the potential space gain.

    Can also dump the full listing.json and tree.json files in the root directory
    with the dump_listing argument.
    If a listing.json file is passed as the path argument instead of a root
    directory, the listing is deserialized from the json file instead of being generated,
    which is significantly quicker but of course less up to date.

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
        import collections
        listing = collections.defaultdict(set)
        tree = dict()
        forbidden = set()
#        listing, tree, forbidden = fsw.walk(path)
        folder_path = path
        if dump_listing:
            fsw.dump_json_listing(listing, folder_path / 'listing.json')
            fsw.dump_json_tree(tree, folder_path / 'tree.json')
            fsw.dump_json_forbidden(forbidden, folder_path / 'forbidden.json')
    else:
        print(f'This is not a valid path - exiting')
        return

    duplicate_listing, size_gain = fsw.get_duplicate(listing)
    if duplicate_listing:
        foreword = 'You can gain '
        afterword = 'bytes space by going through duplicate_listing.json'
        fsw.dump_json_listing(duplicate_listing, folder_path / 'duplicate_listing.json')
        if size_gain < 1E3:
            print(foreword + f'{size_gain} ' + afterword)
        elif size_gain < 1E6:
            print(foreword + f'{size_gain / 1E3:.2f} Kilo' + afterword)
        elif size_gain < 1E9:
            print(foreword + f'{size_gain / 1E6:.2f} Mega' + afterword)
        elif size_gain < 1E12:
            print(foreword + f'{size_gain / 1E9:.2f} Giga' + afterword)
        else:
            print(foreword + f'{size_gain / 1E12:.2f} Tera' + afterword)
    else:
        print(f'Congratulations there is no duplicate here')


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
        old_listing, old_tree, old_forbidden = fsw.walk(old_path)
        old_folder_path = old_path
        if dump_listing:
            fsw.dump_json_listing(old_listing, old_folder_path / 'listing.json')
            fsw.dump_json_tree(old_tree, old_folder_path / 'tree.json')
            fsw.dump_json_forbidden(old_forbidden, old_folder_path / 'forbidden.json')
    else:
        print(f'Old is not a valid path - exiting')
        return

    new_path = pathlib.Path(new_path)
    if new_path.name == 'listing.json':
        new_listing = fsw.load_json_listing(new_path)
        new_folder_path = new_path.parent
    elif new_path.is_dir():
        new_listing, new_tree, new_forbidden = fsw.walk(new_path)
        new_folder_path = new_path
        if dump_listing:
            fsw.dump_json_listing(new_listing, new_folder_path / 'listing.json')
            fsw.dump_json_tree(new_tree, new_folder_path / 'tree.json')
            fsw.dump_json_forbidden(new_forbidden, new_folder_path / 'forbidden.json')
    else:
        print(f'New is not a valid path - exiting')
        return

    missing_listing = fsw.get_missing(old_listing, new_listing)
    if missing_listing:
        fsw.dump_json_listing(missing_listing, new_folder_path / 'missing_listing.json')
        print(f'There are {len(missing_listing)} Old files missing in New'
               ' - please go through missing_listing.json')
    else:
        print(f'Congratulations Old content is totally included in New')
