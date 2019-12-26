import pathlib

import pytest

import fs_walker.walker as fsw

debug = False

tests_data_path = pathlib.Path(__file__).resolve().expanduser().parent / 'data'

folders = [('Folder0', 'Folder0'),
           ('Folder0/Folder3', 'Folder3'),
           ('FolderZipFile', 'FolderZipFile'),
           ('FolderZipFolder', 'FolderZipFolder'),
           ('FolderZipNested', 'FolderZipNested')]
names = [each[1] for each in folders]


@pytest.mark.parametrize('folder, name', folders, ids=names)
def test_walk(folder, name):
    # run
    listing, tree = fsw.walk(tests_data_path / folder)

    # for logging purpose only
    if debug:
        fsw.dump_json_listing(
            listing,
            tests_data_path / (name + '_listing.json'),
            tests_data_path)
        fsw.dump_json_tree(
            tree,
            tests_data_path / (name + '_tree.json'),
            tests_data_path)

    # load expected
    expected_listing = fsw.load_json_listing(
        tests_data_path / (name + '_listing_expected.json'),
        tests_data_path)
    expected_tree = fsw.load_json_tree(
        tests_data_path / (name + '_tree_expected.json'),
        tests_data_path)

    # verify
    if debug:
        fsw.dump_json_tree(tree,
                           tests_data_path / 'tree.json')
        fsw.dump_json_tree(expected_tree,
                           tests_data_path / 'expected_tree.json')
        fsw.dump_json_listing(listing,
                              tests_data_path / 'listing.json')
        fsw.dump_json_listing(expected_listing,
                              tests_data_path / 'expected_listing.json')
    assert listing == expected_listing
    assert tree == expected_tree


def test_walk_with_exclusions():
    # run
    listing, tree = fsw.walk(tests_data_path / 'Folder0',
                              exclusion=['Folder3', 'Folder4_1',
                                         'file3.txt', 'groundhog.png'])

    # for logging purpose only
    if debug:
        fsw.dump_json_listing(
            listing,
            tests_data_path / 'Folder0_listing_with_exclusions.json',
            tests_data_path)
        fsw.dump_json_tree(
            tree,
            tests_data_path / 'Folder0_tree_with_exclusions.json',
            tests_data_path)

    # load expected
    expected_listing = fsw.load_json_listing(
        tests_data_path / 'Folder0_listing_with_exclusions_expected.json',
        tests_data_path)
    expected_tree = fsw.load_json_tree(
        tests_data_path / 'Folder0_tree_with_exclusions_expected.json',
        tests_data_path)

    # verify
    assert listing == expected_listing
    assert tree == expected_tree


def test_unify():
    # run
    listing0_no3, tree0_no3 = fsw.walk(
        tests_data_path / 'Folder0', exclusion=['Folder3'])
    listing3, tree3 = fsw.walk(tests_data_path / 'Folder0' / 'Folder3')
    listing, tree = fsw.unify([listing0_no3, listing3], [tree0_no3, tree3])
    listing0_full, tree0_full = fsw.walk(tests_data_path / 'Folder0')

    # verify
    listing.pop(('7e472b2b54ba97314c63988db267d125', 'DIR', 2698920))
    listing0_full.pop(('4f8c48630a797715e8b86466e0218aa1', 'DIR', 3598557))
    assert listing == listing0_full
    tree.pop(tests_data_path / 'Folder0')
    tree0_full.pop(tests_data_path / 'Folder0')
    assert tree == tree0_full


def test_duplicates():
    # run
    listing, tree = fsw.walk(tests_data_path / 'Folder0' / 'Folder3')
    listing_duplicates, size_gain = fsw.get_duplicates(listing)

    # for logging purpose only
    if debug:
        fsw.dump_json_listing(
            listing_duplicates,
            tests_data_path / 'Folder3_listing_duplicates.json',
            tests_data_path)

    # load expected
    expected_listing_duplicates = fsw.load_json_listing(
        tests_data_path / 'Folder3_listing_duplicates_expected.json',
        tests_data_path)

    # verify
    assert listing_duplicates == expected_listing_duplicates
    assert size_gain == 367645


def test_duplicates_with_zip():
    # run
    listing, tree = fsw.walk(tests_data_path)
    listing_duplicates, size_gain = fsw.get_duplicates(listing)

    # for logging purpose only
    if debug:
        fsw.dump_json_listing(
            listing_duplicates,
            tests_data_path / 'duplicates.json',
            tests_data_path)

    # verify
    k0 = list(listing_duplicates)[0]
    v0 = listing_duplicates[k0]
    assert k0 == ('4f8c48630a797715e8b86466e0218aa1', 'DIR', 3598557)
    assert v0 == {tests_data_path / 'Folder0',
                  tests_data_path / 'FolderZipFile',
                  tests_data_path / 'FolderZipFolder',
                  tests_data_path / 'FolderZipNested'}


def test_non_included_fully_included():
    # run
    listing3, tree3 = fsw.walk(tests_data_path / 'Folder0' / 'Folder3')
    listing0, tree0 = fsw.walk(tests_data_path / 'Folder0')
    listing_non_included = fsw.get_non_included(listing3, listing0)

    # for logging purpose only
    if debug:
        fsw.dump_json_listing(
            listing_non_included,
            tests_data_path / 'Folder3_listing_non_included_in_Folder0.json',
            tests_data_path)

    # verify
    assert listing_non_included == {}


def test_non_included_not_fully_included():
    # run
    listing8, tree8 = fsw.walk(tests_data_path / 'Folder8')
    listing0, tree0 = fsw.walk(tests_data_path / 'Folder0')
    listing_non_included = fsw.get_non_included(listing8, listing0)

    # for logging purpose only
    if debug:
        fsw.dump_json_listing(
            listing_non_included,
            tests_data_path / 'Folder8_listing_non_included_in_Folder0.json',
            tests_data_path)

    # load expected
    expected_listing_non_included = fsw.load_json_listing(
        tests_data_path / 'Folder8_listing_non_included_in_Folder0_expected.json',
        tests_data_path)

    # verify
    assert listing_non_included == expected_listing_non_included
