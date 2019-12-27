import argparse

import fs_walker.api as fs


def missing(args=None):
    description = '''List all files and directories that
are present in an old root directory passed as the --old-path (or -o) argument
and that are missing in a new one passed as the --new-path (or -n) argument.
Save the missing listing as a missing_listing.json file in the new root directory.
Can also dump the full listing.json and tree.json files in the two root directories
with the --dump-listing (or -d) argument.
If a listing.json file is passed as the --old-path (or -o) argument 
or as the --new-path (or -n) argument instead of a root directory,
the corresponding listing is deserialized from the json file instead of being generated.
'''

    examples = '''examples:
  missing -o D:/Pictures
  missing -o D:/Pictures -n E:/AllPictures
  missing -o D:/Pictures -n E:/AllPictures -d
  '''

    arg_parser = argparse.ArgumentParser(description=description, epilog=examples,
                                         formatter_class=argparse.RawTextHelpFormatter)
    arg_parser.add_argument('-o', '--old-path', dest='old_path', type=str, action='store', default='.',
                            help='path to old root directory to walk (default is here)')
    arg_parser.add_argument('-n', '--new-path', dest='new_path', type=str, action='store', default='.',
                            help='path to new root directory to walk (default is here)')
    arg_parser.add_argument('-d', '--dump-listing', dest='dump_listing', action='store_true', default=False,
                            help='dump complete listing and tree (deactivated by default)')
    args = arg_parser.parse_args(args=args)

    fs.missing(args.old_path, args.new_path, args.dump_listing)


# to debug real use cases, set in your Debug Configuration something like:
# Parameters = -o D:/Pictures -n E:/AllPictures -d
#
# this configuration is  generated automatically by pycharm at first debug
# it can be found in Run/Edit Configurations/Python
if __name__ == '__main__':
    import sys

    args = sys.argv[1:]
    missing(args=args)
