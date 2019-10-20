import collections
import hashlib
import os
import pathlib

import pandas as pd

MAX_SIZE = 1048576  # ie  1 Mo
BLOCK_SIZE = 65536  # ie 64 Ko


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


def main(path):
    content_listing = collections.defaultdict(list)
    dirs_listing = {}

    for dir_path, subdir_names, file_names in os.walk(path, topdown=False):
        hash_set = set()

        for file_name in file_names:
            file_path = pathlib.Path(dir_path) / file_name
            file_hasher = hashlib.md5()
            with open(file_path, 'rb') as file_content:
                content_stream = file_content.read(BLOCK_SIZE)
                while len(content_stream) > 0:
                    file_hasher.update(content_stream)
                    content_stream = file_content.read(BLOCK_SIZE)
            file_content_hash = file_hasher.hexdigest()
            file_content_size = file_path.stat().st_size
            file_content_key = (file_content_hash, 'FILE', file_content_size)
            content_listing[file_content_key].append(str(file_path))
            hash_set.add(file_content_hash)

        for subdir_name in subdir_names:
            subdir_path = pathlib.Path(dir_path) / subdir_name
            subdir_content_hash = dirs_listing[str(subdir_path)]
            hash_set.add(subdir_content_hash)

        if hash_set:
            dir_content = str(hash_set).encode()
            dir_content_hash = hashlib.md5(dir_content).hexdigest()
            dir_content_key = (dir_content_hash, 'DIR', 0)
            content_listing[dir_content_key].append(str(dir_path))
            dirs_listing[str(dir_path)] = dir_content_hash

    return content_listing, dirs_listing


if __name__ == '__main__':
    tests_data_path = pathlib.Path(__file__).resolve().expanduser()
    tests_data_path = tests_data_path.parent.parent / 'tests' / 'data'
    content_listing, dirs_listing = main(tests_data_path / 'Folder0')
    print('------------------')
    tab = '    '
    for x in content_listing:
        print(tab + str(x))
        for y in content_listing[x]:
            print(2 * tab + y)
    print('------------------')
    for x in dirs_listing:
        print(tab + x)
        print(2 * tab + dirs_listing[x])
    print('------------------')
