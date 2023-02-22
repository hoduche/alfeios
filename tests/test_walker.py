import collections
import json
import pathlib

import pytest

import alfeios.serialize as asd
import alfeios.tool as at
import alfeios.walker as aw

debug = False

tests_data_path = pathlib.Path(__file__).parent / 'data'

folders = ['Folder9',
           'Folder0',
           'Folder0/Folder3',
           'FolderZipFile',
           'FolderZipFolder',
           'FolderZipNested']
vals = [(f, f) for f in folders]

########################################################################
# Helper functions for test only so far
########################################################################


def reset_listing_mtime(listing):
    result = collections.defaultdict(set)
    for content, pointers in listing.items():
        for pointer in pointers:
            result[content].add((pointer[at.PATH], 0))
    return result


def reset_tree_mtime(tree):
    return {(pointer[at.PATH], 0): content
            for pointer, content in tree.items()}


def sort_json_listing(file_path):
    separator = '-' * 70
    result = []
    json_listing = json.loads(file_path.read_text())
    for content in sorted(json_listing.keys()):
        result.extend([separator, content, separator])
        for pointer in sorted(json_listing[content]):
            result.append(str(pointer))
        result.append('')
    output_path = file_path.parent / (file_path.stem + '_ordered.txt')
    output_path.write_text('\n'.join(result))


def sort_json_tree(file_path):
    result = []
    json_tree = json.loads(file_path.read_text())
    for pointer in sorted(json_tree.keys()):
        result.append(pointer + ': ' + str(json_tree[pointer]))
    output_path = file_path.parent / (file_path.stem + '_ordered.txt')
    output_path.write_text('\n'.join(result))


########################################################################
# Setup and Teardown
########################################################################


@pytest.fixture(scope="module", autouse=True)
def teardown(request):
    # nothing before the tests
    def sort_if_debug():
        if debug:
            for folder in folders:
                for alfeios in ['.alfeios', '.alfeios_expected']:
                    alfeios_path = tests_data_path / folder / alfeios
                    for listing_path in alfeios_path.glob('*listing*.json'):
                        sort_json_listing(listing_path)
                    for tree_path in alfeios_path.glob('*tree*.json'):
                        sort_json_tree(tree_path)
    # sort the trees and listings after the tests
    request.addfinalizer(sort_if_debug)


########################################################################
# Tests
########################################################################


@pytest.mark.parametrize(argnames='folder, name', argvalues=vals, ids=folders)
def test_walk(folder, name):
    path = tests_data_path / folder

    # run
    listing, tree, forbidden = aw.walk(path)

    # for logging purpose only
    if debug:
        asd.save_json_index(path, listing, tree, forbidden,
                            start_path=tests_data_path)

    # load expected
    expected_listing = asd.load_json_listing(
        path / '.alfeios_expected' / 'listing.json',
        start_path=tests_data_path)
    expected_tree = asd.load_json_tree(
        path / '.alfeios_expected' / 'tree.json',
        start_path=tests_data_path)

    # reset mtime for everybody as it is updated with the test itself
    listing = reset_listing_mtime(listing)
    expected_listing = reset_listing_mtime(expected_listing)
    tree = reset_tree_mtime(tree)
    expected_tree = reset_tree_mtime(expected_tree)

    # verify
    assert listing == expected_listing
    assert tree == expected_tree
    assert forbidden == {}


def test_walk_with_exclusions():
    path = tests_data_path / 'Folder0'
    exclusion = {'Folder3', 'Folder4_1', 'file3.txt', 'groundhog.png'}

    # run
    listing, tree, forbidden = aw.walk(path, exclusion=exclusion)

    # for logging purpose only
    if debug:
        asd.save_json_index(path, listing, tree, forbidden,
                            start_path=tests_data_path,
                            prefix='with_exclusions_')

    # load expected
    expected_listing = asd.load_json_listing(
        path / '.alfeios_expected' / 'listing_with_exclusions.json',
        start_path=tests_data_path)
    expected_tree = asd.load_json_tree(
        path / '.alfeios_expected' / 'tree_with_exclusions.json',
        start_path=tests_data_path)

    # reset mtime for everybody as it is updated with the test itself
    listing = reset_listing_mtime(listing)
    expected_listing = reset_listing_mtime(expected_listing)
    tree = reset_tree_mtime(tree)
    expected_tree = reset_tree_mtime(expected_tree)

    # verify
    assert listing == expected_listing
    assert tree == expected_tree
    assert forbidden == {}


def test_unify():
    path0 = tests_data_path / 'Folder0'
    path8 = tests_data_path / 'Folder8'

    # run
    listing0, tree0, forbidden0 = aw.walk(path0)
    listing8, tree8, forbidden8 = aw.walk(path8)
    listing, tree, forbidden = aw.unify([listing0, listing8],
                                        [tree0, tree8],
                                        [forbidden0, forbidden8])

    # load expected
    expected_listing = asd.load_json_listing(
        tests_data_path / '.alfeios_expected' / 'listing_0_8.json',
        start_path=tests_data_path)
    expected_tree = asd.load_json_tree(
        tests_data_path / '.alfeios_expected' / 'tree_0_8.json',
        start_path=tests_data_path)

    # reset mtime for everybody as it is updated with the test itself
    listing = reset_listing_mtime(listing)
    expected_listing = reset_listing_mtime(expected_listing)
    tree = reset_tree_mtime(tree)
    expected_tree = reset_tree_mtime(expected_tree)

    # verify
    assert listing == expected_listing
    assert tree == expected_tree
    assert forbidden == {}


