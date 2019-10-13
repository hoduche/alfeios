import pandas as pd


def parse(path):
    listing = list()
    recursive_parse(path, listing)
    result = pd.DataFrame(listing, columns=['Folder', 'File', 'Size'])
    return result


def recursive_parse(path, listing):
    for each in path.iterdir():
        if each.is_dir():
            recursive_parse(each, listing)
        elif each.is_file():
            folder = each.resolve().expanduser().parent
            file = each.name
            size = each.stat().st_size
            listing.append((folder, file, size))
    return listing


def dump_folder_content(path):
    listing = parse(path)
    listing.to_csv(str(path) + '_listing.csv', index=False)
