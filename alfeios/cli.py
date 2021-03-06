#!/usr/bin/env python

import sys

import colorama
import dsargparse

from alfeios import __version__
import alfeios.api


def main():
    colorama.init(autoreset=True)

    # create the top-level alfeios parser
    parser = dsargparse.ArgumentParser(
        description='Enrich your command-line shell with Herculean cleaning '
                    'capabilities',
        usage='alfeios [-h] <command> [<args>]',
        epilog="See 'alfeios <command> -h' for help on a specific command",
        formatter_class=dsargparse.RawTextHelpFormatter
    )
    parser.add_argument('-V', '--version', action='version',
                        version=__version__)

    subparsers_factory = parser.add_subparsers(
        title='Alfeios commands',
        prog='alfeios',  # mandatory for subcommand help
                         # as usage has been overwritten in alfeios parser
        metavar=' ' * 21  # hack to display help on one-liners
    )

    # create the parser for the index command
    parser_i = subparsers_factory.add_parser(
        func=alfeios.api.index,
        aliases=['idx', 'i'],
        help='Index content of a root directory',
        epilog='''example:
  alfeios index
  alfeios idx D:/Pictures
  alfeios i
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
    parser_d = subparsers_factory.add_parser(
        func=alfeios.api.duplicate,
        aliases=['dup', 'd'],
        help='Find duplicate content in a root directory',
        epilog='''example:
  alfeios duplicate
  alfeios dup -s D:/Pictures
  alfeios d D:/Pictures/.alfeios/2020_01_29_10_29_39_listing.json
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
        '-s', '--save-index', action='store_true',
        help='save the listing.json, tree.json and forbidden.json files in the'
             ' root directory'
    )

    # create the parser for the missing command
    parser_m = subparsers_factory.add_parser(
        func=alfeios.api.missing,
        aliases=['mis', 'm'],
        help='Find missing content in a new root directory from an old root'
             ' directory',
        epilog='''examples:
  alfeios missing D:/Pictures E:/AllPictures
  alfeios mis -s D:/Pictures E:/AllPictures
  alfeios m D:/Pictures/.alfeios/2020_01_29_10_29_39_listing.json E:/AllPics
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
        '-s', '--save-index', action='store_true',
        help='save the listing.json, tree.json and forbidden.json files in the'
             ' 2 root directories'
    )

    # parse command line and call appropriate function
    if len(sys.argv) == 1 or sys.argv[1] in ['help', 'h']:
        parser.print_help(sys.stderr)
        sys.exit(1)

    try:
        return parser.parse_and_run()
    except KeyboardInterrupt:
        print('''
Process interrupted''', file=sys.stderr)
        sys.exit(1)


# to debug real use cases, set in your Debug Configuration something like:
# Parameters = duplicate D:/Pictures -d
#
# this configuration is  generated automatically by pycharm at first debug
# it can be found in Run/Edit Configurations/Python
if __name__ == '__main__':
    main()
