import json
import os
import pathlib
import tarfile
import time

import pytest

import alfeios.listing as al
import alfeios.serialize as asd
import alfeios.walker as aw

"""
To replace expected results, you can use sed like this:
find . -type f -name "*tree*.json" | xargs sed -i -E 's/"\(([^,]+), ([0-9\.]+)\)": \[([^,]+), ([^,]+), ([0-9]+)\]/\1: \[\3, \4, \5, \2\]/g'
find . -type f -name "*tree*.json" | xargs sed -i -E 's/\x27/"/g'
inside /tmp/pytest... after a test run
"""

debug = True

tests_data = pathlib.Path(__file__).parent / 'data' / 'data.tar.gz'

folders = ['Folder9',  # only one file
           'Folder0',  # complete use case without zip files
           'Folder0/Folder3',  # subfolder
           'FolderZipFile',
           'FolderZipFolder',
           'FolderZipNested']
vals = [(f, f) for f in folders]


########################################################################
# Helper functions used in tests only so far
########################################################################


def reset_folder_time(path):
    date_time = time.mktime((2021, 1, 16, 11, 0, 0, 0, 0, -1))
    os.utime(path, (date_time, date_time))


def log_sorted_json_listing(file_path):
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


def log_sorted_json_tree(file_path):
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
def data_path(tmp_path_factory):
    # setup once for all tests
    tar = tarfile.open(tests_data)
    tmp_path = tmp_path_factory.mktemp('data')
    tar.extractall(tmp_path)
    tar.close()
    return tmp_path


@pytest.fixture(scope="module", autouse=True)
def teardown(request, data_path):
    # teardown for each test in case you want to log debug info
    def log_sorted_results():
        if debug:
            for folder in folders + ['.']:
                for alfeios in ['.alfeios', '.alfeios_expected']:
                    alfeios_path = data_path / folder / alfeios
                    for listing_path in alfeios_path.glob('*listing*.json'):
                        log_sorted_json_listing(listing_path)
                    for tree_path in alfeios_path.glob('*tree*.json'):
                        log_sorted_json_tree(tree_path)
    # sort the trees and listings after the tests
    request.addfinalizer(log_sorted_results)


########################################################################
# Tests
########################################################################


@pytest.mark.parametrize(argnames='folder, name', argvalues=vals, ids=folders)
def test_walk(folder, name, data_path):
    path = data_path / folder

    # run
    tree, forbidden = aw.walk(path)

    # for logging purpose only
    if debug:
        asd.save_json_tree(path, tree, forbidden, start_path=data_path)
        reset_folder_time(path)

    # load expected
    expected_tree = asd.load_json_tree(
        path / '.alfeios_expected' / 'tree.json', start_path=data_path)

    # verify
    assert tree == expected_tree
    assert forbidden == {}


def test_walk_with_cache(data_path):  # todo real implementation
    path = data_path / 'FolderWithCache'
    if not pathlib.Path(path).is_dir():
        pathlib.Path(path).mkdir()


def test_walk_with_exclusions(data_path):
    path = data_path / 'Folder0'
    exclusion = {'Folder3', 'Folder4_1', 'file3.txt', 'groundhog.png'}

    # run
    tree, forbidden = aw.walk(path, exclusion=exclusion)

    # for logging purpose only
    if debug:
        f = asd.save_json_tree(path, tree, forbidden, start_path=data_path)
        f.rename(f.with_stem(f.stem + '_with_exclusions'))
        reset_folder_time(path)

    # load expected
    expected_tree = asd.load_json_tree(
        path / '.alfeios_expected' / 'tree_with_exclusions.json',
        start_path=data_path)

    # verify
    assert tree == expected_tree
    assert forbidden == {}


def test_duplicate(data_path):
    path = data_path / 'Folder0' / 'Folder3'

    # run
    tree, forbidden = aw.walk(path)
    listing = al.tree_to_listing(tree)
    duplicate_listing, size_gain = al.get_duplicate(listing)

    # for logging purpose only
    if debug:
        f = asd.save_json_listing(path, duplicate_listing, start_path=data_path)
        f.rename(f.with_stem(f.stem + '_duplicate'))
        reset_folder_time(path)

    # load expected
    expected_duplicate_listing = asd.load_json_listing(
        path / '.alfeios_expected' / 'duplicate_listing.json',
        start_path=data_path)

    # verify
    assert duplicate_listing == expected_duplicate_listing
    assert size_gain == 367645


