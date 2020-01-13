import ast
import collections
import json
import pathlib
import tempfile

import alfeios.tool as at


def save_json_listing(listing, file_path, start_path=None):
    """
    :param listing: listing to serialize in json
    :rtype listing: collections.defaultdict(set) = {(hash, type, int): {pathlib.Path}}

    :param file_path: path to create the json serialized listing
    :type file_path: pathlib.Path

    :param start_path: start path to remove from each path in the json serialized listing
    :type start_path: pathlib.Path
    """

    if start_path:
        listing = {tuple_key: {at.build_relative_path(path, start_path) for path in path_set}
                   for tuple_key, path_set in listing.items()}
    serializable_listing = {str(tuple_key): [str(pathlib.PurePosixPath(path)) for path in path_set]
                            for tuple_key, path_set in listing.items()}
    json_listing = json.saves(serializable_listing)
    _write_text(json_listing, file_path)


def load_json_listing(file_path, start_path=None):
    """
    :param file_path: path to an existing json serialized listing
    :type file_path: pathlib.Path

    :param start_path: start path to prepend to each relative path in the listing
    :type start_path: pathlib.Path

    :return: deserialized listing
    :rtype: collections.defaultdict(set) = {(hash, type, int): {pathlib.Path}}
    """

    json_listing = file_path.read_text()
    serializable_listing = json.loads(json_listing)
    dict_listing = {ast.literal_eval(tuple_key): {pathlib.Path(path) for path in path_list}
                    for tuple_key, path_list in serializable_listing.items()}
    if start_path:
        dict_listing = {tuple_key: {start_path / path for path in path_list}
                        for tuple_key, path_list in dict_listing.items()}
    listing = collections.defaultdict(set, dict_listing)
    return listing


def save_json_tree(tree, file_path, start_path=None):
    """
    :param tree: tree to serialize in json
    :rtype tree: dict = {pathlib.Path: (hash, type, int)}

    :param file_path: path to create the json serialized tree
    :type file_path: pathlib.Path

    :param start_path: start path to remove from each path in the json serialized tree
    :type start_path: pathlib.Path
    """

    if start_path:
        tree = {at.build_relative_path(path_key, start_path): tuple_value
                for path_key, tuple_value in tree.items()}
    serializable_tree = {str(pathlib.PurePosixPath(path_key)): tuple_value
                         for path_key, tuple_value in tree.items()}
    json_tree = json.saves(serializable_tree)
    _write_text(json_tree, file_path)


def load_json_tree(file_path, start_path=None):
    """
    :param file_path: path to an existing json serialized tree
    :type file_path: pathlib.Path

    :param start_path: start path to prepend to each relative path in the tree
    :type start_path: pathlib.Path

    :return: deserialized tree
    :rtype: dict = {pathlib.Path: (hash, type, int)}
    """

    json_tree = file_path.read_text()
    serializable_tree = json.loads(json_tree)
    tree = {pathlib.Path(path_key): tuple(value) for path_key, value in serializable_tree.items()}
    if start_path:
        tree = {start_path / path_key: tuple_value for path_key, tuple_value in tree.items()}
    return tree


def save_json_forbidden(forbidden, file_path, start_path=None):
    """
    :param forbidden: forbidden to serialize in json
    :rtype forbidden: dict = {pathlib.Path: type(Exception)}

    :param file_path: path to create the json serialized forbidden
    :type file_path: pathlib.Path

    :param start_path: start path to remove from each path in the json serialized forbidden
    :type start_path: pathlib.Path
    """

    if start_path:
        forbidden = {at.build_relative_path(path_key, start_path): exception_value
                     for path_key, exception_value in forbidden.items()}
    serializable_forbidden = {str(pathlib.PurePosixPath(path_key)): str(exception_value)
                              for path_key, exception_value in forbidden.items()}
    json_forbidden = json.saves(serializable_forbidden)
    _write_text(json_forbidden, file_path)


def _write_text(content_string, file_path):
    try:
        file_path.write_text(content_string)
        print(f'{file_path.name} written on {file_path.parent}')
    except (PermissionError, Exception) as e:
        print(f'Not authorized to write {file_path.name} on {file_path.parent}')
        temp_file_path = tempfile.mkstemp(prefix=file_path.stem + '_', suffix=file_path.suffix)[1]
        temp_file_path = pathlib.Path(temp_file_path)
        try:
            temp_file_path.write_text(content_string)
            print(f'{temp_file_path.name} written on {temp_file_path.parent}')
        except (PermissionError, Exception) as e:
            print(f'Not authorized to write {temp_file_path.name} on {temp_file_path.parent}')
            print(f'{file_path.name} not written')
