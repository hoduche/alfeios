# import pathlib
#
# import pytest
#
# import alfeios.api as api
# import alfeios.serialize as asd
#
# tests_data_path = pathlib.Path(__file__).parent / 'data'
#
# folders = [('Folder0', 'Folder0'),
#            ('Folder0/Folder3', 'Folder0/Folder3'),
#            ('FolderZipFile', 'FolderZipFile'),
#            ('FolderZipFolder', 'FolderZipFolder'),
#            ('FolderZipNested', 'FolderZipNested')]
# names = [each[1] for each in folders]
#
#
# @pytest.mark.parametrize(argnames='folder, name', argvalues=folders, ids=names)
# def test_index(folder, name):
#     path = tests_data_path / folder
#
#     # run
#     api.index(path)
#     listing = asd.load_json_listing(
#         path / '.alfeios_expected' / 'listing.json',
#         start_path=tests_data_path)
#
#     # load expected
#     expected_listing = asd.load_json_listing(
#         path / '.alfeios_expected' / 'listing.json',
#         start_path=tests_data_path)
#     expected_tree = asd.load_json_tree(
#         path / '.alfeios_expected' / 'tree.json',
#         start_path=tests_data_path)
#
#     # verify
#     assert listing == expected_listing
#     assert tree == expected_tree
#     assert forbidden == {}
#
#
# def test_walk_with_exclusions():
#     path = tests_data_path / 'Folder0'
#     exclusion = {'Folder3', 'Folder4_1', 'file3.txt', 'groundhog.png'}
#
#     # run
#     listing, tree, forbidden = aw.walk(path, exclusion=exclusion)
#
#     # for logging purpose only
#     if debug:
#         asd.save_json_index(path, listing, tree, forbidden,
#                             start_path=tests_data_path,
#                             prefix='with_exclusions_')
#
#     # load expected
#     expected_listing = asd.load_json_listing(
#         path / '.alfeios_expected' / 'listing_with_exclusions.json',
#         start_path=tests_data_path)
#     expected_tree = asd.load_json_tree(
#         path / '.alfeios_expected' / 'tree_with_exclusions.json',
#         start_path=tests_data_path)
#
#     # verify
#     assert listing == expected_listing
#     assert tree == expected_tree
#     assert forbidden == {}
#
#
# def test_unify():
#     path = tests_data_path / 'Folder0'
#
#     # run
#     listing0_no3, tree0_no3, forbidden0_no3 = aw.walk(path,
#                                                       exclusion={'Folder3'})
#     listing3, tree3, forbidden3 = aw.walk(path / 'Folder3')
#     listing, tree, forbidden = aw.unify([listing0_no3, listing3],
#                                         [tree0_no3, tree3],
#                                         [forbidden0_no3, forbidden3])
#     listing0_full, tree0_full, forbidden0_full = aw.walk(path)
#
#     # verify
#     listing.pop(('7e472b2b54ba97314c63988db267d125', 'DIR', 2698920))
#     listing0_full.pop(('4f8c48630a797715e8b86466e0218aa1', 'DIR', 3598557))
#     assert listing == listing0_full
#     tree.pop(tests_data_path / 'Folder0')
#     tree0_full.pop(tests_data_path / 'Folder0')
#     assert tree == tree0_full
#     assert forbidden == forbidden0_full
#
#
# def test_duplicate():
#     path = tests_data_path / 'Folder0' / 'Folder3'
#
#     # run
#     listing, tree, forbidden = aw.walk(path)
#     duplicate_listing, size_gain = aw.get_duplicate(listing)
#
#     # for logging purpose only
#     if debug:
#         asd.save_json_index(path, duplicate_listing,
#                             start_path=tests_data_path,
#                             prefix='duplicate_')
#
#     # load expected
#     expected_duplicate_listing = asd.load_json_listing(
#         path / '.alfeios_expected' / 'duplicate_listing.json',
#         start_path=tests_data_path)
#
#     # verify
#     assert duplicate_listing == expected_duplicate_listing
#     assert size_gain == 367645
#
#
# def test_duplicate_on_listing():
#     path = tests_data_path / 'Folder0' / 'Folder3'
#
#     # run
#     listing, tree, forbidden = aw.walk(path)
#     duplicate_listing, size_gain = aw.get_duplicate(listing)
#
#     asd.save_json_index(path, duplicate_listing,
#                         start_path=tests_data_path,
#                         prefix='duplicate_')
#
#     # load expected
#     expected_duplicate_listing = asd.load_json_listing(
#         path / '.alfeios_expected' / 'duplicate_listing.json',
#         start_path=tests_data_path)
#
#     # verify
#     assert duplicate_listing == expected_duplicate_listing
#     assert size_gain == 367645
#
#
# def test_duplicate_with_zip():
#     # run
#     listing, tree, forbidden = aw.walk(tests_data_path)
#     duplicate_listing, size_gain = aw.get_duplicate(listing)
#
#     # for logging purpose only
#     if debug:
#         asd.save_json_index(tests_data_path, duplicate_listing,
#                             start_path=tests_data_path,
#                             prefix='duplicate_with_zip_')
#
#     # verify
#     assert duplicate_listing[
#                ('4f8c48630a797715e8b86466e0218aa1', 'DIR', 3598557)] == \
#         {tests_data_path / 'Folder0',
#          tests_data_path / 'FolderZipFile',
#          tests_data_path / 'FolderZipFolder',
#          tests_data_path / 'FolderZipNested'}
#
#
# def test_missing_fully_included():
#     path = tests_data_path / 'Folder0'
#
#     # run
#     listing3, tree3, forbidden3 = aw.walk(path / 'Folder3')
#     listing0, tree0, forbidden0 = aw.walk(path)
#     missing_listing = aw.get_missing(listing3, listing0)
#
#     # for logging purpose only
#     if debug:
#         asd.save_json_index(path, missing_listing, start_path=tests_data_path,
#                             prefix='missing_fully_included_')
#
#     # verify
#     assert missing_listing == {}
#
#
# def test_missing_not_fully_included():
#     path = tests_data_path / 'Folder0'
#
#     # run
#     listing8, tree8, forbidden8 = aw.walk(tests_data_path / 'Folder8')
#     listing0, tree0, forbidden0 = aw.walk(path)
#     missing_listing = aw.get_missing(listing8, listing0)
#
#     # for logging purpose only
#     if debug:
#         asd.save_json_index(path, missing_listing, start_path=tests_data_path,
#                             prefix='missing_not_fully_included_')
#
#     # load expected
#     expected_missing_listing = asd.load_json_listing(
#         path / '.alfeios_expected' / 'missing_from_Folder8.json',
#         start_path=tests_data_path)
#
#     # verify
#     assert missing_listing == expected_missing_listing