def test_duplicate_with_zip(data_path):
    # run
    tree, forbidden = aw.walk(data_path)
    listing = al.tree_to_listing(tree)
    duplicate_listing, size_gain = al.get_duplicate(listing)

    # for logging purpose only
    if debug:
        f = asd.save_json_listing(data_path, duplicate_listing,
                                  start_path=data_path)
        f.rename(f.with_stem(f.stem + '_duplicate_with_zip'))
        reset_folder_time(data_path)

    # verify
    # here we only check that the root directory content of 4 folders are equal
    # it sould be enough thanks to the Merkle tree property of alfeios listing
    duplicate_root_content = ('4f8c48630a797715e8b86466e0218aa1',
                              'DIR', 3598557)
    duplicate_root_pointers = duplicate_listing[duplicate_root_content]
    assert duplicate_root_pointers == {
        (data_path / 'Folder0', 1610791200.0),
        (data_path / 'FolderZipFile', 1610791200.0),
        (data_path / 'FolderZipFolder', 1610791200.0),
        (data_path / 'FolderZipNested', 1610791200.0)}


def test_missing_fully_included(data_path):
    path = data_path / 'Folder0'

    # run
    tree3, forbidden3 = aw.walk(path / 'Folder3')
    listing3 = al.tree_to_listing(tree3)

    tree0, forbidden0 = aw.walk(path)
    listing0 = al.tree_to_listing(tree0)

    missing_listing = al.get_missing(listing3, listing0)

    # for logging purpose only
    if debug:
        f = asd.save_json_listing(path, missing_listing, start_path=data_path)
        f.rename(f.with_stem(f.stem + '_missing_fully_included'))
        reset_folder_time(path)

    # verify
    assert missing_listing == {}


def test_missing_not_fully_included(data_path):
    path = data_path / 'Folder0'

    # run
    tree8, forbidden8 = aw.walk(data_path / 'Folder8')
    listing8 = al.tree_to_listing(tree8)

    tree0, forbidden0 = aw.walk(path)
    listing0 = al.tree_to_listing(tree0)

    missing_listing = al.get_missing(listing8, listing0)

    # for logging purpose only
    if debug:
        f = asd.save_json_listing(path, missing_listing, start_path=data_path)
        f.rename(f.with_stem(f.stem + '_missing_not_fully_included'))
        reset_folder_time(path)

    # load expected
    expected_missing_listing = asd.load_json_listing(
        path / '.alfeios_expected' / 'listing_missing_from_Folder8.json',
        start_path=data_path)

    # verify
    assert missing_listing == expected_missing_listing


def test_tree_to_listing(data_path):
    path = data_path / 'Folder0' / '.alfeios_expected'

    # load expected with start_path
    expected_listing = asd.load_json_listing(path / 'listing.json',
                                             start_path=data_path)
    expected_tree = asd.load_json_tree(path / 'tree.json',
                                       start_path=data_path)

    # verify
    assert al.tree_to_listing(expected_tree) == expected_listing

    # load expected without start_path
    expected_listing = asd.load_json_listing(path / 'listing.json')
    expected_tree = asd.load_json_tree(path / 'tree.json')

    # verify
    assert al.tree_to_listing(expected_tree) == expected_listing


def test_listing_to_tree(data_path):
    path = data_path / 'Folder0' / '.alfeios_expected'

    # load expected with start_path
    expected_listing = asd.load_json_listing(path / 'listing.json',
                                             start_path=data_path)
    expected_tree = asd.load_json_tree(path / 'tree.json',
                                       start_path=data_path)

    # verify
    assert al.listing_to_tree(expected_listing) == expected_tree

    # load expected without start_path
    expected_listing = asd.load_json_listing(path / 'listing.json')
    expected_tree = asd.load_json_tree(path / 'tree.json')

    # verify
    assert al.listing_to_tree(expected_listing) == expected_tree
