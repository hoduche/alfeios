import collections

from alfeios import tool as at


def tree_to_listing(tree):
    """ Converts a directory tree index to a listing:
    a collections.defaultdict(set) whose keys are 3-tuples
    (hash-code, path-type, size)
    and values are set of 2-tuples (pathlib.Path, modification-time)

    Args:
        tree: dict = {(pathlib.Path, int): (hash-code, path-type, int)}
              directory index

    Returns:
        listing   : collections.defaultdict(set) =
                    {(hash-code, path-type, int): {(pathlib.Path, int)}}
    """

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
