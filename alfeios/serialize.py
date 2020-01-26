import ast
import collections
import colorama
import datetime
import json
import pathlib
import tempfile

import alfeios.tool as at


def save_json_index(dir_path, listing, tree=None, forbidden=None,
                    start_path=None, prefix=''):
    """

    Save the three data structures of the index (listing, tree and
    forbidden) as json files, tagged with the current date and time plus a user
    definable prefix, in a .alfeios subdirectory, inside the directory passed
    as first argument

    Args:
        dir_path (pathlib.Path): path to the directory where the index will be
        saved (in a .alfeios subdirectory)
        listing (collections.defaultdict(set) =
                 {(hash, type, int): {pathlib.Path}}): listing to serialize
        tree (dict = {pathlib.Path: (hash, type, int)}): tree to serialize
        forbidden (dict = {pathlib.Path: type(Exception)}): forbidden to
                                                            serialize
        start_path (pathlib.Path): start path to remove from each path in the
                                   json serialized index
        prefix (str): prefix to prepend to index json files

    Returns:
        tag with the current date and time plus a user definable prefix(str)
    """

    path = dir_path / '.alfeios'
    if not pathlib.Path(path).is_dir():
        pathlib.Path(path).mkdir()

    tag = datetime.datetime.now().strftime('%Y_%m_%d_%H_%M_%S_') + prefix

    _save_json_listing(listing, path / (tag + 'listing.json'), start_path)
    if tree:
        _save_json_tree(tree, path / (tag + 'tree.json'), start_path)
    if forbidden:
        _save_json_forbidden(forbidden, path / (tag + 'forbidden.json'),
                             start_path)

    return tag


def load_json_listing(file_path, start_path=None):
    """

    Args:
        file_path (pathlib.Path): path to an existing json serialized listing
        start_path (pathlib.Path): start path to prepend to each relative path
                                   in the listing

    Returns:
        collections.defaultdict(set) = {(hash, type, int): {pathlib.Path}}
    """

    json_listing = file_path.read_text()
    serializable_listing = json.loads(json_listing)
    dict_listing = {ast.literal_eval(tuple_key): {pathlib.Path(path)
                                                  for path in path_list}
                    for tuple_key, path_list in serializable_listing.items()}
    if start_path:
        dict_listing = {tuple_key: {start_path / path for path in path_list}
                        for tuple_key, path_list in dict_listing.items()}
    listing = collections.defaultdict(set, dict_listing)
    return listing


def load_json_tree(file_path, start_path=None):
    """

    Args:
        file_path (pathlib.Path): path to an existing json serialized tree
        start_path (pathlib.Path): start path to prepend to each relative path
                                   in the tree

    Returns:
        dict = {pathlib.Path: (hash, type, int)}
    """

    json_tree = file_path.read_text()
    serializable_tree = json.loads(json_tree)
    tree = {pathlib.Path(path_key): tuple(value)
            for path_key, value in serializable_tree.items()}
    if start_path:
        tree = {start_path / path_key: tuple_value
                for path_key, tuple_value in tree.items()}
    return tree


def _save_json_listing(listing, file_path, start_path=None):
    if start_path:
        listing = {tuple_key: {at.build_relative_path(path, start_path)
                               for path in path_set}
                   for tuple_key, path_set in listing.items()}
    serializable_listing = {
        str((tuple_key[0], str(tuple_key[1])[9:], tuple_key[2])):
            [str(pathlib.PurePosixPath(path)) for path in path_set]
        for tuple_key, path_set in listing.items()}
    json_listing = json.dumps(serializable_listing)
    _write_text(json_listing, file_path)


def _save_json_tree(tree, file_path, start_path=None):
    if start_path:
        tree = {at.build_relative_path(path_key, start_path): tuple_value
                for path_key, tuple_value in tree.items()}
    serializable_tree = {str(pathlib.PurePosixPath(path_key)): tuple_value
                         for path_key, tuple_value in tree.items()}
    json_tree = json.dumps(serializable_tree)
    _write_text(json_tree, file_path)


def _save_json_forbidden(forbidden, file_path, start_path=None):
    if start_path:
        forbidden = {at.build_relative_path(path_key, start_path): exception
                     for path_key, exception in forbidden.items()}
    serializable_forbidden = {str(pathlib.PurePosixPath(path_key)): str(excep)
                              for path_key, excep in forbidden.items()}
    json_forbidden = json.dumps(serializable_forbidden)
    _write_text(json_forbidden, file_path)


def _write_text(content_string, file_path):
    try:
        file_path.write_text(content_string)
        print(f'{file_path.name} written on {file_path.parent}')
    except (PermissionError, Exception) as e:
        print(colorama.Fore.RED +
              f'Not authorized to write {file_path.name}'
              f' on {file_path.parent}: {type(e)}')
        temp_file_path = tempfile.mkstemp(prefix=file_path.stem + '_',
                                          suffix=file_path.suffix)[1]
        temp_file_path = pathlib.Path(temp_file_path)
        try:
            temp_file_path.write_text(content_string)
            print(f'{temp_file_path.name} written on {temp_file_path.parent}')
        except (PermissionError, Exception) as e:
            print(colorama.Fore.RED +
                  f'Not authorized to write {temp_file_path.name}'
                  f' on {temp_file_path.parent}: {type(e)}')
            print(colorama.Fore.RED +
                  f'{file_path.name} not written')
