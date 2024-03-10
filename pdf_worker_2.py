import re, sys
from pypdf import PdfReader, PdfWriter, Transformation, PageObject, PaperSize
from pypdf.generic import RectangleObject
import os

def change_filename(filepath, new_filename):
    directory, filename = os.path.split(filepath)
    new_filepath = os.path.join(directory, new_filename)
    return new_filepath

files = os.listdir("./Input")
in_path_list = []
out_path_list = []

for i in range(len(files)):
    in_fpath = "./Input/" + files[i]
    out_fpath = "./Output/" + files[i]

    if os.path.exists(out_fpath):
        continue

    # Part 1; remove sequential pages

    # Initialize PDF reader & writer objects
    in_file = PdfReader(in_fpath, 'rb') 
    writer_1 = PdfWriter()

    # To extract text from a PDF page
    def extract_text(pageObj):
        # Works fine for PDFs I tested with, yet it may fail for others
        # See: https://stackoverflow.com/questions/34837707/how-to-extract-text-from-a-pdf-file
        text = pageObj.extract_text()
        return re.sub('[\n\r\s]+', '', text)

    prev_pg_text = extract_text(in_file.pages[0])
    del_pages = []

    for pgNo in range(1, len(in_file.pages)):
        pg_text = extract_text(in_file.pages[pgNo])
        # If current page contains all text of previous page
        if pg_text.startswith(prev_pg_text):
            del_pages.append(pgNo-1) # Delete previous page
        prev_pg_text = pg_text

    # To delete pages, have to write a new PDF excluding those
    for pgNo in range(len(in_file.pages)):
        if pgNo not in del_pages:
            pg = in_file.pages[pgNo]
            writer_1.add_page(pg)
    
    with open(out_fpath, 'wb') as f:
        writer_1.write(f)

    # Part 2; resize pages

    writer_2 = PdfWriter()

    A5_w = PaperSize.A5.height
    A5_h = PaperSize.A5.width

    for page in writer_1.pages:
        # resize page to fit *inside* A5
        h = float(page.mediabox.height)
        w = float(page.mediabox.width)

        if w > h:
            A5_w = PaperSize.A5.height
            A5_h = PaperSize.A5.width
        else:
            A5_w = PaperSize.A3.width
            A5_h = PaperSize.A3.height

        scale_factor = min(A5_h/h, A5_w/w)

        # get borders to center old page into new page
        center_w = A5_w - w * scale_factor
        center_h = A5_h - h * scale_factor

        # apply transform
        transform = Transformation().scale(scale_factor,scale_factor).translate(center_w / 2, center_h / 2)
        page.add_transformation(transform)

        # prepare A5 blank page

        page.cropbox = RectangleObject((0, 0, A5_w, A5_h))
        page_A5 = PageObject.create_blank_page(width = A5_w, height = A5_h)
        page.mediabox = page_A5.mediabox
        page_A5.merge_page(page)

        # add content to page
        writer_2.add_page(page_A5)

    writer_2.write(out_fpath)