import ast
import collections
import hashlib
import io
import json
import os.path
import pathlib
import zipfile

BLOCK_SIZE = 65536  # ie 64 Ko
FILE_TYPE = 'FILE'
DIR_TYPE = 'DIR'


def crawl(path, exclusion=None):
    """
    Recursively crawls through a root directory to list its content.
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

    _recursive_crawl(Node(path), listing, tree, exclusion)

    return listing, tree


def _recursive_crawl(node, listing, tree, exclusion):
    if node.is_dir():
        dir_content_size = 0
        dir_content_hash_list = []
        for each_child in node.get_children():
            if each_child.get_name() not in exclusion:
                _recursive_crawl(each_child, listing, tree, exclusion)
                dir_content_size += tree[each_child][2]
                dir_content_hash_list.append(tree[each_child][0])
        dir_content = '\n'.join(sorted(dir_content_hash_list))
        dir_content_hash = hashlib.md5(dir_content.encode()).hexdigest()
        dir_content_key = (dir_content_hash, DIR_TYPE, dir_content_size)
        listing[dir_content_key].add(node)
        tree[node] = dir_content_key

    elif node.is_file():
        file_hasher = hashlib.md5()
        with node.open_rb() as file_content:
            content_stream = file_content.read(BLOCK_SIZE)
            while len(content_stream) > 0:
                file_hasher.update(content_stream)
                content_stream = file_content.read(BLOCK_SIZE)
        file_content_hash = file_hasher.hexdigest()
        file_content_size = node.get_size()
        file_content_key = (file_content_hash, FILE_TYPE, file_content_size)
        listing[file_content_key].add(node)
        tree[node] = file_content_key


def relative_path(absolute_path, start_path):
    return pathlib.Path(os.path.relpath(absolute_path, start=start_path))


def dump_json_listing(listing, file_path, start_path=None):
    """
    :param: listing to serialize in json
    :rtype: collections.defaultdict(set) = {(hash, type, int): {Node}}

    :param file_path: path to create the json serialized listing
    :type file_path: pathlib.Path

    :param start_path: start path to remove from each path in the json serialized listing
    :type start_path: pathlib.Path
    """

    listing = {tuple_key: {node.get_path() for node in node_set}
               for tuple_key, node_set in listing.items()}
    if start_path:
        listing = {tuple_key: {relative_path(path, start_path) for path in path_set}
                   for tuple_key, path_set in listing.items()}
    serializable_listing = {str(tuple_key): [str(pathlib.PurePosixPath(path)) for path in path_set]
                            for tuple_key, path_set in listing.items()}
    json_listing = json.dumps(serializable_listing)
    file_path.write_text(json_listing)


def load_json_listing(file_path, start_path):
    """
    :param file_path: path to an existing json serialized listing
    :type file_path: pathlib.Path

    :param start_path: start path to prepend to each relative path in the listing
    :type start_path: pathlib.Path

    :return: deserialized listing
    :rtype: collections.defaultdict(set) = {(hash, type, int): {Node}}
    """

    json_listing = file_path.read_text()
    serializable_listing = json.loads(json_listing)
    dict_listing = {ast.literal_eval(tuple_key): {pathlib.Path(path) for path in path_list}
                    for tuple_key, path_list in serializable_listing.items()}
    if start_path:
        dict_listing = {tuple_key: {start_path / path for path in path_list}
                        for tuple_key, path_list in dict_listing.items()}
    dict_listing = {tuple_key: {Node(path) for path in path_list}
                    for tuple_key, path_list in dict_listing.items()}
    listing = collections.defaultdict(set, dict_listing)
    return listing


def dump_json_tree(tree, file_path, start_path=None):
    """
    :param: tree to serialize in json
    :rtype: dict = {Node: (hash, type, int)}

    :param file_path: path to create the json serialized tree
    :type file_path: pathlib.Path

    :param start_path: start path to remove from each path in the json serialized tree
    :type start_path: pathlib.Path
    """

    tree = {node_key.get_path(): tuple_value
            for node_key, tuple_value in tree.items()}
    if start_path:
        tree = {relative_path(path_key, start_path): tuple_value
                for path_key, tuple_value in tree.items()}
    serializable_tree = {str(pathlib.PurePosixPath(path_key)): tuple_value
                         for path_key, tuple_value in tree.items()}
    json_tree = json.dumps(serializable_tree)
    file_path.write_text(json_tree)


def load_json_tree(file_path, start_path):
    """
    :param file_path: path to an existing json serialized tree
    :type file_path: pathlib.Path

    :param start_path: start path to prepend to each relative path in the tree
    :type start_path: pathlib.Path

    :return: deserialized tree
    :rtype: dict = {Node: (hash, type, int)}
    """

    json_tree = file_path.read_text()
    serializable_tree = json.loads(json_tree)
    tree = {pathlib.Path(path_key): tuple(value) for path_key, value in serializable_tree.items()}
    if start_path:
        tree = {start_path / path_key: tuple_value for path_key, tuple_value in tree.items()}
    tree = {Node(path_key): tuple_value for path_key, tuple_value in tree.items()}
    return tree


def unify(listings, trees):
    tree = dict()  # = {Node: (hash, type, int)}
    for each_tree in trees:
        for k, v in each_tree.items():
            if (not k in tree) or (tree[k][2] < v[2]):
                tree[k] = v
    listing = collections.defaultdict(set)  # = {(hash, type, int): {Node}}
    for each_listing in listings:
        for k, v in each_listing.items():
            for each_v in v:
                if tree[each_v] == k:
                    listing[k].add(each_v)
    return listing, tree


def get_duplicates(listing):
    duplicates = {k: v for k, v in listing.items() if len(v) >= 2}
    size_gain = sum([k[2] * (len(v) - 1) for k, v in duplicates.items()])
    duplicates_sorted_by_size = {k: v for (k, v) in sorted(duplicates.items(),
                                                           key=lambda i: i[0][2],
                                                           reverse=True)}
    result = collections.defaultdict(set, duplicates_sorted_by_size)
    return result, size_gain


def get_non_included(listing, listing_ref):
    non_included = {k: v for k, v in listing.items() if k not in listing_ref}
    result = collections.defaultdict(set, non_included)
    return result


class Node:

    def __init__(self, path):
        self.path = path

    def __hash__(self):
        return hash(self.path)

    def __eq__(self, other):
        return self.path == other.path

    def __repr__(self, other):
        return str(self.path)

    def get_path(self):
        return self.path

    def is_dir(self):
        return self.path.is_dir()

    def is_file(self):
        return self.path.is_file()

    def get_name(self):
        return self.path.name

    def get_size(self):
        return self.path.stat().st_size

    def get_children(self):
        for each_child in self.path.iterdir():
            yield Node(each_child)

    def open_rb(self):
        return open(self.path, mode='rb')


if __name__ == '__main__':
    desktop_path = pathlib.Path('C:/Users') / 'Henri-Olivier' / 'Desktop'
    p1 = Node(desktop_path)
    print(p1.get_name())
