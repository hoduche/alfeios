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
    archive_mtime = archive.stat().st_mtime
    os.utime(extract_dir, (archive_mtime, archive_mtime))
    info_map = {f.filename: f.date_time
                for f in zipfile.ZipFile(archive, 'r').infolist()}
    for file in extract_dir.rglob("*"):
        if file.name in info_map:
            # still need to adjust the dt o/w item will have the current dt
            mtime = time.mktime(info_map[file.name] + (0, 0, -1))
        else:
            mtime = archive_mtime
        os.utime(file, (mtime, mtime))
