import hashlib
import pathlib
import shutil
import tempfile

import alfeios.tool as at

# TODO:
"""
Here are the  different options to simple walk:

- use last result hashes if path, type, mtime and size are unchanged: Yes, No
- hash results: Yes, No

- find previous result inside or outside root folder: Yes, No
- walk inside compressed files: Yes, No
- hash directories: Yes, No

- handle progress bar (interface implemented by tqdm): Yes, No
- handle results in color (interface implemented by colorama): Yes, No

- write result inside root folder: Yes, No
"""

# Content data
HASH = 0  # content md5 hashcode
TYPE = 1  # content type : PathType.FILE or PathType.DIR
SIZE = 2  # content size in bytes
MTIME = 3  # last modification time


def walk(path, exclusion=None, cache=None, should_hash=True, pbar=None):
    """ Recursively walks through a root directory to index its content

    It manages two data structures:
    - tree: a dictionary whose keys are pathlib.Path and values are
        4-tuples (hash-code, path-type, size, modification-time)
        - hash-code is computed with the md5 hash function
        - path-type distinguishes files from directories
        - size are expressed in bytes
        - modification-time are expressed in seconds since the Unix epoch
          00:00:00 UTC on 1 January 1970
    - forbidden: the no-access list - a dictionary whose keys are pathlib.Path
        and values are Exceptions

    Args:
        path (pathlib.Path): path to the root directory to parse
        exclusion (set of str): set of directories and files not to parse
        cache (tree): previous result to be used as cache to avoid re-hashing
                      if path, type, mtime and size are unchanged
        should_hash (bool): flag to hash content or not
        pbar (object): progress bar that must implement the interface:
            * update()       - mandatory
            * set_postfix()  - nice to have

    Returns:
        tree      : dict = {pathlib.Path: (hash-code, path-type, int, int)}
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
    _recursive_walk(path, tree, forbidden, cache, exclusion, should_hash, pbar)

    return tree, forbidden


def _recursive_walk(path, tree, forbidden, cache, exclusion, should_hash, pbar):

    # CASE 0: path is in cache
    # --------------------------------------------------
    if path in cache:
        cached_content = cache[path]
        stat = path.stat()
        if at.get_path_type(path) == cached_content[TYPE] and \
                stat.st_size == cached_content[SIZE] and \
                stat.st_mtime == cached_content[MTIME]:
            tree[path] = cached_content
            return

    # CASE 1: path is a directory
    # --------------------------------------------------
    if path.is_dir():
        dir_size = 0
        dir_hashes = []
        for child in path.iterdir():
            try:
                if child.name not in exclusion and not child.is_symlink():
                    _recursive_walk(child, tree, forbidden, cache,
                                    exclusion, should_hash, pbar)
                    if child not in forbidden:
                        # by construction of the recursion
                        # tree is guaranteed to contain child in its keys
                        child_content = tree[child]
                        dir_size += child_content[SIZE]
                        dir_hashes.append(child_content[HASH])
            except (PermissionError, Exception) as e:
                forbidden[child] = type(e)
        if should_hash:
            concat_hashes = '\n'.join(sorted(dir_hashes))
            dir_hash = hashlib.md5(concat_hashes.encode()).hexdigest()
        else:
            dir_hash = ''
        tree[path] = (dir_hash, at.PathType.DIR, dir_size, path.stat().st_mtime)

    # CASE 2: path is a compressed file
    # --------------------------------------------------
    elif at.is_compressed_file(path):
        temp_dir = pathlib.Path(tempfile.mkdtemp())
        try:
            at.unpack_archive_and_restore_mtime(path, extract_dir=temp_dir)
            # calls the recursion one step above to create separate output
            # that will be merged afterwards
            zt, zf = walk(temp_dir, exclusion, cache=cache,
                          should_hash=should_hash, pbar=pbar)
            _append_tree(tree, zt, path, temp_dir)
            _append_tree(forbidden, zf, path, temp_dir)
        except (shutil.ReadError, OSError, Exception) as e:
            forbidden[path] = type(e)
            _hash_and_index_file(path, tree, should_hash=should_hash, pbar=pbar)
        finally:
            shutil.rmtree(temp_dir)

    # CASE 3: path is a standard (uncompressed) file
    # --------------------------------------------------
    elif path.is_file():
        _hash_and_index_file(path, tree, should_hash=should_hash, pbar=pbar)

    # CASE 4: should not happen
    # --------------------------------------------------
    else:
        forbidden[path] = Exception


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
    tree[path] = (hash_code, at.PathType.FILE, stat.st_size, stat.st_mtime)


def _append_tree(tree, additional_tree, start_path, temp_path):
    for path, content in additional_tree.items():
        relative_path = at.build_relative_path(path, temp_path)
        absolute_path = start_path / relative_path
        tree[absolute_path] = content
