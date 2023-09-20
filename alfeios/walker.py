import hashlib
import os
import pathlib
import shutil
import tempfile

import alfeios.tool as at

# Content data
HASH = 0  # content md5 hashcode
SIZE = 1  # content size in bytes
MTIME = 2  # last modification time


def walk(path, exclusion=None, cache=None, should_unzip=True, should_hash=True,
         pbar=None):
    """ Recursively walks through a root directory to index its content

    It manages two data structures:
    - tree: a dictionary whose keys are pathlib.Path and values are
        3-tuples (hash-code, size, modification-time)
        - hash-code is computed with the md5 hash function
        - size are expressed in bytes
        - modification-time are expressed in seconds since the Unix epoch
          00:00:00 UTC on 1 January 1970
    - forbidden: the no-access list - a dictionary whose keys are pathlib.Path
        and values are Exceptions

    Args:
        path (pathlib.Path): path to the root directory to parse
        exclusion (set of str): set of directories and files not to parse
        cache (tree): previous result to be used as cache to avoid re-hashing
                      if path, mtime and size are unchanged
        should_unzip (bool): flag to unzip and walk compressed files or not
        should_hash (bool): flag to hash content or not
        pbar (object): progress bar that must implement the interface:
            * update()       - mandatory
            * set_postfix()  - nice to have

    Possible future args:
        - find previous result inside or outside root folder: Yes, No
        - hash directories: Yes, No
        - handle progress bar (interface implemented by tqdm): Yes, No
        - handle results in color (interface implemented by colorama): Yes, No
        - write result inside root folder: Yes, No

    Returns:
        tree      : dict = {pathlib.Path: (hash-code, int, int)}
        forbidden : dict = {pathlib.Path: Exception}
    """

    if exclusion is None:
        exclusion = set()
    exclusion.update(['.alfeios', '.alfeios_expected'])

    if cache is None:  # todo check if this is pythonic
        cache = dict()

    tree = dict()
    forbidden = dict()

    #    path = path.resolve()  # todo remove if not used (understand before)
    path, original_cwd = at.change_dir_relative(path)  # todo understand better
    _recursive_walk(path, tree, forbidden, cache, exclusion,
                    should_unzip, should_hash, pbar)
    os.chdir(original_cwd)  # todo understand better

    return tree, forbidden


def _recursive_walk(path, tree, forbidden, cache, exclusion,
                    should_unzip, should_hash, pbar):

    # CASE 1: path is a directory
    # --------------------------------------------------
    if path.is_dir():
        for child in path.iterdir():
            try:
                if child.name not in exclusion and not child.is_symlink():
                    _recursive_walk(child, tree, forbidden, cache, exclusion,
                                    should_unzip, should_hash, pbar)
            except (PermissionError, Exception) as e:
                forbidden[child] = type(e)

    # CASE 2: path is a file
    # --------------------------------------------------
    elif path.is_file():
        if _has_same_file_in_cache(path, cache):
            _fill_tree_from_cache(tree, path, cache)
        else:
            _hash_and_index_file(path, tree, should_hash=should_hash,
                                 pbar=pbar)
        if at.is_compressed_file(path) and should_unzip:
            _walk_zip_file(tree, forbidden, path, exclusion, should_hash, pbar)

    # CASE 3: should not happen
    # --------------------------------------------------
    else:
        forbidden[path] = Exception


def _fill_tree_from_cache(tree, path, cache):
    tree[path] = cache[path]


def _walk_zip_file(tree, forbidden, path, exclusion, should_hash, pbar):
    temp_dir = pathlib.Path(tempfile.mkdtemp())
    try:
        at.unpack_archive_and_restore_mtime(path, extract_dir=temp_dir)
        # calls the recursion one step above with no cache to create
        # separate output that will be merged afterwards
        zt, zf = walk(temp_dir, exclusion, cache=dict(),
                      should_unzip=True,
                      should_hash=should_hash, pbar=pbar)
        _append_tree(tree, zt, path)
        _append_tree(forbidden, zf, path)
    except (shutil.ReadError, OSError, Exception) as e:
        forbidden[path] = type(e)
    finally:
        shutil.rmtree(temp_dir)


def _has_same_file_in_cache(path, cache):
    if path in cache:
        cached = cache[path]
        stat = path.stat()
        if stat.st_size == cached[SIZE] and stat.st_mtime == cached[MTIME]:
            return True
    return False


def _hash_and_index_file(path, tree, should_hash, pbar):
    block_size = 65536  # ie 64 KiB

    if should_hash:
        file_hasher = hashlib.md5()
        with path.open(mode='rb') as file_content:
            content_stream = file_content.read(block_size)
            while len(content_stream) > 0:
                file_hasher.update(content_stream)
                if pbar is not None:
                    pbar.set_postfix(file=str(path)[-10:], refresh=False)
                    pbar.update(len(content_stream))
                content_stream = file_content.read(block_size)
        hash_code = file_hasher.hexdigest()
    else:
        if pbar is not None:
            pbar.set_postfix(file=str(path)[-10:], refresh=False)
            pbar.update(1)
        hash_code = ''

    stat = path.stat()
    tree[path] = (hash_code, stat.st_size, stat.st_mtime)


def _append_tree(tree, additional_tree, start_path):
    for path, content in additional_tree.items():
        tree[start_path / path] = content
