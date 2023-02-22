import collections
import hashlib
import pathlib
import shutil
import tempfile

import alfeios.tool as at

# TODO:
"""
An attempt to build the index as a tree only.
This should simplify the code without loosing in performance or functionality.
Maybe to start with we could do :
- key = path
- value = (type, mtime, size, hash)

Here are the  different options to simple walk:
- walk inside compressed files: Yes, No
- write result inside root folder: Yes, No
- hash results: Yes, No
- use last result hashes if path, type, mtime and size are unchanged: Yes, No
- find previous result inside or outside root folder: Yes, No
- handle progress bar (interface implemented by tqdm): Yes, No
- handle results in color (interface implemented by colorama): Yes, No
- hash directories: Yes, No

"""


def walk(path, exclusion=None, should_hash=True, pbar=None):
    """ Recursively walks through a root directory to index its content

    It manages three data structures:
    - listing   : the most important one: a collections.defaultdict(set) whose
                  keys are 3-tuples (hash-code, path-type, size) and values are
                  set of 2-tuples (pathlib.Path, modification-time)
    - tree      : the listing dual: a dictionary whose keys are
                  2-tuples (pathlib.Path, modification-time) and values are
                  3-tuples (hash-code, path-type, size)
    - forbidden : the no-access list: a dictionary whose keys are pathlib.Path
                  and values are Exceptions
    in listing and tree, the path-type distinguishes files from directories
    size are expressed in bytes
    modification-time are expressed in nanoseconds
    since the Unix epoch 00:00:00 UTC on 1 January 1970

    Args:
        path (pathlib.Path): path to the root directory to parse
        exclusion (set of str): set of directories and files not to parse
        should_hash (bool): flag to hash content or not
        pbar (object): progress bar that must implement the interface:
                        * update()       - mandatory
                        * set_postfix()  - nice to have

    Returns:
        listing   : collections.defaultdict(set) =
                    {(hash-code, path-type, int): {(pathlib.Path, int)}}
        tree      : dict = {(pathlib.Path, int): (hash-code, path-type, int)}
        forbidden : dict = {pathlib.Path: Exception}
    """

    if exclusion is None:
        exclusion = set()
    exclusion.update(['.alfeios', '.alfeios_expected'])

    listing = collections.defaultdict(set)
    tree = dict()
    forbidden = dict()

    #    path = path.resolve()
    _recursive_walk(path, listing, tree, forbidden, exclusion,
                    should_hash, pbar)

    return listing, tree, forbidden


def _recursive_walk(path, listing, tree, forbidden, exclusion,
                    should_hash, pbar):
    if path.is_dir():
        dir_size = 0
        dir_hashes = []
        for child in path.iterdir():
            try:
                if child.name not in exclusion and not child.is_symlink():
                    _recursive_walk(child, listing, tree, forbidden,
                                    exclusion, should_hash, pbar)
                    if child not in forbidden:
                        # by construction of the recursion
                        # tree is guaranteed to contain child in its keys
                        # however zip file mtime is modified during the walk
                        # todo no longer the case so could be simplified !!!
                        child_content = [content for
                                         pointer, content in tree.items()
                                         if pointer[at.PATH] == child][0]
                        dir_size += child_content[at.SIZE]
                        dir_hashes.append(child_content[at.HASH])
            except (PermissionError, Exception) as e:
                forbidden[child] = type(e)
        if should_hash:
            concat_hashes = '\n'.join(sorted(dir_hashes))
            dir_hash_code = hashlib.md5(concat_hashes.encode()).hexdigest()
        else:
            dir_hash_code = ''
        dir_content = (dir_hash_code, at.PathType.DIR, dir_size)
        dir_pointer = (path, path.stat().st_mtime)
        listing[dir_content].add(dir_pointer)
        tree[dir_pointer] = dir_content

    elif path.is_file() and path.suffix in ['.zip', '.tar', '.gztar', '.bztar',
                                            '.xztar']:
        temp_dir_path = pathlib.Path(tempfile.mkdtemp())
        try:
            shutil.unpack_archive(path, extract_dir=temp_dir_path)
            at.restore_mtime_after_unpack(path, extract_dir=temp_dir_path)
            # calls the recursion one step above to create separate output
            # that will be merged afterwards
            zl, zt, zf = walk(temp_dir_path, exclusion,
                              should_hash=should_hash, pbar=pbar)
            _append_listing(listing, zl, path, temp_dir_path)
            _append_tree(tree, zt, path, temp_dir_path)
            _append_forbidden(forbidden, zf, path, temp_dir_path)
        except (shutil.ReadError, OSError, Exception) as e:
            forbidden[path] = type(e)
            _hash_and_index_file(path, listing, tree,
                                 should_hash=should_hash, pbar=pbar)
        finally:
            shutil.rmtree(temp_dir_path)

    elif path.is_file():
        _hash_and_index_file(path, listing, tree,
                             should_hash=should_hash, pbar=pbar)

    else:
        forbidden[path] = Exception


