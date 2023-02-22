import enum
import os
import os.path
import pathlib
import time
import zipfile

# Content data
HASH = 0   # content md5 hashcode
TYPE = 1   # content type : PathType.FILE or PathType.DIR
SIZE = 2   # content size in bytes

# Pointer data
PATH = 0   # filesystem path
MTIME = 1  # last modification time


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


def restore_mtime_after_unpack(archive, extract_dir):
    for f in zipfile.ZipFile(archive, 'r').infolist():
        fullpath = extract_dir / f.filename
        # still need to adjust the dt o/w item will have the current dt
        date_time = time.mktime(f.date_time + (0, 0, -1))
        os.utime(fullpath, (date_time, date_time))
