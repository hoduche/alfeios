#!/usr/bin/env python

import argparse


def duplicate(args):
    print('duplicate function: ' + args.path)


def missing(args):
    print('missing function: ' + args.old_path + ' -> ' + args.new_path)


if __name__ == '__main__':
    # create the top-level parser
    parser = argparse.ArgumentParser(prog='alfeios')
    subparsers = parser.add_subparsers(
        title='list of subcommands',
        #metavar='<subcommand>',
        #help='<description>'
        )

    # create the parser for the duplicate command
    parser_d = subparsers.add_parser('duplicate', help='find duplicate content',
                                     description='describe duplicate')
    parser_d.add_argument('path', help='directory path')
    parser_d.set_defaults(guiliguili=duplicate)

    # create the parser for the missing command
    parser_m = subparsers.add_parser('missing', help='find missing content')
    parser_m.add_argument('old_path', help='old directory path')
    parser_m.add_argument('new_path', help='new directory path')
    parser_m.set_defaults(guiliguili=missing)

    args = parser.parse_args()
    args.guiliguili(args)

#    print(args)
