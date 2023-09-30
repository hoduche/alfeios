import pathlib
import sys

import colorama
import tqdm

import alfeios.listing as al
import alfeios.serialize as asd
import alfeios.tool as at
import alfeios.walker as aw


def index(path, exclusion=None, no_cache=False, progress_bar=False):
    """

    - Index all file and directory contents in a root directory
      including the inside of zip, tar, gztar, bztar and xztar compressed files
    - Contents are identified by their hash-code and size
    - It saves 2 files in the root directory:
       - A tree.json.file that is a dictionary: path -> content
       - A forbidden.json file that lists paths with no access
    - In case of no write access to the root directory, the output files are
      saved in a temp directory of the filesystem with a unique identifier

    Args:
        path (str or pathlib.Path): path to the root directory
        exclusion (set of str): set of directories and files not to consider
        no_cache: boolean to decide if we should use cache when it exists
        progress_bar: boolean to show command progress with a progress bar
    """

    _index(path, exclusion, no_cache, progress_bar, save_index=True)


def duplicate(path, exclusion=None, no_cache=False, save_index=False):
    """

    - List all duplicated files and directories in a root directory
    - Save result as a duplicate_listing.json file in the root directory
    - Print the potential space gain
    - If a tree.json file is passed as positional argument instead of a root
      directory, the tree is deserialized from the json file instead of
      being generated, which is significantly quicker but of course less up to
      date
    - Can save the tree.json and forbidden.json files in the root directory
    - In case of no write access to the root directory, the output files are
      saved in a temp directory of the filesystem with a unique identifier

    Args:
        path (str or pathlib.Path): path to the root directory to parse or the
                                    tree.json file to deserialize
        exclusion (set of str): set of directories and files not to consider
        no_cache: boolean to decide if we should use cache when it exists
        save_index (bool): flag to save the tree.json and forbidden.json files
                           in the root directory
                           default is False
    """

    path = pathlib.Path(path)
    if path.is_file() and path.name.endswith('_tree.json'):
        tree = asd.load_json_tree(path)
        # todo fragile hypothesis that this is inside an .alfeios directory
        path = path.parent.parent
    else:
        tree = _index(path, exclusion, no_cache, save_index=save_index)

    listing = al.tree_to_listing(tree)
    duplicate_listing, size_gain = al.get_duplicate(listing)

    if duplicate_listing:
        f = asd.save_json_listing(path, duplicate_listing)
        f = at.add_suffix(f, '_duplicate')
        print(colorama.Fore.GREEN +
              f'You can gain {at.natural_size(size_gain)} '
              f'space by going through {f}')
    else:
        print(colorama.Fore.GREEN +
              'Congratulations there is no duplicate here')


def missing(old_path, new_path, exclusion=None, no_cache=False,
            save_index=False):
    """

    - List all files and directories that are present in an old root directory
      and that are missing in a new one
    - Save result as a missing_listing.json file in the old root directory
    - Print the number of missing files
    - If a tree.json file is passed as positional argument instead of a root
      directory, the corresponding tree is deserialized from the json file
      instead of being generated, which is significantly quicker but of course
      less up to date
    - Can save the tree.json and forbidden.json files in the 2 root directories
    - In case of no write access to the new root directory, the output files
      are saved in a temp directory of the filesystem with a unique identifier

    Args:
        old_path (str or pathlib.Path): path to the old root directory to parse
                                        or the tree.json file to deserialize
        new_path (str or pathlib.Path): path to the new root directory to parse
                                        or the tree.json file to deserialize
        exclusion (set of str): set of directories and files not to consider
        no_cache: boolean to decide if we should use cache when it exists
        save_index (bool): flag to save the tree.json and forbidden.json files
                           in the 2 root directories
                           default is False
    """

    old_path = pathlib.Path(old_path)
    if old_path.is_file() and old_path.name.endswith('_tree.json'):
        old_tree = asd.load_json_tree(old_path)
        # todo fragile hypothesis that this is inside an .alfeios directory
        old_path = old_path.parent.parent
    else:
        old_tree = _index(old_path, exclusion, no_cache, save_index=save_index)

    new_path = pathlib.Path(new_path)
    if new_path.is_file() and new_path.name.endswith('_tree.json'):
        new_tree = asd.load_json_tree(new_path)
    else:
        new_tree = _index(new_path, exclusion, no_cache, save_index=save_index)

    old_listing = al.tree_to_listing(old_tree)
    new_listing = al.tree_to_listing(new_tree)
    missing_listing = al.get_missing(old_listing, new_listing)

    if missing_listing:
        f = asd.save_json_listing(old_path, missing_listing)
        f = at.add_suffix(f, '_missing')
        print(colorama.Fore.GREEN +
              f'There are {len(missing_listing)} Old files missing in New'
              f' - please go through {f} in Old')
    else:
        print(colorama.Fore.GREEN +
              'Congratulations Old content is totally included in New')


def _index(path, exclusion=None, no_cache=False, progress_bar=False,
           save_index=False):
    path = pathlib.Path(path)
    if not path.is_dir():
        print(colorama.Fore.RED + f'{path} is not a valid path - exiting',
              file=sys.stderr)
        return {}
    else:
        cache = dict() if no_cache else asd.load_last_json_tree(path)
        if progress_bar:
            tree, forbidden = _walk_with_progressbar(
                path, exclusion=exclusion, cache=cache)
        else:
            tree, forbidden = _walk_without_progressbar(
                path, exclusion=exclusion, cache=cache)
        if save_index:
            asd.save_json_tree(path, tree, forbidden)
        return tree


def _walk_without_progressbar(path, exclusion=None, cache=None):
    tree, forbidden = aw.walk(path, exclusion=exclusion, cache=cache,
                              should_unzip=True, should_hash=True,
                              pbar=None)
    return tree, forbidden


def _walk_with_progressbar(path, exclusion=None, cache=None):
    # todo move to walker by injecting pbar so that tqdm is not known by walker

    # First walk without hashing, just to get the total size to hash
    pbar_nb_files = tqdm.tqdm(total=1, desc='Exploring',
                              unit=' files', unit_scale=False)
    t, f = aw.walk(path, exclusion=exclusion, cache=dict(),
                   should_unzip=True, should_hash=False,
                   pbar=pbar_nb_files)
    path_size = sum(c[aw.SIZE] for c in t.values())
    pbar_nb_files.close()

    # Second walk with hashing and progress bar based on the total size to hash
    pbar_size = tqdm.tqdm(total=path_size, desc='Indexing ',
                          unit='B', unit_scale=True, unit_divisor=1024)
    tree, forbidden = aw.walk(path, exclusion=exclusion, cache=cache,
                              should_unzip=True, should_hash=True,
                              pbar=pbar_size)
    pbar_size.close()

    return tree, forbidden
