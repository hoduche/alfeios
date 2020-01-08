import argparse

import alfeios.api as aa


def duplicate(args=None):
    description = '''List all duplicated files and directories in
a root directory passed as the --path (or -p) argument.
Save the duplicate listing as a duplicate_listing.json file in the root directory.
Print the potential space gain in Gigabytes.
Can also dump the full listing.json and tree.json files in the root directory
with the --dump-listing (or -d) argument.
If a listing.json file is passed as the --path (or -p) argument instead of a root
directory, the listing is deserialized from the json file instead of being generated.
'''

    examples = '''examples:
  duplicate
  duplicate -p D:/Pictures
  duplicate -p D:/Pictures -d
  '''

    arg_parser = argparse.ArgumentParser(description=description, epilog=examples,
                                         formatter_class=argparse.RawTextHelpFormatter)
    arg_parser.add_argument('-p', '--path', type=str, action='store', default='.',
                            help='path to root directory to walk (default is here)')
    arg_parser.add_argument('-d', '--dump-listing', dest='dump_listing', action='store_true', default=False,
                            help='dump complete listing and tree (deactivated by default)')
    args = arg_parser.parse_args(args=args)

    aa.duplicate(args.path, args.dump_listing)


# to debug real use cases, set in your Debug Configuration something like:
# Parameters = -p D:/Pictures -d
#
# this configuration is  generated automatically by pycharm at first debug
# it can be found in Run/Edit Configurations/Python
if __name__ == '__main__':
    import sys

    args = sys.argv[1:]
    duplicate(args=args)
