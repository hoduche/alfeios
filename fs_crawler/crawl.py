import collections
import hashlib
import os
import pathlib

import pandas as pd

BLOCK_SIZE = 65536  # ie 64 Ko
FILE_TYPE = 'FILE'
DIR_TYPE = 'DIR'


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
    content_listing = collections.defaultdict(list)  # {(hash, type, int): [pathlib.Path]}
    dirs_content_hash = {}  # {pathlib.Path: hash}
    dirs_size = {}  # {pathlib.Path: int}

    for dir_path_string, subdir_names, file_names in os.walk(path, topdown=False):
        dir_path = pathlib.Path(dir_path_string)
        dir_content_hash_set = set()
        dir_size = 0

        for file_name in file_names:
            file_path = dir_path / file_name

            file_hasher = hashlib.md5()
            with open(file_path, 'rb') as file_content:
                content_stream = file_content.read(BLOCK_SIZE)
                while len(content_stream) > 0:
                    file_hasher.update(content_stream)
                    content_stream = file_content.read(BLOCK_SIZE)
            file_content_hash = file_hasher.hexdigest()
            dir_content_hash_set.add(file_content_hash)

            file_content_size = file_path.stat().st_size
            dir_size += file_content_size

            file_content_key = (file_content_hash, FILE_TYPE, file_content_size)
            content_listing[file_content_key].append(file_path)

        for subdir_name in subdir_names:
            subdir_path = dir_path / subdir_name

            subdir_content_hash = dirs_content_hash[subdir_path]
            dir_content_hash_set.add(subdir_content_hash)

            subdir_size = dirs_size[subdir_path]
            dir_size += subdir_size

        if dir_content_hash_set:
            file_content_hash_list = sorted(dir_content_hash_set)
            dir_content = '/n'.join(file_content_hash_list)
            dir_content_hash = hashlib.md5(dir_content.encode()).hexdigest()
            dirs_content_hash[dir_path] = dir_content_hash

            dirs_size[dir_path] = dir_size

            dir_content_key = (dir_content_hash, DIR_TYPE, dir_size)
            content_listing[dir_content_key].append(dir_path)

    return content_listing, dirs_content_hash, dirs_size


if __name__ == '__main__':
    project_path = pathlib.Path(__file__).resolve().expanduser().parent.parent
    tests_data_path = project_path / 'tests' / 'data'
    listing, hashes, sizes = main(tests_data_path / 'Folder0')
    print('------------------')
    tab = '    '
    for x in listing:
        print(x)
        for y in listing[x]:
            print(tab + str(y))
    print('------------------')
    for x in hashes:
        print(str(x) + tab + hashes[x])
    print('------------------')
    for x in sizes:
        print(str(x) + tab + str(sizes[x]))
    print('------------------')
