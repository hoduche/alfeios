import ast
import collections
import colorama
import json
import pathlib
import tempfile

import alfeios.listing as al
import alfeios.tool as at
import alfeios.walker as aw


def save_json_tree(dir_path, tree, forbidden=None, start_path=None):
    """
    Save the 2 data structures of the index (tree and  forbidden) as json files,
    tagged with the current date and time, in a .alfeios subdirectory,
    inside the directory passed as first argument

    Args:
        dir_path (pathlib.Path): path to the directory where the index will be
            saved (in a .alfeios subdirectory)
        tree (dict = {pathlib.Path: (hash, type, int, int)}):
            tree to serialize
        forbidden (dict = {pathlib.Path: type(Exception)}):
            forbidden to serialize
        start_path (pathlib.Path): start path to remove from each path in the
                                   json serialized index

    Returns:
        pathlib.Path: serialized tree path
    """

    path = dir_path / '.alfeios'
    if not pathlib.Path(path).is_dir():
        pathlib.Path(path).mkdir()

    tag = at.build_current_datetime_tag()

    tree_path = path / (tag + '_tree.json')
    _save_json_tree(tree, tree_path, start_path)

    if len(forbidden) > 0:
        forbidden_path = path / (tag + '_forbidden.json')
        _save_json_forbidden(forbidden, forbidden_path, start_path)

    return tree_path


def load_json_tree(file_path, start_path=None):
    """
    Args:
        file_path (pathlib.Path): path to an existing json serialized tree
        start_path (pathlib.Path): start path to prepend to each relative path
                                   in the tree

    Returns:
        dict = {pathlib.Path: (hash, type, int, int)}
    """

    text_tree = file_path.read_text()
    json_tree = json.loads(text_tree)
    tree = {pathlib.Path(path): (content[aw.HASH],
                                 at.PathType(content[aw.TYPE]),
                                 content[aw.SIZE],
                                 content[aw.MTIME])
            for path, content in json_tree.items()}
    if start_path is not None:
        tree = {start_path / path: content for path, content in tree.items()}
    return tree


def load_last_json_tree(dir_path):
    """
    Args:
        dir_path (pathlib.Path): path to a root directory where previous
            index might have been saved (in a .alfeios subdirectory)

    Returns:
        dict = {pathlib.Path: (hash, type, int, int)}
    """

    cache_path = dir_path / '.alfeios'
    if not cache_path.exists():
        return dict()
    else:
        times = []
        for tree_path in cache_path.glob('*_tree.json'):
            times.append(at.read_datetime_tag(tree_path.name[:19]))
        max_time = max(times)
        max_time_tag = at.build_datetime_tag(max_time)
        last_json_tree = cache_path / (max_time_tag + '_tree.json')
        return load_json_tree(last_json_tree)


def save_json_listing(dir_path, listing, start_path=None):
    """
    Save listing as json file, tagged with the current date and time,
    in a .alfeios subdirectory, inside the directory passed as first argument

    Args:
        dir_path (pathlib.Path): path to the directory where the listing will be
            saved (in a .alfeios subdirectory)
        listing (collections.defaultdict(set) =
                {(hash, type, int): {(pathlib.Path, int)}}):
                listing to serialize
        start_path (pathlib.Path): start path to remove from each path in the
                                   json serialized index

    Returns:
        pathlib.Path: serialized listing path
    """

    path = dir_path / '.alfeios'
    if not pathlib.Path(path).is_dir():
        pathlib.Path(path).mkdir()

    listing_path = path / (at.build_current_datetime_tag() + '_listing.json')
    _save_json_listing(listing, listing_path, start_path)

    return listing_path


def load_json_listing(file_path, start_path=None):
    # todo: used only by tests -> move it to tests ?
    """
    Args:
        file_path (pathlib.Path): path to an existing json serialized listing
        start_path (pathlib.Path): start path to prepend to each relative path
                                   in the listing

    Returns:
        collections.defaultdict(set) =
            {(hash, type, int): {(pathlib.Path, int)}}
    """

    text_listing = file_path.read_text()
    json_listing = json.loads(text_listing)
    # ast.literal_eval allows transforming a string into a tuple
    dict_listing = {ast.literal_eval(content): pointers
                    for content, pointers in json_listing.items()}
    # we then cast the text elements into their expected types
    dict_listing = {(content[al.HASH],
                     at.PathType(content[al.TYPE]),
                     content[al.SIZE]): {(pathlib.Path(pointer[al.PATH]),
                                          pointer[al.MTIME])
                                         for pointer in pointers}
                    for content, pointers in dict_listing.items()}
    if start_path is not None:
        dict_listing = {content: {(start_path / pointer[al.PATH],
                                   pointer[al.MTIME])
                                  for pointer in pointers}
                        for content, pointers in dict_listing.items()}
    listing = collections.defaultdict(set, dict_listing)
    return listing


def _save_json_tree(tree, file_path, start_path=None):
    if start_path is not None:
        tree = {at.build_relative_path(path, start_path): content
                for path, content in tree.items()}
    serializable_tree = {str(pathlib.PurePosixPath(path)): list(content)
                         for path, content in tree.items()}
    json_tree = json.dumps(serializable_tree)
    _write_text(json_tree, file_path)


def _save_json_forbidden(forbidden, file_path, start_path=None):
    if start_path is not None:
        forbidden = {at.build_relative_path(path_key, start_path): exception
                     for path_key, exception in forbidden.items()}
    serializable_forbidden = {str(pathlib.PurePosixPath(path_key)): str(excep)
                              for path_key, excep in forbidden.items()}
    json_forbidden = json.dumps(serializable_forbidden)
    _write_text(json_forbidden, file_path)


def _save_json_listing(listing, file_path, start_path=None):
    if start_path is not None:
        listing = {content: {
            (at.build_relative_path(pointer[al.PATH], start_path),
             pointer[al.MTIME]) for pointer in pointers}
            for content, pointers in listing.items()}
    serializable_listing = {
        str((content[al.HASH], json.dumps(content[al.TYPE])[1:-1],
             content[al.SIZE])): [
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
