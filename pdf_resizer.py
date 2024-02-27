from PyPDF2 import PdfReader, PdfWriter
import re, sys

# Input through Command line arguments
if len(sys.argv)<2:
    print('Also give a PDF filepath on which script will work\n')
    exit(1)
else:
    in_fpath= sys.argv[1]

if len(sys.argv)==3: # To give output file path
	out_fpath = sys.argv[2]
else:   # Replace the same file
	out_fpath = in_fpath

from pypdf import PdfReader, PdfWriter, Transformation, PageObject, PaperSize
from pypdf.generic import RectangleObject

reader = PdfReader(in_fpath)
page = reader.pages[0]
writer = PdfWriter()

A4_w = PaperSize.A5.height
A4_h = PaperSize.A5.width

# resize page to fit *inside* A4
h = float(page.mediabox.height)
w = float(page.mediabox.width)
scale_factor = min(A4_h/h, A4_w/w)

transform = Transformation().scale(scale_factor,scale_factor).translate(17.5, 0)
page.add_transformation(transform)

page.cropbox = RectangleObject((0, 0, A4_w, A4_h))

# merge the pages to fit inside A4

# prepare A4 blank page
page_A4 = PageObject.create_blank_page(width = A4_w, height = A4_h)
page.mediabox = page_A4.mediabox
page_A4.merge_page(page)

writer.add_page(page_A4)
writer.write(out_fpath)