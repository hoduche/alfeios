import pathlib
import sys

import alfeios.serialize as asd
import alfeios.walker as aw


def index(path):
    """

    - Index all file and directory contents in a root directory
      including the inside of zip, tar, gztar, bztar and xztar compressed files
    - Contents are identified by their hash-code, type (file or directory) and
      size
    - It saves three files in the root directory:
       - A listing.json file that is a dictionary: content -> list of paths
       - A tree.json.file that is a dictionary: path -> content
         (the listing.json dual)
       - A forbidden.json file that lists paths with no access
    - In case of no write access to the root directory, the output files are
      saved in a temp directory of the filesystem with a unique identifier

    Args:
        path (str or pathlib.Path): path to the root directory
    """

    path = pathlib.Path(path)
    if path.is_dir():
        listing, tree, forbidden = aw.walk(path)
        asd.save_json_listing(listing, path / 'listing.json')
        asd.save_json_tree(tree, path / 'tree.json')
        asd.save_json_forbidden(forbidden, path / 'forbidden.json')
    else:
        print(f'This is not a valid path - exiting')
        return


def duplicate(path, save_index=False):
    """

    - List all duplicated files and directories in a root directory
    - Save result as a duplicate_listing.json file in the root directory
    - Print the potential space gain
    - If a listing.json file is passed as positional argument instead of a root
      directory, the listing is deserialized from the json file instead of
      being generated, which is significantly quicker but of course less up to
      date
    - Can save the listing.json, tree.json and forbidden.json files in the root
      directory
    - In case of no write access to the root directory, the output files are
      saved in a temp directory of the filesystem with a unique identifier

    Args:
        path (str or pathlib.Path): path to the root directory to parse or the
                                    listing.json file to deserialize
        save_index (bool): flag to save the listing.json, tree.json and
                           forbidden.json files in the root directory
                           default is False
    """

    path = pathlib.Path(path)
    if path.is_file() and path.name == 'listing.json':
        listing = asd.load_json_listing(path)
        directory_path = path.parent
    elif path.is_dir():
        listing, tree, forbidden = aw.walk(path)
        directory_path = path
        if save_index:
            asd.save_json_listing(listing, directory_path / 'listing.json')
            asd.save_json_tree(tree, directory_path / 'tree.json')
            asd.save_json_forbidden(forbidden,
                                    directory_path / 'forbidden.json')
    else:
        print(f'This is not a valid path - exiting', file=sys.stderr)
        return

    duplicate_listing, size_gain = aw.get_duplicate(listing)
    if duplicate_listing:
        foreword = 'You can gain '
        afterword = 'bytes space by going through duplicate_listing.json'
        asd.save_json_listing(duplicate_listing,
                              directory_path / 'duplicate_listing.json')
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


def missing(old_path, new_path, save_index=False):
    """

    - List all files and directories that are present in an old root directory
      and that are missing in a new one
    - Save result as a missing_listing.json file in the new root directory
    - Print the number of missing files
    - If a listing.json file is passed as positional argument instead of a root
      directory, the corresponding listing is deserialized from the json file
      instead of being generated, which is significantly quicker but of course
      less up to date
    - Can save the listing.json, tree.json and forbidden.json files in the 2
      root directories
    - In case of no write access to the new root directory, the output files
      are saved in a temp directory of the filesystem with a unique identifier

    Args:
        old_path (str or pathlib.Path): path to the old root directory to parse
                                        or the listing.json file to deserialize
        new_path (str or pathlib.Path): path to the new root directory to parse
                                        or the listing.json file to deserialize
        save_index (bool): flag to save the listing.json, tree.json
                           and forbidden.json files in the 2 root directories
                           default is False
    """

    old_path = pathlib.Path(old_path)
    if old_path.is_file() and old_path.name == 'listing.json':
        old_listing = asd.load_json_listing(old_path)
    elif old_path.is_dir():
        old_listing, old_tree, old_forbidden = aw.walk(old_path)
        old_directory_path = old_path
        if save_index:
            asd.save_json_listing(old_listing,
                                  old_directory_path / 'listing.json')
            asd.save_json_tree(old_tree, old_directory_path / 'tree.json')
            asd.save_json_forbidden(old_forbidden,
                                    old_directory_path / 'forbidden.json')
    else:
        print(f'Old is not a valid path - exiting')
        return

    new_path = pathlib.Path(new_path)
    if new_path.is_file() and new_path.name == 'listing.json':
        new_listing = asd.load_json_listing(new_path)
        new_directory_path = new_path.parent
    elif new_path.is_dir():
        new_listing, new_tree, new_forbidden = aw.walk(new_path)
        new_directory_path = new_path
        if save_index:
            asd.save_json_listing(new_listing,
                                  new_directory_path / 'listing.json')
            asd.save_json_tree(new_tree, new_directory_path / 'tree.json')
            asd.save_json_forbidden(new_forbidden,
                                    new_directory_path / 'forbidden.json')
    else:
        print(f'New is not a valid path - exiting')
        return

    missing_listing = aw.get_missing(old_listing, new_listing)
    if missing_listing:
        asd.save_json_listing(missing_listing,
                              new_directory_path / 'missing_listing.json')
        print(f'There are {len(missing_listing)} Old files missing in New'
              ' - please go through missing_listing.json')
    else:
        print(f'Congratulations Old content is totally included in New')
