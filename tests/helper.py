import datetime
import json
import os
import shutil
import time

import pdfkit  # to create pdf file (alt: fpdf2)
import PIL.Image
from pypdf import PdfReader, PdfWriter  # to modify MetaData (alt: pikepdf)

import alfeios.tool as at


def create_png(path, dt_tuple, colors, w=36, h=65):
    c1, c2, c3 = colors.split()
    img = PIL.Image.new('RGB', (3 * w, h), color=c1)
    la1 = PIL.Image.new('RGB', (1 * w, h), color=c2)
    la2 = PIL.Image.new('RGB', (1 * w, h), color=c3)
    img.paste(la1, (1 * w, 0))
    img.paste(la2, (2 * w, 0))
    img.save(path)
    reset_time(path, dt_tuple)


def create_txt(path, dt_tuple, content):
    path.write_text(content)
    reset_time(path, dt_tuple)


def create_pdf(path, dt_tuple, content):
    # create pdf file (with pdfkit - alternative: fpdf2)
    pdfkit.from_string(content, path)

    # modify MetaData to force CreationDate (with pypdf - alternative: pikepdf)
    reader = PdfReader(path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)
    writer.add_metadata(reader.metadata)
    datetime_object = datetime.datetime(*(dt_tuple[:-2]))
    utc_time = "+02'00'"
    datetime_string = datetime_object.strftime(f"D:%Y%m%d%H%M%S{utc_time}")
    writer.add_metadata({"/CreationDate": datetime_string})

    # write file
    with path.open(mode='wb') as f:
        writer.write(f)
    reset_time(path, dt_tuple)


def create_zip(path, dt_tuple, paths):
    shutil.make_archive(path, 'zip', paths)
    reset_time(path.parent / (path.name + ".zip"), dt_tuple)


def reset_time(path, dt_tuple):
    datetime_float = time.mktime(dt_tuple)
    os.utime(path, (datetime_float, datetime_float))


def log_sorted_json_listing(file_path):
    separator = '-' * 70
    result = []
    json_listing = json.loads(file_path.read_text())
    for content in sorted(json_listing.keys()):
        result.extend([separator, content, separator])
        for pointer in sorted(json_listing[content]):
            result.append(str(pointer))
        result.append('')
    output_path = file_path.parent / (file_path.stem + '_ordered.txt')
    output_path.write_text('\n'.join(result))


def log_sorted_json_tree(file_path):
    result = []
    json_tree = json.loads(file_path.read_text())
    for pointer in sorted(json_tree.keys()):
        result.append(pointer + ': ' + str(json_tree[pointer]))
    output_path = file_path.parent / (file_path.stem + '_ordered.txt')
    output_path.write_text('\n'.join(result))


def remove_last_json_tree(dir_path):
    cache_path = dir_path / '.alfeios'
    times = []
    for tree_path in cache_path.glob('*_tree.json'):
        times.append(at.read_datetime_tag(tree_path.name[:19]))
    max_time = max(times)
    max_time_tag = at.build_datetime_tag(max_time)
    last_json_tree = cache_path / (max_time_tag + '_tree.json')
    os.remove(last_json_tree)
