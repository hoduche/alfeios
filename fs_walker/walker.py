import ast
import collections
import hashlib
import json
import os.path
import pathlib
import shutil
import tempfile

BLOCK_SIZE = 65536  # ie 64 Ko
FILE_TYPE = 'FILE'
DIR_TYPE = 'DIR'


def walk(path, exclusion=None):
    """
    Recursively walks through a root directory to list its content.
    It manages two data structures:
    listing : a collections.defaultdict(set) whose keys are tuples (hash, type, size)
              and values are list of pathlib.Path
    tree    : a dictionary whose keys are pathlib.Path and values are tuples (hash, type, size)
    in both data structures, the type distinguishes files from directories

    :param path: path of the root directory to parse
    :type path: pathlib.Path

    :param exclusion: list of directories and files not to parse
    :type exclusion: list of str

    :return: root directory listing
    :rtype: collections.defaultdict(set) = {(hash, type, int): {pathlib.Path}}

    :return: root directory tree
    :rtype: dict = {pathlib.Path: (hash, type, int)}
    """

    if not exclusion:
        exclusion = []

    listing = collections.defaultdict(set)
    tree = dict()
    forbidden = set()

    _recursive_walk(path, listing, tree, forbidden, exclusion)

    return listing, tree, forbidden


def _recursive_walk(path, listing, tree, forbidden, exclusion):
    if path.is_dir():
        dir_content_size = 0
        dir_content_hash_list = []
        for each_child in path.iterdir():
            try:
                if each_child.name not in exclusion and not each_child.is_symlink():
                    _recursive_walk(each_child, listing, tree, forbidden, exclusion)
                    if each_child not in forbidden:
                        dir_content_size += tree[each_child][2]
                        dir_content_hash_list.append(tree[each_child][0])
            except (PermissionError, Exception) as e:
                print(f'!!!!!!!!!!!!!!!!!!!!!! Exception: {type(e)} on: {each_child}')
                forbidden.add(each_child)
        dir_content = '\n'.join(sorted(dir_content_hash_list))
        dir_content_hash = hashlib.md5(dir_content.encode()).hexdigest()
        dir_content_key = (dir_content_hash, DIR_TYPE, dir_content_size)
        listing[dir_content_key].add(path)
        tree[path] = dir_content_key

    elif path.is_file() and path.suffix in ['.zip', '.tar', '.gztar', '.bztar', '.xztar']:
        try:
            temp_dir_path = pathlib.Path(tempfile.mkdtemp())
            shutil.unpack_archive(str(path), extract_dir=str(temp_dir_path))  # v3.7 accepts pathlib
            zip_listing, zip_tree, zip_forbidden = walk(temp_dir_path)
            append_listing(listing, zip_listing, path, temp_dir_path)
            append_tree(tree, zip_tree, path, temp_dir_path)
            append_forbidden(forbidden, zip_forbidden, path, temp_dir_path)
        except (shutil.ReadError, OSError, Exception) as e:
            print(f'!!!!!!!!!!!!!!!!!!!!!! Exception: {type(e)} on: {path}')
            forbidden.add(path)
            hash_and_index_file(path, listing, tree)

    elif path.is_file():
        hash_and_index_file(path, listing, tree)

    else:
        forbidden.add(path)


def hash_and_index_file(path, listing, tree):
    file_hasher = hashlib.md5()
    with path.open(mode='rb') as file_content:
        content_stream = file_content.read(BLOCK_SIZE)
        while len(content_stream) > 0:
            file_hasher.update(content_stream)
            content_stream = file_content.read(BLOCK_SIZE)
    file_content_hash = file_hasher.hexdigest()
    file_content_size = path.stat().st_size
    file_content_key = (file_content_hash, FILE_TYPE, file_content_size)
    listing[file_content_key].add(path)
    tree[path] = file_content_key


def get_duplicate(listing):
    duplicate = {k: v for k, v in listing.items() if len(v) >= 2}
    size_gain = sum([k[2] * (len(v) - 1) for k, v in duplicate.items()])
    duplicate_sorted_by_size = {k: v for (k, v) in sorted(duplicate.items(),
                                                           key=lambda i: i[0][2],
                                                           reverse=True)}
    result = collections.defaultdict(set, duplicate_sorted_by_size)
    return result, size_gain


