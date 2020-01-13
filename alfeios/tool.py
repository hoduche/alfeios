import os.path
import pathlib


def build_relative_path(absolute_path, start_path):
    return pathlib.Path(os.path.relpath(str(absolute_path), start=start_path))
