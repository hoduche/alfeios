#!/usr/bin/env python

import dsargparse

import alfeios.api


def main():
    # create the top-level alfeios parser
    parser = dsargparse.ArgumentParser(
        description='Enrich your command-line shell with Herculean cleaning'
                    ' capabilities',
        usage='alfeios [-h] <command> [<args>]',
        epilog='''
        ''',
        formatter_class=dsargparse.RawTextHelpFormatter
    )
    subparsers_factory = parser.add_subparsers(
        title='Alfeios commands',
        prog='alfeios',  # mandatory as usage has been overwritten
                         # in alfeios parser
        metavar=' ' * 21  # hack to display help on one-liners
    )

    # create the parser for the index command
    index_help = 'Index content of a root directory'
    parser_i = subparsers_factory.add_parser(
        func=alfeios.api.index,
        aliases=['idx', 'i'],
        help=index_help,  # for alfeios help
        epilog='''example:
  alfeios index
  alfeios index D:/Pictures
''',
        formatter_class=dsargparse.RawTextHelpFormatter
    )
    parser_i.add_argument(
        'path',
        nargs='?', default='.',
        help='path to the root directory'
             ' - default is current working directory'
    )

    # create the parser for the duplicate command
    duplicate_help = 'Find duplicate content in a root directory'
    parser_d = subparsers_factory.add_parser(
        func=alfeios.api.duplicate,
        aliases=['dup', 'd'],
        help=duplicate_help,  # for alfeios help
        epilog='''example:
  alfeios duplicate
  alfeios duplicate D:/Pictures
  alfeios duplicate D:/Pictures -s
  alfeios duplicate D:/Pictures/listing.json
''',
        formatter_class=dsargparse.RawTextHelpFormatter
    )
    parser_d.add_argument(
        'path',
        nargs='?', default='.',
        help='path to the root directory (or listing.json) - '
             'default is current working directory'
    )
    parser_d.add_argument(
        '-s', '--save-listing', action='store_true',
        help='save complete listing and tree (deactivated by default)'
    )

    # create the parser for the missing command
    missing_help = 'Find missing content in a new root directory' \
                   ' from an old root directory'
    parser_m = subparsers_factory.add_parser(
        func=alfeios.api.missing,
        aliases=['mis', 'm'],
        help=missing_help,  # for alfeios help
        epilog='''examples:
  alfeios missing D:/Pictures E:/AllPictures
  alfeios missing D:/Pictures E:/AllPictures -s
  alfeios missing D:/Pictures/listing.json E:/AllPictures/listing.json
''',
        formatter_class=dsargparse.RawTextHelpFormatter
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

    # parse command line and call appropriate function
    return parser.parse_and_run()


# to debug real use cases, set in your Debug Configuration something like:
# Parameters = duplicate D:/Pictures -d
#
# this configuration is  generated automatically by pycharm at first debug
# it can be found in Run/Edit Configurations/Python
if __name__ == '__main__':
    main()