def get_missing(old_listing, new_listing):
    non_included = {k: v for k, v in old_listing.items() if (k not in new_listing
                                                             and k[1] == FILE_TYPE)}
    result = collections.defaultdict(set, non_included)
    return result


def dump_json_listing(listing, file_path, start_path=None):
    """
    :param listing: listing to serialize in json
    :rtype listing: collections.defaultdict(set) = {(hash, type, int): {pathlib.Path}}

    :param file_path: path to create the json serialized listing
    :type file_path: pathlib.Path

    :param start_path: start path to remove from each path in the json serialized listing
    :type start_path: pathlib.Path
    """

    if start_path:
        listing = {tuple_key: {build_relative_path(path, start_path) for path in path_set}
                   for tuple_key, path_set in listing.items()}
    serializable_listing = {str(tuple_key): [str(pathlib.PurePosixPath(path)) for path in path_set]
                            for tuple_key, path_set in listing.items()}
    json_listing = json.dumps(serializable_listing)
    write_json(json_listing, file_path)


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


def dump_json_tree(tree, file_path, start_path=None):
    """
    :param tree: tree to serialize in json
    :rtype tree: dict = {pathlib.Path: (hash, type, int)}

    :param file_path: path to create the json serialized tree
    :type file_path: pathlib.Path

    :param start_path: start path to remove from each path in the json serialized tree
    :type start_path: pathlib.Path
    """

    if start_path:
        tree = {build_relative_path(path_key, start_path): tuple_value
                for path_key, tuple_value in tree.items()}
    serializable_tree = {str(pathlib.PurePosixPath(path_key)): tuple_value
                         for path_key, tuple_value in tree.items()}
    json_tree = json.dumps(serializable_tree)
    write_json(json_tree, file_path)


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


def dump_json_forbidden(forbidden, file_path, start_path=None):
    """
    :param forbidden: forbidden to serialize in json
    :rtype forbidden: set = {pathlib.Path}

    :param file_path: path to create the json serialized forbidden
    :type file_path: pathlib.Path

    :param start_path: start path to remove from each path in the json serialized forbidden
    :type start_path: pathlib.Path
    """

    if start_path:
        forbidden = {build_relative_path(path, start_path) for path in forbidden}
    serializable_forbidden = [str(pathlib.PurePosixPath(path)) for path in forbidden]
    json_forbidden = json.dumps(serializable_forbidden)
    write_json(json_forbidden, file_path)


def unify(listings, trees, forbiddens):
    tree = dict()  # = {pathlib.Path: (hash, type, int)}
    for each_tree in trees:
        for k, v in each_tree.items():
            if (not k in tree) or (tree[k][2] < v[2]):
                tree[k] = v
    listing = collections.defaultdict(set)  # = {(hash, type, int): {pathlib.Path}}

    for each_listing in listings:
        for k, v in each_listing.items():
            for each_v in v:
                if tree[each_v] == k:
                    listing[k].add(each_v)
    forbidden = set()

    for each_forbidden in forbiddens:
        forbidden.update(each_forbidden)

    return listing, tree, forbidden


def build_relative_path(absolute_path, start_path):
    return pathlib.Path(os.path.relpath(str(absolute_path), start=str(start_path)))  # v3.6 accepts pathlib


def write_json(json_string, file_path):
    try:
        file_path.write_text(json_string)
    except PermissionError as e:
        print(f'Not authorized to write {file_path.name} on {file_path.parent}')


def append_listing(listing, additional_listing, start_path, temp_path):
    for tuple_key, path_set in additional_listing.items():
        for each_path in path_set:
            each_relative_path = build_relative_path(each_path, temp_path)
            each_absolute_path = start_path / each_relative_path
            listing[tuple_key].add(each_absolute_path)


def append_tree(tree, additional_tree, start_path, temp_path):
    for path_key, tuple_value in additional_tree.items():
        relative_path_key = build_relative_path(path_key, temp_path)
        absolute_path_key = start_path / relative_path_key
        tree[absolute_path_key] = tuple_value


def append_forbidden(forbidden, additional_forbidden, start_path, temp_path):
    for path in additional_forbidden:
        relative_path = build_relative_path(path, temp_path)
        absolute_path = start_path / relative_path
        forbidden.add(absolute_path)
