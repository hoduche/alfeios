import pathlib

import pytest

import alfeios.json as aj
import alfeios.walker as aw

debug = False

tests_data_path = pathlib.Path(__file__).parent / 'data'

folders = [('Folder0', 'Folder0'),
           ('Folder0/Folder3', 'Folder3'),
           ('FolderZipFile', 'FolderZipFile'),
           ('FolderZipFolder', 'FolderZipFolder'),
           ('FolderZipNested', 'FolderZipNested')]
names = [each[1] for each in folders]


@pytest.mark.parametrize('folder, name', folders, ids=names)
def test_walk(folder, name):
    # run
    listing, tree, forbidden = aw.walk(tests_data_path / folder)

    # for logging purpose only
    if debug:
        aj.save_json_listing(
            listing,
            tests_data_path / (name + '_listing.json'),
            tests_data_path)
        aj.save_json_tree(
            tree,
            tests_data_path / (name + '_tree.json'),
            tests_data_path)
        aj.save_json_forbidden(
            forbidden,
            tests_data_path / (name + '_forbidden.json'),
            tests_data_path)

    # load expected
    expected_listing = aj.load_json_listing(
        tests_data_path / (name + '_listing_expected.json'),
        tests_data_path)
    expected_tree = aj.load_json_tree(
        tests_data_path / (name + '_tree_expected.json'),
        tests_data_path)

    # verify
    if debug:
        aj.save_json_tree(tree,
                           tests_data_path / 'tree.json')
        aj.save_json_tree(expected_tree,
                           tests_data_path / 'expected_tree.json')
        aj.save_json_listing(listing,
                              tests_data_path / 'listing.json')
        aj.save_json_listing(expected_listing,
                              tests_data_path / 'expected_listing.json')
    assert listing == expected_listing
    assert tree == expected_tree
    assert forbidden == {}


def test_walk_with_exclusions():
    # run
    listing, tree, forbidden = aw.walk(tests_data_path / 'Folder0',
                                        exclusion=['Folder3', 'Folder4_1',
                                                   'file3.txt', 'groundhog.png'])

    # for logging purpose only
    if debug:
        aj.save_json_listing(
            listing,
            tests_data_path / 'Folder0_listing_with_exclusions.json',
            tests_data_path)
        aj.save_json_tree(
            tree,
            tests_data_path / 'Folder0_tree_with_exclusions.json',
            tests_data_path)
        aj.save_json_forbidden(
            forbidden,
            tests_data_path / 'Folder0_forbidden_with_exclusions.json',
            tests_data_path)

    # load expected
    expected_listing = aj.load_json_listing(
        tests_data_path / 'Folder0_listing_with_exclusions_expected.json',
        tests_data_path)
    expected_tree = aj.load_json_tree(
        tests_data_path / 'Folder0_tree_with_exclusions_expected.json',
        tests_data_path)

    # verify
    assert listing == expected_listing
    assert tree == expected_tree
    assert forbidden == {}


def test_unify():
    # run
    listing0_no3, tree0_no3, forbidden0_no3 = aw.walk(
        tests_data_path / 'Folder0', exclusion=['Folder3'])
    listing3, tree3, forbidden3 = aw.walk(tests_data_path / 'Folder0' / 'Folder3')
    listing, tree, forbidden = aw.unify([listing0_no3, listing3],
                                         [tree0_no3, tree3],
                                         [forbidden0_no3, forbidden3])
    listing0_full, tree0_full, forbidden0_full = aw.walk(tests_data_path / 'Folder0')

    # verify
    listing.pop(('7e472b2b54ba97314c63988db267d125', 'DIR', 2698920))
    listing0_full.pop(('4f8c48630a797715e8b86466e0218aa1', 'DIR', 3598557))
    assert listing == listing0_full
    tree.pop(tests_data_path / 'Folder0')
    tree0_full.pop(tests_data_path / 'Folder0')
    assert tree == tree0_full
    assert forbidden == forbidden0_full


def test_duplicate():
    # run
    listing, tree, forbidden = aw.walk(tests_data_path / 'Folder0' / 'Folder3')
    duplicate_listing, size_gain = aw.get_duplicate(listing)

    # for logging purpose only
    if debug:
        aj.save_json_listing(
            duplicate_listing,
            tests_data_path / 'Folder3_duplicate_listing.json',
            tests_data_path)

    # load expected
    expected_duplicate_listing = aj.load_json_listing(
        tests_data_path / 'Folder3_duplicate_listing_expected.json',
        tests_data_path)

    # verify
    assert duplicate_listing == expected_duplicate_listing
    assert size_gain == 367645


def test_duplicate_with_zip():
    # run
    listing, tree, forbidden = aw.walk(tests_data_path)
    duplicate_listing, size_gain = aw.get_duplicate(listing)

    # for logging purpose only
    if debug:
        aj.save_json_listing(
            duplicate_listing,
            tests_data_path / 'duplicate.json',
            tests_data_path)

    # verify
    assert duplicate_listing[('4f8c48630a797715e8b86466e0218aa1', 'DIR', 3598557)] == \
           {tests_data_path / 'Folder0',
            tests_data_path / 'FolderZipFile',
            tests_data_path / 'FolderZipFolder',
            tests_data_path / 'FolderZipNested'}


def test_missing_fully_included():
    # run
    listing3, tree3, forbidden3 = aw.walk(tests_data_path / 'Folder0' / 'Folder3')
    listing0, tree0, forbidden0 = aw.walk(tests_data_path / 'Folder0')
    missing_listing = aw.get_missing(listing3, listing0)

    # for logging purpose only
    if debug:
        aj.save_json_listing(
            missing_listing,
            tests_data_path / 'Folder3_missing_listing_in_Folder0.json',
            tests_data_path)

    # verify
    assert missing_listing == {}


def test_missing_not_fully_included():
    # run
    listing8, tree8, forbidden8 = aw.walk(tests_data_path / 'Folder8')
    listing0, tree0, forbidden0 = aw.walk(tests_data_path / 'Folder0')
    missing_listing = aw.get_missing(listing8, listing0)

    # for logging purpose only
    if debug:
        aj.save_json_listing(
            missing_listing,
            tests_data_path / 'Folder8_missing_listing_in_Folder0.json',
            tests_data_path)

    # load expected
    expected_missing_listing = aj.load_json_listing(
        tests_data_path / 'Folder8_missing_listing_in_Folder0_expected.json',
        tests_data_path)

    # verify
    assert missing_listing == expected_missing_listing
