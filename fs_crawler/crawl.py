import pandas as pd


def parse(path):
    """
    Recursively crawl through a root folder to list all its files
    (with their parent folder and size)

    :param path: path of the root folder to parse
    :type path: pathlib.Path

    :return: DataFrame with one row per file and with columns:
             * Folder: path of the file's parent folder - pathlib.Path
             * File: file name - str
             * Size: size of the file in bytes - unsigned int
    :rtype: pandas.DataFrame
    """
    listing = list()
    _recursive_parse(path, listing)
    result = pd.DataFrame(listing, columns=['Folder', 'File', 'Size'])
    return result


def _recursive_parse(path, listing):
    for each in path.iterdir():
        if each.is_dir():
            _recursive_parse(each, listing)
        elif each.is_file():
            folder = each.resolve().expanduser().parent
            file = each.name
            size = each.stat().st_size
            listing.append((folder, file, size))
    return listing


def dump_folder_content(path):
    """
    Dump root folder files listing in a csv file

    :param path: path of the root folder to parse
    :type path: pathlib.Path
    """
    listing = parse(path)
    listing.to_csv(str(path) + '_listing.csv', index=False)