def test_unify_with_exclusion():
    path = tests_data_path / 'Folder0'

    # run
    listing0_no3, tree0_no3, forbidden0_no3 = aw.walk(path,
                                                      exclusion={'Folder3'})
    listing3, tree3, forbidden3 = aw.walk(path / 'Folder3')
    listing_uni, tree_uni, forbid_uni = aw.unify([listing0_no3, listing3],
                                                 [tree0_no3, tree3],
                                                 [forbidden0_no3, forbidden3])
    listing0_full, tree0_full, forbidden0_full = aw.walk(path)

    # remove the root folder record
    # as the run with exclusion does not give the full size and hash
    # normally the unification is on separate folders
    listing_uni.pop(('7e472b2b54ba97314c63988db267d125', 'DIR', 2698920))
    listing0_full.pop(('4f8c48630a797715e8b86466e0218aa1', 'DIR', 3598557))
    tree_uni = {pointer: content for pointer, content in tree_uni.items()
                if pointer[at.PATH] != tests_data_path / 'Folder0'}
    tree0_full = {pointer: content for pointer, content in tree0_full.items()
                  if pointer[at.PATH] != tests_data_path / 'Folder0'}

    # verify
    assert listing_uni == listing0_full
    assert tree_uni == tree0_full
    assert forbid_uni == forbidden0_full


def test_duplicate():
    path = tests_data_path / 'Folder0' / 'Folder3'

    # run
    listing, tree, forbidden = aw.walk(path)
    duplicate_listing, size_gain = aw.get_duplicate(listing)

    # for logging purpose only
    if debug:
        asd.save_json_index(path, duplicate_listing,
                            start_path=tests_data_path,
                            prefix='duplicate_')

    # load expected
    expected_duplicate_listing = asd.load_json_listing(
        path / '.alfeios_expected' / 'duplicate_listing.json',
        start_path=tests_data_path)

    # reset mtime for everybody as it is updated with the test itself
    duplicate_listing = reset_listing_mtime(duplicate_listing)
    expected_duplicate_listing = reset_listing_mtime(
        expected_duplicate_listing)

    # verify
    assert duplicate_listing == expected_duplicate_listing
    assert size_gain == 367645


def test_duplicate_with_zip():
    # run
    listing, tree, forbidden = aw.walk(tests_data_path)
    duplicate_listing, size_gain = aw.get_duplicate(listing)

    # for logging purpose only
    if debug:
        asd.save_json_index(tests_data_path, duplicate_listing,
                            start_path=tests_data_path,
                            prefix='duplicate_with_zip_')

    # verify
    # here we only check that the root directory content of 4 folders are equal
    # it sould be enough thanks to the Merkle tree property of alfeios listing
    duplicate_root_content = ('4f8c48630a797715e8b86466e0218aa1',
                              'DIR', 3598557)
    duplicate_root_pointers = duplicate_listing[duplicate_root_content]
    # remove mtime for everybody as it is updated with the test itself
    duplicate_root_directories = {path for path, mtime
                                  in duplicate_root_pointers}
    assert duplicate_root_directories == {tests_data_path / 'Folder0',
                                          tests_data_path / 'FolderZipFile',
                                          tests_data_path / 'FolderZipFolder',
                                          tests_data_path / 'FolderZipNested'}


def test_missing_fully_included():
    path = tests_data_path / 'Folder0'

    # run
    listing3, tree3, forbidden3 = aw.walk(path / 'Folder3')
    listing0, tree0, forbidden0 = aw.walk(path)
    missing_listing = aw.get_missing(listing3, listing0)

    # for logging purpose only
    if debug:
        asd.save_json_index(path, missing_listing, start_path=tests_data_path,
                            prefix='missing_fully_included_')

    # verify
    assert missing_listing == {}


def test_missing_not_fully_included():
    path = tests_data_path / 'Folder0'

    # run
    listing8, tree8, forbidden8 = aw.walk(tests_data_path / 'Folder8')
    listing0, tree0, forbidden0 = aw.walk(path)
    missing_listing = aw.get_missing(listing8, listing0)

    # for logging purpose only
    if debug:
        asd.save_json_index(path, missing_listing, start_path=tests_data_path,
                            prefix='missing_not_fully_included_')

    # load expected
    expected_missing_listing = asd.load_json_listing(
        path / '.alfeios_expected' / 'listing_missing_from_Folder8.json',
        start_path=tests_data_path)

    # reset mtime for everybody as it is updated with the test itself
    missing_listing = reset_listing_mtime(missing_listing)
    expected_missing_listing = reset_listing_mtime(expected_missing_listing)

    # verify
    assert missing_listing == expected_missing_listing


def test_tree_to_listing():
    path = tests_data_path / 'Folder0' / '.alfeios_expected'

    # load expected with start_path
    expected_listing = asd.load_json_listing(path / 'listing.json',
                                             start_path=tests_data_path)
    expected_tree = asd.load_json_tree(path / 'tree.json',
                                       start_path=tests_data_path)

    # verify
    assert aw.tree_to_listing(expected_tree) == expected_listing

    # load expected without start_path
    expected_listing = asd.load_json_listing(path / 'listing.json')
    expected_tree = asd.load_json_tree(path / 'tree.json')

    # verify
    assert aw.tree_to_listing(expected_tree) == expected_listing


def test_listing_to_tree():
    path = tests_data_path / 'Folder0' / '.alfeios_expected'

    # load expected with start_path
    expected_listing = asd.load_json_listing(path / 'listing.json',
                                             start_path=tests_data_path)
    expected_tree = asd.load_json_tree(path / 'tree.json',
                                       start_path=tests_data_path)

    # verify
    assert aw.listing_to_tree(expected_listing) == expected_tree

    # load expected without start_path
    expected_listing = asd.load_json_listing(path / 'listing.json')
    expected_tree = asd.load_json_tree(path / 'tree.json')

    # verify
    assert aw.listing_to_tree(expected_listing) == expected_tree
