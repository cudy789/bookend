#!/usr/bin/python3


from PIL import Image
import io

def image_to_bmp(image_io):

    # Load and process the image
    image = Image.open(image_io).resize((480, 800), Image.LANCZOS).convert('1')

    # Save BMP to memory
    bmp_io = io.BytesIO()
    image.save(bmp_io, format='BMP')
    bmp_io.seek(0)

    return bmp_io