import collections

import alfeios.walker as aw

# Content data
HASH = 0   # content md5 hashcode
SIZE = 1   # content size in bytes

# Pointer data
PATH = 0   # filesystem path
MTIME = 1  # last modification time


def tree_to_listing(tree):
    """ Converts a directory tree index to a listing:
    a collections.defaultdict(set) whose keys are 2-tuples (hash-code, size)
    and values are set of 2-tuples (pathlib.Path, modification-time)

    Args:
        tree: dict = {(pathlib.Path, int): (hash-code, int)}
              directory index

    Returns:
        listing   : collections.defaultdict(set) =
                    {(hash-code, int): {(pathlib.Path, int)}}
    """

    listing = collections.defaultdict(set)
    for k, v in tree.items():
        content = (v[aw.HASH], v[aw.SIZE])
        pointer = (k, v[aw.MTIME])
        listing[content].add(pointer)
    return listing


def listing_to_tree(listing):
    tree = dict()
    for k, pointers in listing.items():
        for pointer in pointers:
            tree[pointer[PATH]] = (k[HASH], k[SIZE], pointer[MTIME])
    return tree


def get_duplicate(listing):
    duplicate = {content: pointers for content, pointers in listing.items()
                 if len(pointers) >= 2}
    size_gain = sum([content[aw.SIZE] * (len(pointers) - 1)
                     for content, pointers in duplicate.items()])
    duplicate_sorted_by_size = {content: pointers for (content, pointers)
                                in sorted(duplicate.items(),
                                          key=lambda item: item[0][aw.SIZE],
                                          reverse=True)}
    result = collections.defaultdict(set, duplicate_sorted_by_size)
    return result, size_gain


def get_missing(old_listing, new_listing):
    non_included = {content: pointers for content, pointers
                    in old_listing.items() if content not in new_listing}
    result = collections.defaultdict(set, non_included)
    return result
