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
        help='index content of a root directory',
        epilog='''example:
  alfeios index
  alfeios idx -n D:/Pictures
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
    parser_i.add_argument(
        '-n', '--no-cache', action='store_true',
        help='do not use cache already saved in .alfeios directory'
    )
    parser_i.add_argument(
        '-p', '--progress-bar', action='store_true',
        help='show command progress with a progress bar'
    )

    # create the parser for the duplicate command
    parser_d = subparsers_factory.add_parser(
        func=alfeios.api.duplicate,
        aliases=['dup', 'd'],
        help='find duplicate content in a root directory',
        epilog='''example:
  alfeios duplicate
  alfeios dup -ns D:/Pictures
  alfeios d D:/Pictures/.alfeios/2020_01_29_10_29_39_tree.json
''',
        formatter_class=dsargparse.RawTextHelpFormatter
    )
    parser_d.add_argument(
        'path',
        nargs='?', default='.',
        help='path to the root directory (or tree.json) - '
             'default is current working directory'
    )
    parser_d.add_argument(
        '-n', '--no-cache', action='store_true',
        help='do not use cache already saved in .alfeios directory'
    )
    parser_d.add_argument(
        '-s', '--save-index', action='store_true',
        help='save tree.json and forbidden.json files in the root directory'
    )

    # create the parser for the missing command
    parser_m = subparsers_factory.add_parser(
        func=alfeios.api.missing,
        aliases=['mis', 'm'],
        help='find missing content in a new root directory from an old root'
             ' directory',
        epilog='''examples:
  alfeios missing D:/Pictures E:/AllPictures
  alfeios mis -ns D:/Pictures E:/AllPictures
  alfeios m D:/Pictures/.alfeios/2020_01_29_10_29_39_tree.json E:/AllPics
''',
        formatter_class=dsargparse.RawTextHelpFormatter
    )
    parser_m.add_argument(
        'old_path',
        help='path to the old root directory (or old tree.json)'
    )
    parser_m.add_argument(
        'new_path',
        help='path to the new root directory (or new tree.json)'
    )
    parser_m.add_argument(
        '-n', '--no-cache', action='store_true',
        help='do not use cache already saved in the 2 .alfeios directories'
    )
    parser_m.add_argument(
        '-s', '--save-index', action='store_true',
        help='save the tree.json and forbidden.json files in the 2 root'
             ' directories'
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
