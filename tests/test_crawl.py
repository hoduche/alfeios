import pathlib

import fs_crawler.crawl as fsc

tests_data_path = pathlib.Path(__file__).resolve().expanduser().parent / 'data'


def test_crawl():
    listing, tree = fsc.crawl(tests_data_path / 'Folder0')

    expected_listing = fsc.load_json_listing(tests_data_path / 'Folder0_listing_expected.json')
    assert expected_listing == listing
    expected_tree = fsc.load_json_tree(tests_data_path / 'Folder0_tree_expected.json')
    assert expected_tree == tree
