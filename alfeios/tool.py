import enum
import os.path
import pathlib


HASH = 0
TYPE = 1
SIZE = 2

PATH = 0
MTIME = 1


class PathType(str, enum.Enum):
    FILE = 'FILE'
    DIR = 'DIR'


def build_relative_path(absolute_path, start_path):
    return pathlib.Path(os.path.relpath(str(absolute_path), start=start_path))


def natural_size(num, unit='B'):
    for prefix in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            result = f'{num:.1f} {prefix}{unit}'
            return result
        num /= 1024.0
    result = f'{num:.1f} Yi{unit}'
    return result
