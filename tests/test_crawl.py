import pathlib as p

import pandas as pd
import pandas.util.testing as pdt

import fs_crawler.crawl as fsc

tests_data_path = p.Path(__file__).resolve().expanduser().parent / 'data'


def test_parse():
    listing = fsc.parse(tests_data_path / 'folder1')
    expected = pd.read_csv(str(tests_data_path / 'folder1_listing.csv'))
    expected['Folder'] = expected['Folder'].apply(lambda x: p.Path(x))
    pdt.assert_frame_equal(listing, expected)
