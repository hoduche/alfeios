import pathlib

import pandas as pd
import pandas.util.testing as pdt

import fs_crawler.crawl as fsc

tests_data_path = pathlib.Path(__file__).resolve().expanduser().parent / 'data'


def test_parse():
    listing = fsc.parse(tests_data_path / 'folder1')
    expected = pd.read_csv(str(tests_data_path / 'folder1_listing.csv'))
    expected['Folder'] = expected['Folder'].apply(lambda x: pathlib.Path(x))
    pdt.assert_frame_equal(listing, expected)


def test_main():
    listing, hashes, sizes = fsc.main(tests_data_path / 'Folder0')

    expected_listing = fsc.load_json_listing(tests_data_path / 'Folder0_listing_expected.json')
    assert expected_listing == listing
    expected_hashes = fsc.load_json_path_dict(tests_data_path / 'Folder0_hashes_expected.json')
    assert expected_hashes == hashes
    expected_sizes = fsc.load_json_path_dict(tests_data_path / 'Folder0_sizes_expected.json')
    assert expected_sizes == sizes