BLOCK_SIZE = 65536  # ie 64 KiB


def _hash_and_index_file(path, listing, tree, should_hash, pbar):
    if should_hash:
        file_hasher = hashlib.md5()
        with path.open(mode='rb') as file_content:
            content_stream = file_content.read(BLOCK_SIZE)
            while len(content_stream) > 0:
                file_hasher.update(content_stream)
                if pbar is not None:
                    pbar.set_postfix(file=str(path)[-10:], refresh=False)
                    pbar.update(len(content_stream))
                content_stream = file_content.read(BLOCK_SIZE)
        hash_code = file_hasher.hexdigest()
    else:
        if pbar is not None:
            pbar.set_postfix(file=str(path)[-10:], refresh=False)
            pbar.update(1)
        hash_code = ''
    size = path.stat().st_size
    mtime = path.stat().st_mtime
    content = (hash_code, at.PathType.FILE, size)
    pointer = (path, mtime)
    listing[content].add(pointer)
    tree[pointer] = content


def get_duplicate(listing):
    duplicate = {content: pointers for content, pointers in listing.items()
                 if len(pointers) >= 2}
    size_gain = sum([content[at.SIZE] * (len(pointers) - 1)
                     for content, pointers in duplicate.items()])
    duplicate_sorted_by_size = {content: pointers for (content, pointers)
                                in sorted(duplicate.items(),
                                          key=lambda item: item[0][at.SIZE],
                                          reverse=True)}
    result = collections.defaultdict(set, duplicate_sorted_by_size)
    return result, size_gain


def get_missing(old_listing, new_listing):
    non_included = {content: pointers for content, pointers
                    in old_listing.items() if content not in new_listing}
    result = collections.defaultdict(set, non_included)
    return result


def unify(listings, trees, forbiddens):
    # {(pathlib.Path, int): (hash-code, path-type, int)}
    unified_tree = dict()
    for tree in trees:
        for pointer, content in tree.items():
            if (pointer not in unified_tree) or \
                    (unified_tree[pointer][at.SIZE] < content[at.SIZE]):
                unified_tree[pointer] = content

    # {(hash-code, path-type, int): {(pathlib.Path, int)}}
    unified_listing = collections.defaultdict(set)
    for each_listing in listings:
        for content, pointers in each_listing.items():
            for pointer in pointers:
                if unified_tree[pointer] == content:
                    unified_listing[content].add(pointer)

    # {pathlib.Path: Exception}
    forbidden = dict()
    for each_forbidden in forbiddens:
        forbidden.update(each_forbidden)

    return unified_listing, unified_tree, forbidden


def tree_to_listing(tree):
    listing = collections.defaultdict(set)
    for pointer, content in tree.items():
        listing[content].add(pointer)
    return listing


def listing_to_tree(listing):
    tree = dict()
    for content, pointers in listing.items():
        for pointer in pointers:
            tree[pointer] = content
    return tree


def _append_listing(listing, additional_listing, start_path, temp_path):
    for content, pointer_set in additional_listing.items():
        for pointer in pointer_set:
            relative_path = at.build_relative_path(pointer[at.PATH], temp_path)
            absolute_path = start_path / relative_path
            listing[content].add((absolute_path, pointer[at.MTIME]))


def _append_tree(tree, additional_tree, start_path, temp_path):
    for pointer, content in additional_tree.items():
        relative_path = at.build_relative_path(pointer[at.PATH], temp_path)
        absolute_path = start_path / relative_path
        tree[(absolute_path, pointer[at.MTIME])] = content


def _append_forbidden(forbidden, additional_forbidden, start_path, temp_path):
    for path, exception_value in additional_forbidden:
        relative_path = at.build_relative_path(path, temp_path)
        absolute_path = start_path / relative_path
        forbidden[absolute_path] = exception_value
