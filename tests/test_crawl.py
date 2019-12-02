import pathlib

import fs_crawler.crawl as fsc

tests_data_path = pathlib.Path(__file__).resolve().expanduser().parent / 'data'


# todo parametrize for Folder3 and co
def test_crawl():
    # run
    listing, tree = fsc.crawl(tests_data_path / 'Folder0')

    # for logging purpose only
    fsc.dump_json_listing(listing, tests_data_path / 'Folder0_listing.json')
    fsc.dump_json_tree(tree, tests_data_path / 'Folder0_tree.json')

    # load expected
    expected_listing = fsc.load_json_listing(tests_data_path / 'Folder0_listing_expected.json')
    expected_tree = fsc.load_json_tree(tests_data_path / 'Folder0_tree_expected.json')

    # verify
    assert expected_listing == listing
    assert expected_tree == tree


def test_crawl_with_exclusions():
    # run
    listing, tree = fsc.crawl(tests_data_path / 'Folder0',
                              exclusion=['Folder3', 'Folder4_1', 'file3.txt', 'groundhog.png'])

    # for logging purpose only
    fsc.dump_json_listing(listing, tests_data_path / 'Folder0_listing_with_exclusions.json')
    fsc.dump_json_tree(tree, tests_data_path / 'Folder0_tree_with_exclusions.json')

    # load expected
    expected_listing = fsc.load_json_listing(tests_data_path / 'Folder0_listing_with_exclusions_expected.json')
    expected_tree = fsc.load_json_tree(tests_data_path / 'Folder0_tree_with_exclusions_expected.json')

    # verify
    assert expected_listing == listing
    assert expected_tree == tree


def test_crawl_with_exclusions2():
    # run
    listing0_no3, tree0_no3 = fsc.crawl(tests_data_path / 'Folder0', exclusion=['Folder3'])
    listing3, tree3 = fsc.crawl(tests_data_path / 'Folder0' / 'Folder3')
    listing, tree = fsc.unify([listing0_no3, listing3], [tree0_no3, tree3])
    listing0_full, tree0_full = fsc.crawl(tests_data_path / 'Folder0')

    # for logging purpose only
    fsc.dump_json_listing(listing, tests_data_path / 'listing.json')
    fsc.dump_json_listing(listing0_full, tests_data_path / 'listing0_full.json')
    fsc.dump_json_tree(tree, tests_data_path / 'tree.json')
    fsc.dump_json_tree(tree0_full, tests_data_path / 'tree0_full.json')

    # verify
#    assert listing == listing0_full
    assert tree == tree0_full


def test_crawl_asynchronous():
    existing_listing_path = tests_data_path / 'Folder0_listing_with_exclusions_expected.json'
    existing_tree_path = tests_data_path / 'Folder0_tree_with_exclusions_expected.json'
    listing, tree = fsc.crawl(tests_data_path / 'Folder0',
                              json_listing_path=existing_listing_path,
                              json_tree_path=existing_tree_path)

    expected_listing = fsc.load_json_listing(tests_data_path / 'Folder0_listing_with_exclusions_expected.json')
    expected_tree = fsc.load_json_tree(tests_data_path / 'Folder0_tree_with_exclusions_expected.json')

    listings = [listing, listing, listing, expected_listing]
    trees = [expected_tree, tree]

    l, t = fsc.unify(listings, trees)
    el = fsc.load_json_listing(tests_data_path / 'Folder0_listing_expected.json')
    assert el == l
    et = fsc.load_json_tree(tests_data_path / 'Folder0_tree_expected.json')
    assert et == t

    expected_listing = fsc.load_json_listing(tests_data_path / 'Folder0_listing_expected.json')
#    assert sorted(expected_listing) == sorted(listing)
    expected_tree = fsc.load_json_tree(tests_data_path / 'Folder0_tree_expected.json')
    assert sorted(expected_tree) == sorted(tree)
