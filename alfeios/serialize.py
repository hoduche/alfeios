import ast
import collections
import sys

import colorama
import json
import pathlib
import tempfile

import alfeios.listing as al
import alfeios.tool as at
import alfeios.walker as aw


def save_json_tree(dir_path, tree, forbidden=None):
    """
    Save the 2 data structures of the index (tree and  forbidden) as json files
    tagged with the current date and time, in a .alfeios subdirectory,
    inside the directory passed as first argument

    Args:
        dir_path (pathlib.Path): path to the directory where the index will be
            saved (in a .alfeios subdirectory)
        tree (dict = {pathlib.Path: (hash, int, int)}):
            tree to serialize
        forbidden (dict = {pathlib.Path: type(Exception)}):
            forbidden to serialize

    Returns:
        pathlib.Path: serialized tree path
    """

    path = dir_path / '.alfeios'
    if not pathlib.Path(path).is_dir():
        pathlib.Path(path).mkdir()

    tag = at.build_current_datetime_tag()

    tree_path = path / (tag + '_tree.json')
    _save_json_tree(tree, tree_path)

    if len(forbidden) > 0:
        forbidden_path = path / (tag + '_forbidden.json')
        _save_json_forbidden(forbidden, forbidden_path)

    return tree_path


def load_json_tree(file_path):
    """
    Args:
        file_path (pathlib.Path): path to an existing json serialized tree

    Returns:
        dict = {pathlib.Path: (hash, int, int)}
    """

    text_tree = file_path.read_text()
    json_tree = json.loads(text_tree)
    tree = {pathlib.Path(path): (content[aw.HASH],
                                 content[aw.SIZE],
                                 content[aw.MTIME])
            for path, content in json_tree.items()}
    return tree


def load_last_json_tree(dir_path):
    """
    Args:
        dir_path (pathlib.Path): path to a root directory where previous
            index might have been saved (in a .alfeios subdirectory)

    Returns:
        dict = {pathlib.Path: (hash, int, int)}
    """

    try:
        cache_path = dir_path / '.alfeios'
        times = []
        for tree_path in cache_path.glob('*_tree.json'):
            times.append(at.read_datetime_tag(tree_path.name[:19]))
        max_time = max(times)
        max_time_tag = at.build_datetime_tag(max_time)
        last_json_tree = cache_path / (max_time_tag + '_tree.json')
        return load_json_tree(last_json_tree)
    except (ValueError, IndexError, Exception) as e:
        print(colorama.Fore.RED +
              f'No cache readable in {dir_path.name}'
              f' due to: {type(e)}', file=sys.stderr)
        return dict()


def save_json_listing(dir_path, listing):
    """
    Save listing as json file, tagged with the current date and time,
    in a .alfeios subdirectory, inside the directory passed as first argument

    Args:
        dir_path (pathlib.Path): path to the directory where the listing will
            be saved (in a .alfeios subdirectory)
        listing (collections.defaultdict(set) =
                {(hash, int): {(pathlib.Path, int)}}):
                listing to serialize

    Returns:
        pathlib.Path: serialized listing path
    """

    path = dir_path / '.alfeios'
    if not pathlib.Path(path).is_dir():
        pathlib.Path(path).mkdir()

    listing_path = path / (at.build_current_datetime_tag() + '_listing.json')
    _save_json_listing(listing, listing_path)

    return listing_path


def load_json_listing(file_path):
    # todo: used only by tests -> move it to tests ?
    """
    Args:
        file_path (pathlib.Path): path to an existing json serialized listing

    Returns:
        collections.defaultdict(set) =
            {(hash, int): {(pathlib.Path, int)}}
    """

    text_listing = file_path.read_text()
    json_listing = json.loads(text_listing)
    # ast.literal_eval allows transforming a string into a tuple
    dict_listing = {ast.literal_eval(content): pointers
                    for content, pointers in json_listing.items()}
    # we then cast the text elements into their expected types
    dict_listing = {(content[al.HASH],
                     content[al.SIZE]): {(pathlib.Path(pointer[al.PATH]),
                                          pointer[al.MTIME])
                                         for pointer in pointers}
                    for content, pointers in dict_listing.items()}
    listing = collections.defaultdict(set, dict_listing)
    return listing


def _save_json_tree(tree, file_path):
    serializable_tree = {str(pathlib.PurePosixPath(path)): list(content)
                         for path, content in tree.items()}
    json_tree = json.dumps(serializable_tree)
    _write_text(json_tree, file_path)


def _save_json_forbidden(forbidden, file_path):
    serializable_forbidden = {str(pathlib.PurePosixPath(path_key)): str(excep)
                              for path_key, excep in forbidden.items()}
    json_forbidden = json.dumps(serializable_forbidden)
    _write_text(json_forbidden, file_path)


def _save_json_listing(listing, file_path):
    serializable_listing = {
        str((content[al.HASH], content[al.SIZE])): [
            [str(pathlib.PurePosixPath(pointer[al.PATH])), pointer[al.MTIME]]
            for pointer in pointers]
        for content, pointers in listing.items()}
    json_listing = json.dumps(serializable_listing)
    _write_text(json_listing, file_path)


def _write_text(content_string, file_path):
    try:
        file_path.write_text(content_string)
        print(f'{file_path.name} written on {file_path.parent}')
    except (PermissionError, Exception) as e:
        print(colorama.Fore.RED +
              f'Not authorized to write {file_path.name}'
              f' on {file_path.parent}: {type(e)}', file=sys.stderr)
        temp_file_path = tempfile.mkstemp(prefix=file_path.stem + '_',
                                          suffix=file_path.suffix)[1]
        temp_file_path = pathlib.Path(temp_file_path)
        try:
            temp_file_path.write_text(content_string)
            print(f'{temp_file_path.name} written on {temp_file_path.parent}')
        except (PermissionError, Exception) as e:
            print(colorama.Fore.RED +
                  f'Not authorized to write {temp_file_path.name}'
                  f' on {temp_file_path.parent}: {type(e)}', file=sys.stderr)
            print(colorama.Fore.RED +
                  f'{file_path.name} not written', file=sys.stderr)
