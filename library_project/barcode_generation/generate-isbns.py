#!/usr/bin/python3

"""
This script will generate ISBN barcodes from the raw numbers.
"""

from barcode import EAN13, Code39
from barcode.writer import ImageWriter
import sys


m_barcode = sys.argv[1]

if len(m_barcode) != 13:
    print("Error: ISBN must be exactly 13 digits")
    exit(1)

# Or to an actual file:
with open(str(m_barcode) + ".png", "wb") as f:
    barcode_obj = Code39(str(m_barcode), writer=ImageWriter(), add_checksum=False)
    barcode_obj.write(f)
    print(barcode_obj.get_fullcode())