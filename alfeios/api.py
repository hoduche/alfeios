import pathlib

import alfeios.io as ai
import alfeios.walker as aw


def index(path):
    """
    - Index all file and directory contents in a root directory
      including the inside of zip, tar, gztar, bztar and xztar compressed files
    - Contents are identified by their hash-code, type (file or directory) and size
    - It saves in the root directory:
       - A listing.json file that is a dictionary: content -> list of paths
       - A tree.json.file that is a dictionary: path -> content
       - A forbidden.json file that lists paths with no access
    - In case there is no write access to the root directory,
      the output files are saved in a temp folder of the filesystem with a unique identifier

    :param path: path of the root directory
    :type path: str or pathlib.Path
    """

    path = pathlib.Path(path)
    if path.is_dir():
        listing, tree, forbidden = aw.walk(path)
        ai.save_json_listing(listing, path / 'listing.json')
        ai.save_json_tree(tree, path / 'tree.json')
        ai.save_json_forbidden(forbidden, path / 'forbidden.json')
    else:
        print(f'This is not a valid path - exiting')
        return


def duplicate(path, save_listing=False):
    """
    List all duplicated files and directories in
    a root directory passed as the path argument.
    Save the duplicate listing as a duplicate_listing.json file in the root directory.
    Print the potential space gain.

    Can also save the full listing.json and tree.json files in the root directory
    with the save_listing argument.
    If a listing.json file is passed as the path argument instead of a root
    directory, the listing is deserialized from the json file instead of being generated,
    which is significantly quicker but of course less up to date.

    :param path: path of the root directory to parse
                 or the listing.json file to deserialize
    :type path: str or pathlib.Path

    :param save_listing: flag to save the full listing.json and tree.json files
                         in the root directory
                         default is False
    :type save_listing: bool
    """

    path = pathlib.Path(path)
    if path.name == 'listing.json':
        listing = ai.load_json_listing(path)
        folder_path = path.parent
    elif path.is_dir():
        listing, tree, forbidden = aw.walk(path)
        folder_path = path
        if save_listing:
            ai.save_json_listing(listing, folder_path / 'listing.json')
            ai.save_json_tree(tree, folder_path / 'tree.json')
            ai.save_json_forbidden(forbidden, folder_path / 'forbidden.json')
    else:
        print(f'This is not a valid path - exiting')
        return

    duplicate_listing, size_gain = aw.get_duplicate(listing)
    if duplicate_listing:
        foreword = 'You can gain '
        afterword = 'bytes space by going through duplicate_listing.json'
        ai.save_json_listing(duplicate_listing, folder_path / 'duplicate_listing.json')
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


def missing(old_path, new_path, save_listing=False):
    """
    List all files and directories that
    are present in an old root directory passed as the old_path argument
    and that are missing in a new one passed as the new_path argument.
    Save the missing listing as a missing_listing.json file in the new root directory.
    Can also save the full listing.json and tree.json files in the two root directories
    with the save_listing argument.
    If a listing.json file is passed as the old-path argument
    or as the new-path argument instead of a root directory,
    the corresponding listing is deserialized from the json file instead of being generated.


    :param old_path: path of the old root directory to parse
                     or the listing.json file to deserialize
    :type old_path: str or pathlib.Path

    :param new_path: path of the new root directory to parse
                     or the listing.json file to deserialize
    :type new_path: str or pathlib.Path

    :param save_listing: flag to save the full listing.json and tree.json files
                         in the two root directories
                         default is False
    :type save_listing: bool
    """

    old_path = pathlib.Path(old_path)
    if old_path.name == 'listing.json':
        old_listing = ai.load_json_listing(old_path)
    elif old_path.is_dir():
        old_listing, old_tree, old_forbidden = aw.walk(old_path)
        old_folder_path = old_path
        if save_listing:
            ai.save_json_listing(old_listing, old_folder_path / 'listing.json')
            ai.save_json_tree(old_tree, old_folder_path / 'tree.json')
            ai.save_json_forbidden(old_forbidden, old_folder_path / 'forbidden.json')
    else:
        print(f'Old is not a valid path - exiting')
        return

    new_path = pathlib.Path(new_path)
    if new_path.name == 'listing.json':
        new_listing = ai.load_json_listing(new_path)
        new_folder_path = new_path.parent
    elif new_path.is_dir():
        new_listing, new_tree, new_forbidden = aw.walk(new_path)
        new_folder_path = new_path
        if save_listing:
            ai.save_json_listing(new_listing, new_folder_path / 'listing.json')
            ai.save_json_tree(new_tree, new_folder_path / 'tree.json')
            ai.save_json_forbidden(new_forbidden, new_folder_path / 'forbidden.json')
    else:
        print(f'New is not a valid path - exiting')
        return

    missing_listing = aw.get_missing(old_listing, new_listing)
    if missing_listing:
        ai.save_json_listing(missing_listing, new_folder_path / 'missing_listing.json')
        print(f'There are {len(missing_listing)} Old files missing in New'
               ' - please go through missing_listing.json')
    else:
        print(f'Congratulations Old content is totally included in New')
