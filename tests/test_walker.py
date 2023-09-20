import pathlib
import shutil
import tarfile
import time
import unittest.mock

import pytest

import alfeios.api as aa
import alfeios.listing as al
import alfeios.serialize as asd
import alfeios.tool as at
import alfeios.walker as aw
import helper as h

debug = False

"""  # noqa: W605 E501
-------------------------------------------------------
After a test run with debug=False
-------------------------------------------------------
There will be a new directory /tmp/pytest.../data/
Inside this directory you can recreate the data.tar.gz file
replacing expected results with sed (see examples below), then running:
$ tar -czvf data.tar.gz *

Example:
$ find . -type f -name "*tree*.json" | xargs sed -i -E 's/"\(([^,]+), ([0-9\.]+)\)": \[([^,]+), ([^,]+), ([0-9]+)\]/\1: \[\3, \4, \5, \2\]/g'
$ find . -type f -name "*tree*.json" | xargs sed -i -E 's/\x27/"/g'

Other example:
$ find . -type f -name "*tree*.json" | xargs sed -i -E 's/"[^\/^"]+": \[([^]]+)]/"\.": \[\1\]/g'
$ find . -type f -name "*tree*.json" | xargs sed -i -E 's/"[^\/]+\/([^"]+)": \[([^]]+)]/"\1": \[\2\]/g'

Other example: remove the DIR lines in the trees
$ find . -type f -name "*tree*.json" | xargs sed -i -E 's/"[^"]+": \["[^"]+", "DIR", [0-9]+, [0-9\.]+\], //g'
$ find . -type f -name "*tree*.json" | xargs sed -i -E 's/, "[^"]+": \["[^"]+", "DIR", [0-9]+, [0-9\.]+\]//g'

Other example: remove the "FILE" type in the trees and listings
$ find . -type f -name "*tree*.json" | xargs sed -i -E 's/, "FILE"//g'
$ find . -type f -name "*listing*.json" | xargs sed -i -E "s/, 'FILE'//g"

-------------------------------------------------------
After a test run with debug=True
-------------------------------------------------------
It is possible to clean the corresponding directory with :

$ find . -type d -name .alfeios | xargs ls -l
$ find . -type d -name .alfeios | xargs ls -ld
$ find . -type d -name .alfeios | xargs rm -rf

$ find . -type f -name *ordered.txt | xargs ls -l
$ find . -type f -name *ordered.txt | xargs rm

"""

########################################################################
# New way of doing tests: create content programmatically
########################################################################
content1 = "hello"
content2 = "hello\nworld\n"
content3 = "hello\nbeautiful world\n"
colors1 = "green white orange"
colors2 = "blue white red"
dt_tuple1 = (2021, 1, 16, 11, 1, 0, 0, 0, -1)
dt_tuple2 = (2022, 2, 17, 12, 2, 0, 0, 0, -1)
dt_tuple3 = (2023, 3, 18, 13, 3, 0, 0, 0, -1)

tests_data_path = pathlib.Path(__file__).parent / 'data'

########################################################################
# Old way of doing tests: use already created content
########################################################################
tests_data = tests_data_path / 'data.tar.gz'

folders = ['Folder9',  # only one file
           'Folder0',  # complete use case without zip files
           'Folder0/Folder3',  # subfolder
           'FolderZipFile',
           'FolderZipFolder',
           'FolderZipNested']
vals = [(f, f) for f in folders]


########################################################################
# Setup and Teardown
########################################################################

@pytest.fixture(scope="module", autouse=True)
def data_path(tmp_path_factory):
    # setup once for all tests - old way of doing tests
    tmp_path = tmp_path_factory.mktemp('data')
    tar = tarfile.open(tests_data)
    tar.extractall(tmp_path)
    tar.close()
    return tmp_path


@pytest.fixture(scope="module", autouse=True)
def teardown(request, data_path):
    # teardown for each test in case you want to log debug info
    def log_sorted_results():
        if debug:
            for folder in folders + ['.', 'Folder8', 'FolderWithCache']:
                for alfeios in ['.alfeios', '.alfeios_expected']:
                    alfeios_path = data_path / folder / alfeios
                    for listing_path in alfeios_path.glob('*listing*.json'):
                        h.log_sorted_json_listing(listing_path)
                    for tree_path in alfeios_path.glob('*tree*.json'):
                        h.log_sorted_json_tree(tree_path)
    # sort the trees and listings after the tests
    request.addfinalizer(log_sorted_results)


