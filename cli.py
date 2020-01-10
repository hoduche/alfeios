#!/usr/bin/env python

import argparse


def index(args):
    print('index function: ' + args.path)


def duplicate(args):
    print('duplicate function: ' + args.path)


def missing(args):
    print('missing function: ' + args.old_path + ' -> ' + args.new_path)


def main():
    # create the top-level alfeios parser
    parser = argparse.ArgumentParser(
        description='Enrich your command-line shell with Herculean cleaning capabilities',
        usage='alfeios [-h] <command> [<args>]',
        epilog='''
        ''',
        formatter_class=argparse.RawTextHelpFormatter
    )
    subparsers_factory = parser.add_subparsers(
        title='Alfeios commands',
        prog='alfeios',  # mandatory as usage has been overwritten in alfeios parser
        metavar=' ' * 21  # hack to display help on one-liners
    )

    # create the parser for the index command
    index_help = 'Index content of a root directory'
    parser_i = subparsers_factory.add_parser(
        name='index',
        aliases=['idx', 'i'],
        help=index_help,  # for alfeios help
        description=index_help + ''':
  - Index all file and directory contents in a root directory
    including the inside of zip, tar, gztar, bztar and xztar compressed files
  - Contents are identified by their hash-code, type (file or directory) and size
  - It saves in the root directory:
     - A listing.json file that is a dictionary: content -> list of paths
     - A tree.json.file that is a dictionary: path -> content
     - A forbidden.json file that lists paths with no access
  - In case there is no write access to the root directory,
    the output files are saved in a temp folder of the filesystem with a unique identifier
''',
        epilog='''example:
  alfeios index
  alfeios index D:/Pictures
''',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser_i.add_argument(
        'path',
        nargs='?', default='.',
        help='path to the root directory - default is here'
    )
    parser_i.set_defaults(function_to_call=index)

    # create the parser for the duplicate command
    duplicate_help = 'Find duplicate content in a root directory'
    parser_d = subparsers_factory.add_parser(
        name='duplicate',
        aliases=['dup', 'd'],
        help=duplicate_help,  # for alfeios help
        description=duplicate_help + ''':
  - List all duplicated files and directories in a root directory
  - Save the duplicate listing as a duplicate_listing.json file in the root directory
  - Print the potential space gain
  - Can also dump the full listing.json and tree.json files in the root directory
    with the --save-listing (or -s) argument
  - If a listing.json file is passed as positional argument instead of a root directory,
    the listing is deserialized from the json file instead of being generated
''',
        epilog='''example:
  alfeios duplicate
  alfeios duplicate D:/Pictures
  alfeios duplicate D:/Pictures -s
  alfeios duplicate D:/Pictures/listing.json
''',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser_d.add_argument(
        'path',
        nargs='?', default='.',
        help='path to the root directory (or listing.json) - default is here'
    )
    parser_d.add_argument(
        '-s', '--save-listing', action='store_true',
        help='save complete listing and tree (deactivated by default)'
    )
    parser_d.set_defaults(function_to_call=duplicate)

    # create the parser for the missing command
    missing_help = 'Find missing content in a new root directory from an old root directory'
    parser_m = subparsers_factory.add_parser(
        name='missing',
        aliases=['mis', 'm'],
        help=missing_help,  # for alfeios help
        description=missing_help + ''':
  - List all files and directories that are present in an old root directory
    and that are missing in a new one
  - Save the missing listing as a missing_listing.json file in the new root directory
  - Can also save the full listing.json and tree.json files in the two root directories
    with the --save-listing (or -s) optional argument
  - If a listing.json file is passed as one positional argument instead of a root directory,
    the corresponding listing is deserialized from the json file instead of being generated
''',
        epilog='''examples:
  alfeios missing D:/Pictures E:/AllPictures
  alfeios missing D:/Pictures E:/AllPictures -s
  alfeios missing D:/Pictures/listing.json E:/AllPictures/listing.json
''',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser_m.add_argument(
        'old_path',
        help='path to the old root directory (or old listing.json)'
    )
    parser_m.add_argument(
        'new_path',
        help='path to the new root directory (or new listing.json)'
    )
    parser_m.add_argument(
        '-s', '--save-listing', action='store_true',
        help='save complete listing and tree (deactivated by default)'
    )
    parser_m.set_defaults(function_to_call=missing)

    # parse command line and call appropriate function
    args = parser.parse_args()
    args.function_to_call(args)


# to debug real use cases, set in your Debug Configuration something like:
# Parameters = duplicate D:/Pictures -d
#
# this configuration is  generated automatically by pycharm at first debug
# it can be found in Run/Edit Configurations/Python
if __name__ == '__main__':
    main()
