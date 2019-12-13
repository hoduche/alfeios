import pathlib

import pytest

import fs_crawler.crawl as fsc

debug = False

tests_data_path = pathlib.Path(__file__).resolve().expanduser().parent / 'data'

folders = [('Folder0', 'Folder0'),
           ('Folder0/Folder3', 'Folder3'),
           ('FolderZipFile', 'FolderZipFile')]
names = [each[1] for each in folders]


@pytest.mark.parametrize('folder, name', folders, ids=names)
def test_crawl(folder, name):
    # run
    listing, tree = fsc.crawl(tests_data_path / folder)

    # for logging purpose only
    if debug:
        fsc.dump_json_listing(
            listing, tests_data_path / (name + '_listing.json'))
        fsc.dump_json_tree(
            tree, tests_data_path / (name + '_tree.json'))

    # load expected
    expected_listing = fsc.load_json_listing(
        tests_data_path / (name + '_listing_expected.json'))
    expected_tree = fsc.load_json_tree(
        tests_data_path / (name + '_tree_expected.json'))

    # verify
    assert listing == expected_listing
    assert tree == expected_tree


def test_crawl_with_exclusions():
    # run
    listing, tree = fsc.crawl(tests_data_path / 'Folder0',
                              exclusion=['Folder3', 'Folder4_1',
                                         'file3.txt', 'groundhog.png'])

    # for logging purpose only
    if debug:
        fsc.dump_json_listing(
            listing, tests_data_path / 'Folder0_listing_with_exclusions.json')
        fsc.dump_json_tree(
            tree, tests_data_path / 'Folder0_tree_with_exclusions.json')

    # load expected
    expected_listing = fsc.load_json_listing(
        tests_data_path / 'Folder0_listing_with_exclusions_expected.json')
    expected_tree = fsc.load_json_tree(
        tests_data_path / 'Folder0_tree_with_exclusions_expected.json')

    # verify
    assert listing == expected_listing
    assert tree == expected_tree


def test_unify():
    # run
    listing0_no3, tree0_no3 = fsc.crawl(
        tests_data_path / 'Folder0', exclusion=['Folder3'])
    listing3, tree3 = fsc.crawl(tests_data_path / 'Folder0' / 'Folder3')
    listing, tree = fsc.unify([listing0_no3, listing3], [tree0_no3, tree3])
    listing0_full, tree0_full = fsc.crawl(tests_data_path / 'Folder0')

    # verify
    listing.pop(('7e472b2b54ba97314c63988db267d125', 'DIR', 2698920))
    listing0_full.pop(('4f8c48630a797715e8b86466e0218aa1', 'DIR', 3598557))
    assert listing == listing0_full
    tree.pop(tests_data_path / 'Folder0')
    tree0_full.pop(tests_data_path / 'Folder0')
    assert tree == tree0_full


def test_duplicates():
    # run
    listing, tree = fsc.crawl(tests_data_path / 'Folder0' / 'Folder3')
    listing_duplicates, size_gain = fsc.get_duplicates(listing)

    # for logging purpose only
    if debug:
        fsc.dump_json_listing(
            listing_duplicates,
            tests_data_path / 'Folder3_listing_duplicates.json')

    # load expected
    expected_listing_duplicates = fsc.load_json_listing(
        tests_data_path / 'Folder3_listing_duplicates_expected.json')

    # verify
    assert listing_duplicates == expected_listing_duplicates
    assert size_gain == 367645


def test_non_included_fully_included():
    # run
    listing3, tree3 = fsc.crawl(tests_data_path / 'Folder0' / 'Folder3')
    listing0, tree0 = fsc.crawl(tests_data_path / 'Folder0')
    listing_non_included = fsc.get_non_included(listing3, listing0)

    # for logging purpose only
    if debug:
        fsc.dump_json_listing(
            listing_non_included,
            tests_data_path / 'Folder3_listing_non_included_in_Folder0.json')

    # verify
    assert listing_non_included == {}


def test_non_included_not_fully_included():
    # run
    listing8, tree8 = fsc.crawl(tests_data_path / 'Folder8')
    listing0, tree0 = fsc.crawl(tests_data_path / 'Folder0')
    listing_non_included = fsc.get_non_included(listing8, listing0)

    # for logging purpose only
    if debug:
        fsc.dump_json_listing(
            listing_non_included,
            tests_data_path / 'Folder8_listing_non_included_in_Folder0.json')

    # load expected
    expected_listing_non_included = fsc.load_json_listing(
        tests_data_path / 'Folder8_listing_non_included_in_Folder0_expected.json')

    # verify
    assert listing_non_included == expected_listing_non_included