########################################################################
# Tests
########################################################################
def test_index_with_cache(data_path):
    path = data_path / 'FolderWithCache'
    if pathlib.Path(path).is_dir():
        shutil.rmtree(path)
    pathlib.Path(path).mkdir()

    h.create_png(path / "flag1.png", dt_tuple1, colors1)
    h.create_png(path / "flag2.png", dt_tuple2, colors2)
    h.create_txt(path / "file1.txt", dt_tuple1, content1)
    h.create_txt(path / "file2.txt", dt_tuple2, content2)
    h.create_txt(path / "file3.txt", dt_tuple3, content3)
    h.create_pdf(path / "pres1.pdf", dt_tuple1, content1)

    pathlib.Path(path / "archive_dir").mkdir()
    h.create_png(path / "archive_dir" / "flag1.png", dt_tuple1, colors1)
    h.create_zip(path / "archive_1", dt_tuple2, path / "archive_dir")
    shutil.rmtree(path / "archive_dir")

    with unittest.mock.patch("alfeios.walker._hash_and_index_file") as ha:
        with unittest.mock.patch("alfeios.walker._fill_tree_from_cache") as ca:
            aa.index(path)
            ha.assert_called()  # 14 times (7 for 1st run + 7 for 2nd run)
            ca.assert_not_called()
    h.remove_last_json_tree(path)

    aa.index(path)
    tree = asd.load_last_json_tree(path)
    expected_tree = asd.load_json_tree(tests_data_path / 'expected_tree1.json')
    assert tree == expected_tree

    time.sleep(1)  # to avoid name_collision
    with unittest.mock.patch("alfeios.walker._hash_and_index_file") as ha:
        with unittest.mock.patch("alfeios.walker._fill_tree_from_cache") as ca:
            aa.index(path)
            ha.assert_called()  # 7 times (for 1st run with should_hash=False)
            ca.assert_called()  # 7 times (for 2nd run)
    h.remove_last_json_tree(path)

    h.reset_time(path / "file2.txt", dt_tuple3)
    h.create_txt(path / "file3.txt", dt_tuple3, content3 + content2)

    with unittest.mock.patch("alfeios.walker._hash_and_index_file") as ha:
        with unittest.mock.patch("alfeios.walker._fill_tree_from_cache") as ca:
            aa.index(path)
            ha.assert_called()  # 9 times (7 for 1st run + 2 for 2nd run)
            ca.assert_called()  # 5 times (for 2nd run)
    h.remove_last_json_tree(path)

    aa.index(path)
    tree = asd.load_last_json_tree(path)
    expected_tree = asd.load_json_tree(tests_data_path / 'expected_tree2.json')
    assert tree == expected_tree


@pytest.mark.parametrize(argnames='folder, name', argvalues=vals, ids=folders)
def test_walk(folder, name, data_path):
    path = data_path / folder

    # run
    tree, forbidden = aw.walk(path)

    # for logging purpose only
    if debug:
        asd.save_json_tree(path, tree, forbidden)
        h.reset_time(path, dt_tuple1)

    # load expected
    expected_tree = asd.load_json_tree(
        path / '.alfeios_expected' / 'tree.json')

    # verify
    assert tree == expected_tree
    assert forbidden == {}


def test_walk_with_exclusions(data_path):
    path = data_path / 'Folder0'
    exclusion = {'Folder3', 'Folder4_1', 'file3.txt', 'groundhog.png'}

    # run
    tree, forbidden = aw.walk(path, exclusion=exclusion)

    # for logging purpose only
    if debug:
        time.sleep(1)  # to avoid name_collision
        f = asd.save_json_tree(path, tree, forbidden)
        f = at.add_suffix(f, '_with_exclusions')
        h.reset_time(path, dt_tuple1)

    # load expected
    expected_tree = asd.load_json_tree(
        path / '.alfeios_expected' / 'tree_with_exclusions.json')

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
        f = asd.save_json_listing(path, duplicate_listing)
        f = at.add_suffix(f, '_duplicate')
        h.reset_time(path, dt_tuple1)

    # load expected
    expected_duplicate_listing = asd.load_json_listing(
        path / '.alfeios_expected' / 'listing_duplicate.json')

    # verify
    assert duplicate_listing == expected_duplicate_listing
    assert size_gain == 367645


