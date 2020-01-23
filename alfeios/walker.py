import collections
import enum
import hashlib
import os
import pathlib
import shutil
import tempfile

import tqdm

import alfeios.tool as at


BLOCK_SIZE = 65536  # ie 64 Ko


class PathType(str, enum.Enum):
    FILE = 'FILE'
    DIR = 'DIR'


def compute_size(path, create_pbar=False):
    if create_pbar:
        pbar = tqdm.tqdm(unit=' files')
    nb_files = 0
    total_size = 0
    for dir_path_string, subdir_names, file_names in os.walk(path):
        for file_name in file_names:
            file_path = pathlib.Path(dir_path_string) / file_name
            file_size = file_path.stat().st_size
            nb_files += 1
            total_size += file_size
            if create_pbar:
                pbar.update()
    if create_pbar:
        pbar.close()
    return nb_files, total_size


def walk(path, exclusion=None, create_pbar=False):
    """ Recursively walks through a root directory to index its content

    It manages three data structures:
    - listing   : the most important one: a collections.defaultdict(set) whose
                  keys are 3-tuples (hash-code, path-type, size) and values are
                  list of pathlib.Path
    - tree      : the listing dual: a dictionary whose keys are pathlib.Path
                  and values are 3-tuples (hash-code, path-type, size)
    - forbidden : the no-access list: a dictionary whose keys are pathlib.Path
                  and values are Exceptions
    in listing and tree, the path-type distinguishes files from directories

    Args:
        path (pathlib.Path): path to the root directory to parse
        exclusion (list of str): list of directories and files not to parse

    Returns:
        listing   : collections.defaultdict(set) =
                    {(hash-code, path-type, int): {pathlib.Path}}
        tree      : dict = {pathlib.Path: (hash-code, path-type, int)}
        forbidden : dict = {pathlib.Path: Exception}
    """

    if not exclusion:
        exclusion = []

    listing = collections.defaultdict(set)
    tree = dict()
    forbidden = dict()

    nb_files, total_size = compute_size(path, create_pbar)

#    path = path.resolve()
    if create_pbar:
        pbar = tqdm.tqdm(total=2*total_size, desc='indexing',
                         unit='B', unit_scale=True, unit_divisor=1024)
    else:
        pbar = None
    _recursive_walk(path, listing, tree, forbidden, exclusion, pbar)
    if create_pbar:
        pbar.close()

    return listing, tree, forbidden


def _recursive_walk(path, listing, tree, forbidden, exclusion, pbar):
    if path.is_dir():
        dir_content_size = 0
        dir_content_hash_list = []
        for each_child in path.iterdir():
            try:
                if each_child.name not in exclusion and\
                        not each_child.is_symlink():
                    _recursive_walk(each_child, listing, tree, forbidden,
                                    exclusion, pbar)
                    if each_child not in forbidden:
                        dir_content_size += tree[each_child][2]
                        dir_content_hash_list.append(tree[each_child][0])
            except (PermissionError, Exception) as e:
                forbidden[each_child] = type(e)
        dir_content = '\n'.join(sorted(dir_content_hash_list))
        dir_content_hash = hashlib.md5(dir_content.encode()).hexdigest()
        dir_content_key = (dir_content_hash, PathType.DIR, dir_content_size)
        listing[dir_content_key].add(path)
        tree[path] = dir_content_key

    elif path.is_file() and path.suffix in ['.zip', '.tar', '.gztar', '.bztar',
                                            '.xztar']:
        temp_dir_path = pathlib.Path(tempfile.mkdtemp())
        try:
            # v3.7 accepts pathlib as extract_dir=
            shutil.unpack_archive(str(path), extract_dir=str(temp_dir_path))
            zip_listing, zip_tree, zip_forbidden = walk(temp_dir_path,
                                                        create_pbar=False)
            _append_listing(listing, zip_listing, path, temp_dir_path)
            _append_tree(tree, zip_tree, path, temp_dir_path)
            _append_forbidden(forbidden, zip_forbidden, path, temp_dir_path)
        except (shutil.ReadError, OSError, Exception) as e:
            forbidden[path] = type(e)
            _hash_and_index_file(path, listing, tree, pbar)
        finally:
            shutil.rmtree(temp_dir_path)

    elif path.is_file():
        _hash_and_index_file(path, listing, tree, pbar)

    else:
        forbidden[path] = Exception


def _hash_and_index_file(path, listing, tree, pbar):
    file_hasher = hashlib.md5()
    with path.open(mode='rb') as file_content:
        content_stream = file_content.read(BLOCK_SIZE)
        while len(content_stream) > 0:
            file_hasher.update(content_stream)
            content_stream = file_content.read(BLOCK_SIZE)
            if pbar:
                pbar.set_postfix(file=str(path)[-10:], refresh=False)
                pbar.update(BLOCK_SIZE)
    file_content_hash = file_hasher.hexdigest()
    file_content_size = path.stat().st_size
    file_content_key = (file_content_hash, PathType.FILE, file_content_size)
    listing[file_content_key].add(path)
    tree[path] = file_content_key


def get_duplicate(listing):
    duplicate = {k: v for k, v in listing.items() if len(v) >= 2}
    size_gain = sum([k[2] * (len(v) - 1) for k, v in duplicate.items()])
    duplicate_sorted_by_size = {k: v for (k, v)
                                in sorted(duplicate.items(),
                                          key=lambda i: i[0][2],
                                          reverse=True)}
    result = collections.defaultdict(set, duplicate_sorted_by_size)
    return result, size_gain


def get_missing(old_listing, new_listing):
    non_included = {k: v for k, v in old_listing.items()
                    if (k not in new_listing and k[1] == PathType.FILE)}
    result = collections.defaultdict(set, non_included)
    return result


def unify(listings, trees, forbiddens):
    tree = dict()  # = {pathlib.Path: (hash-code, path-type, int)}
    for each_tree in trees:
        for k, v in each_tree.items():
            if (k not in tree) or (tree[k][2] < v[2]):
                tree[k] = v

    listing = collections.defaultdict(set)
    # = {(hash-code, path-type, int): {pathlib.Path}}
    for each_listing in listings:
        for k, v in each_listing.items():
            for each_v in v:
                if tree[each_v] == k:
                    listing[k].add(each_v)

    forbidden = dict()  # = {pathlib.Path: Exception}
    for each_forbidden in forbiddens:
        forbidden.update(each_forbidden)

    return listing, tree, forbidden


def _append_listing(listing, additional_listing, start_path, temp_path):
    for tuple_key, path_set in additional_listing.items():
        for each_path in path_set:
            each_relative_path = at.build_relative_path(each_path, temp_path)
            each_absolute_path = start_path / each_relative_path
            listing[tuple_key].add(each_absolute_path)


def _append_tree(tree, additional_tree, start_path, temp_path):
    for path_key, tuple_value in additional_tree.items():
        relative_path_key = at.build_relative_path(path_key, temp_path)
        absolute_path_key = start_path / relative_path_key
        tree[absolute_path_key] = tuple_value


def _append_forbidden(forbidden, additional_forbidden, start_path, temp_path):
    for path_key, exception_value in additional_forbidden:
        relative_path_key = at.build_relative_path(path_key, temp_path)
        absolute_path_key = start_path / relative_path_key
        forbidden[absolute_path_key] = exception_value


if __name__ == '__main__':
    path = pathlib.Path('C:\\netBeansProjects')
    listing, tree, forbidden = walk(path, create_pbar=True)
