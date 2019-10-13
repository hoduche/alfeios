import pathlib as p

import pandas as pd
import pandas.util.testing as pdt

import fs_crawler.crawl as fsc


def test_parse():
    tests_data_path = p.Path().resolve().expanduser() / 'data'
    listing = fsc.parse(tests_data_path / 'folder1')
    expected = pd.read_csv(str(tests_data_path / 'folder1_listing.csv'))
    expected['Folder'] = expected['Folder'].apply(lambda x: p.Path(x))
    pdt.assert_frame_equal(listing, expected)