def test_duplicate_with_zip(data_path):  # todo write the expected as others
    # run
    tree, forbidden = aw.walk(data_path)
    listing = al.tree_to_listing(tree)
    duplicate_listing, size_gain = al.get_duplicate(listing)

    # for logging purpose only
    if debug:
        f = asd.save_json_listing(data_path, duplicate_listing)
        f = at.add_suffix(f, '_duplicate_with_zip')
        h.reset_time(data_path, dt_tuple1)

    # verify
    duplicate_root_content = ('6a4316b18e6162cf9fcfa435c8eb74c1', 12)
    duplicate_root_pointers = duplicate_listing[duplicate_root_content]
    assert duplicate_root_pointers == {
        (pathlib.Path('Folder0/Folder1/file5.txt'), 1576878010.0),
        (pathlib.Path('Folder0/Folder2/Folder2_1/file5.txt'), 1576878010.0),
        (pathlib.Path('Folder0/Folder2/file5.txt'), 1576878010.0),
        (pathlib.Path('Folder0/Folder3/Folder3_1/file5.txt'), 1576878010.0),
        (pathlib.Path('Folder0/Folder3/file5.txt'), 1576878010.0),
        (pathlib.Path('Folder0/Folder4/file5.txt'), 1576878010.0),
        (pathlib.Path('Folder0/file5.txt'), 1576878010.0),
        (pathlib.Path('Folder8/Folder3_1/file5.txt'), 1576878010.0),
        (pathlib.Path('Folder8/Folder3_1/file6_included.txt'), 1576878010.0),
        (pathlib.Path('Folder8/file5.txt'), 1576878010.0),
        (pathlib.Path('FolderZipFile/Folder1/file5.txt'), 1576878010.0),
        (pathlib.Path('FolderZipFile/Folder2/Folder2_1.zip/file5.txt'),
         1571554388.0),
        (pathlib.Path('FolderZipFile/Folder2/file5.txt'), 1576878010.0),
        (pathlib.Path('FolderZipFile/Folder3/Folder3_1/file5.txt'),
         1576878010.0),
        (pathlib.Path('FolderZipFile/Folder3/file5.txt'), 1576878010.0),
        (pathlib.Path('FolderZipFile/Folder4/file5.txt'), 1576878010.0),
        (pathlib.Path('FolderZipFile/file5.txt'), 1576878010.0),
        (pathlib.Path('FolderZipFolder/Folder1/file5.txt'), 1576878010.0),
        (pathlib.Path('FolderZipFolder/Folder2.zip/Folder2_1/file5.txt'),
         1571554388.0),
        (pathlib.Path('FolderZipFolder/Folder2.zip/file5.txt'), 1571554388.0),
        (pathlib.Path('FolderZipFolder/Folder3/Folder3_1/file5.txt'),
         1576878010.0),
        (pathlib.Path('FolderZipFolder/Folder3/file5.txt'), 1576878010.0),
        (pathlib.Path('FolderZipFolder/Folder4/file5.txt'), 1576878010.0),
        (pathlib.Path('FolderZipFolder/file5.txt'), 1576878010.0),
        (pathlib.Path('FolderZipNested/Folder1/file5.txt'), 1576878010.0),
        (pathlib.Path('FolderZipNested/Folder2.zip/Folder2_1.zip/file5.txt'),
         1571554388.0),
        (pathlib.Path('FolderZipNested/Folder2.zip/file5.txt'), 1571554388.0),
        (pathlib.Path('FolderZipNested/Folder3/Folder3_1/file5.txt'),
         1576878010.0),
        (pathlib.Path('FolderZipNested/Folder3/file5.txt'), 1576878010.0),
        (pathlib.Path('FolderZipNested/Folder4/file5.txt'), 1576878010.0),
        (pathlib.Path('FolderZipNested/file5.txt'), 1576878010.0)}


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
        f = asd.save_json_listing(path, missing_listing)
        f = at.add_suffix(f, '_missing_fully_included')
        h.reset_time(path, dt_tuple1)

    # verify
    assert missing_listing == {}


def test_missing_not_fully_included(data_path):
    # run
    path8 = data_path / 'Folder8'
    tree8, forbidden8 = aw.walk(path8)
    listing8 = al.tree_to_listing(tree8)

    path0 = data_path / 'Folder0'
    tree0, forbidden0 = aw.walk(path0)
    listing0 = al.tree_to_listing(tree0)

    missing_listing = al.get_missing(listing8, listing0)

    # for logging purpose only
    if debug:
        f = asd.save_json_listing(path8, missing_listing)
        f = at.add_suffix(f, '_missing_not_fully_included')
        h.reset_time(path8, dt_tuple1)

    # load expected
    expected_missing_listing = asd.load_json_listing(
        path8 / '.alfeios_expected' / 'listing_missing_in_Folder0.json')

    # verify
    assert missing_listing == expected_missing_listing


def test_tree_to_listing(data_path):
    path = data_path / 'Folder0' / '.alfeios_expected'

    expected_listing = asd.load_json_listing(path / 'listing.json')
    expected_tree = asd.load_json_tree(path / 'tree.json')

    assert al.tree_to_listing(expected_tree) == expected_listing


def test_listing_to_tree(data_path):
    path = data_path / 'Folder0' / '.alfeios_expected'

    expected_listing = asd.load_json_listing(path / 'listing.json')
    expected_tree = asd.load_json_tree(path / 'tree.json')

    assert al.listing_to_tree(expected_listing) == expected_tree
