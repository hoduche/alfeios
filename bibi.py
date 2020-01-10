#!/usr/bin/env python

import argparse


def index(args):
    print('index function: ' + args.path)


def duplicate(args):
    print('duplicate function: ' + args.path)


def missing(args):
    print('missing function: ' + args.old_path + ' -> ' + args.new_path)


description_temp = '''Alfeios commands:
        
   index (idx)      Index content of a directory
   duplicate (dup)  Find duplicate content in a directory
   missing (mis)    Find missing content from an old directory in a new directory
        '''

if __name__ == '__main__':
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
    index_help = 'Index content of a directory'
    parser_i = subparsers_factory.add_parser(
        name='index',
        aliases=['idx', 'i'],
        help=index_help,  # for alfeios help
        description=index_help,  # for command help
        epilog='''example:
    like
    example 1
    example 2
    ''',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser_i.add_argument('path', help='directory path')
    parser_i.set_defaults(guiliguili=index)

    # create the parser for the duplicate command
    duplicate_help = 'Find duplicate content in a directory'
    parser_d = subparsers_factory.add_parser(
        name='duplicate',
        aliases=['dup', 'd'],
        help=duplicate_help,  # for alfeios help
        description=duplicate_help,  # for command help
        epilog='''example:
    like
    example 1
    example 2
    ''',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser_d.add_argument('path', help='directory path')
    parser_d.set_defaults(guiliguili=duplicate)

    # create the parser for the missing command
    missing_help = 'Find missing content in a new directory from an old directory'
    parser_m = subparsers_factory.add_parser(
        name='missing',
        aliases=['mis', 'm'],
        help=missing_help,  # for alfeios help
        description=missing_help,  # for command help
        epilog='''example:
        like
        example 1
        example 2
        ''',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser_m.add_argument('old_path', help='old directory path')
    parser_m.add_argument('new_path', help='new directory path')
    parser_m.set_defaults(guiliguili=missing)

    args = parser.parse_args()
    args.guiliguili(args)
