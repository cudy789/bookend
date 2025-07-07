#!/usr/bin/python3


from PIL import Image
import io

def image_to_bmp(image_io):

    # Load and process the image
    image = Image.open(image_io).resize((480, 800), Image.LANCZOS).convert('1').rotate(90, expand=True)

    # Save BMP to memory
    bmp_io = io.BytesIO()

    # Flip vertically to match BMP bottom-up row layout
    image = image.transpose(Image.FLIP_TOP_BOTTOM)

    image = image.transpose(Image.FLIP_TOP_BOTTOM)


    image.save(bmp_io, format='BMP')
    bmp_io.seek(0)

    return bmp_io