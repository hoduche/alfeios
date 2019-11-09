import ast
import collections
import hashlib
import json
import os
import pathlib
import pickle

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


tabulation = 4 * ' '


def print_simple_dict(simple_dict):
    for each_key in simple_dict:
        print(str(each_key) + tabulation + str(simple_dict[each_key]))


def print_dict_of_list(dict_of_list):
    for each_key in dict_of_list:
        print(each_key)
        for each_value in dict_of_list[each_key]:
            print(tabulation + str(each_value))


def dump_json_listing(listing, file_path):
    serializable_listing = {str(tuple_key): [str(path) for path in path_list]
                            for tuple_key, path_list in listing.items()}
    json_listing = json.dumps(serializable_listing)
    file_path.write_text(json_listing)


def load_json_listing(file_path):
    json_listing = file_path.read_text()
    serializable_listing = json.loads(json_listing)
    dict_listing = {ast.literal_eval(tuple_key): [pathlib.Path(path) for path in path_list]
                    for tuple_key, path_list in serializable_listing.items()}
    listing = collections.defaultdict(list, dict_listing)
    return listing


def dump_json_path_dict(path_dict, file_path):
    serializable_path_dict = {str(path_key): value for path_key, value in path_dict.items()}
    json_path_dict = json.dumps(serializable_path_dict)
    file_path.write_text(json_path_dict)


def load_json_path_dict(file_path):
    json_path_dict = file_path.read_text()
    serializable_path_dict = json.loads(json_path_dict)
    path_dict = {pathlib.Path(path_key): value for path_key, value in serializable_path_dict.items()}
    return path_dict


if __name__ == '__main__':
    project_path = pathlib.Path(__file__).resolve().expanduser().parent.parent
    tests_data_path = project_path / 'tests' / 'data'
    listing, hashes, sizes = main(tests_data_path / 'Folder0')
# todo   listing, hashes, sizes = main(project_path.parent) crashes on .git
# todo   replace os.walk by a personal recursion to avoid certain files/folder (like .gitignore)

    print('------------------')
    print_dict_of_list(listing)
    dump_json_listing(listing, tests_data_path / 'Folder0_listing.json')
    pickle.dump(listing, open(str(tests_data_path / 'Folder0_listing.pickle'), 'wb'))
    print('------------------')
    print_simple_dict(hashes)
    dump_json_path_dict(hashes, tests_data_path / 'Folder0_hashes.json')
    pickle.dump(hashes, open(str(tests_data_path / 'Folder0_hashes.pickle'), 'wb'))
    print('------------------')
    print_simple_dict(sizes)
    dump_json_path_dict(sizes, tests_data_path / 'Folder0_sizes.json')
    pickle.dump(sizes, open(str(tests_data_path / 'Folder0_sizes.pickle'), 'wb'))
    print('------------------')
