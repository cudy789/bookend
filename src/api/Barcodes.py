#!/usr/bin/python3

from barcode import ISBN13, Code39
from barcode.writer import ImageWriter
from io import BytesIO

class Barcodes():
    def __init__(self):
        pass
    def gen_image(self, number):
        print(f"generating barcode for number {number}")
        rv = BytesIO()

        if len(number) == 13:
            try:
                ISBN13(str(number), writer=ImageWriter()).write(rv)
            except Exception:
                Code39(str(number), writer=ImageWriter(), add_checksum=False).write(rv)
        elif len(number) == 10:
            try:
                ISBN13(str(number), writer=ImageWriter()).write(rv)
            except Exception:
                Code39(str(number), writer=ImageWriter(), add_checksum=False).write(rv)
        else:
            Code39(str(number), writer=ImageWriter(), add_checksum=False).write(rv)

        return rv
