import ast
import collections
import hashlib
import json
import pathlib

BLOCK_SIZE = 65536  # ie 64 Ko
FILE_TYPE = 'FILE'
DIR_TYPE = 'DIR'


def crawl(path, json_listing_path=None, json_tree_path=None, exclusion=[]):
    """
    Recursively crawls through a root directory to list its content.
    It manages two data structures:
    listing : a collections.defaultdict(list) whose keys are tuples (hash, type, size)
              and values are list of pathlib.Path
    tree    : a dictionary whose keys are pathlib.Path and values are tuples (hash, type, size)
    in both data structures, the type distinguishes files from directories

    :param path: path of the root directory to parse
    :type path: pathlib.Path

    :param json_listing_path: path to an existing json serialized listing to append to
    :type json_listing_path: pathlib.Path

    :param json_tree_path: path to an existing json serialized tree to append to
    :type json_tree_path: pathlib.Path

    :param exclusion: list of directories and files not to parse
    :type exclusion: list of pathlib.Path

    :return: root directory listing and tree
    :rtype: collections.defaultdict(list), dict
    """
    if json_listing_path:
        listing = load_json_listing(json_listing_path)
    else:
        listing = collections.defaultdict(list)  # {(hash, type, int): [pathlib.Path]}
    if json_tree_path:
        tree = load_json_tree(json_tree_path)
    else:
        tree = dict()  # {pathlib.Path: (hash, type, int)}
    _recursive_crawl(path, listing, tree, exclusion)
    return listing, tree


def _recursive_crawl(path, listing, tree, exclusion):
    for each in path.iterdir():
        if each not in exclusion:
            if each.is_dir():
                _recursive_crawl(each, listing, tree, exclusion)
                dir_content_size = 0
                dir_content_hash_list = []
                for each_child in each.iterdir():
                    dir_content_size += tree[each_child][2]
                    dir_content_hash_list.append(tree[each_child][0])
                dir_content = '\n'.join(sorted(dir_content_hash_list))
                dir_content_hash = hashlib.md5(dir_content.encode()).hexdigest()
                dir_content_key = (dir_content_hash, DIR_TYPE, dir_content_size)
                listing[dir_content_key].append(each)
                tree[each] = dir_content_key
            elif each.is_file():
                file_hasher = hashlib.md5()
                with open(each, 'rb') as file_content:
                    content_stream = file_content.read(BLOCK_SIZE)
                    while len(content_stream) > 0:
                        file_hasher.update(content_stream)
                        content_stream = file_content.read(BLOCK_SIZE)
                file_content_hash = file_hasher.hexdigest()
                file_content_size = each.stat().st_size
                file_content_key = (file_content_hash, FILE_TYPE, file_content_size)
                listing[file_content_key].append(each)
                tree[each] = file_content_key


def dump_json_listing(listing, file_path):
    serializable_listing = {str(tuple_key): [str(path) for path in path_list]
                            for tuple_key, path_list in listing.items()}
    json_listing = json.dumps(serializable_listing)
    file_path.write_text(json_listing)


def load_json_listing(file_path):
    json_listing = file_path.read_text()
    serializable_listing = json.loads(json_listing)
    dict_listing = {ast.literal_eval(tuple_key): [pathlib.Path(path) for path in path_list]
                    for tuple_key, path_list in serializable_listing.items()}
    listing = collections.defaultdict(list, dict_listing)
    return listing


def dump_json_tree(tree, file_path):
    serializable_tree = {str(path_key): tuple_value for path_key, tuple_value in tree.items()}
    json_tree = json.dumps(serializable_tree)
    file_path.write_text(json_tree)


def load_json_tree(file_path):
    json_tree = file_path.read_text()
    serializable_tree = json.loads(json_tree)
    tree = {pathlib.Path(path_key): tuple(value) for path_key, value in serializable_tree.items()}
    return tree


if __name__ == '__main__':
    project_path = pathlib.Path(__file__).resolve().expanduser().parent.parent
    tests_data_path = project_path / 'tests' / 'data'

## todo   listing, hashes, sizes = main(project_path.parent) crashes on .git
## todo   replace os.walk by a personal recursion to avoid certain files/directory (like .gitignore)

    listing2, tree2 = crawl(tests_data_path / 'Folder0')
    dump_json_listing(listing2, tests_data_path / 'Folder0_listing.json')
    dump_json_tree(tree2, tests_data_path / 'Folder0_tree.json')
