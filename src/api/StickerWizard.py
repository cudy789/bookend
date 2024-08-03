#!/usr/bin/python3

from .Barcodes import Barcodes

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from PIL import Image

class StickerWizard:
    def __init__(self):
        pass
    def AveryTemplate5160(self, isbns: list, output_filename: str) -> None:
        print(f"isbn input list: {isbns}")
        images = [Barcodes().gen_image(isbn) for isbn in isbns if len(isbn) > 0]

        # Avery 5160 labels setup
        labels_per_row = 3
        labels_per_column = 10
        label_width = 2.625 * inch  # 2-5/8 inches
        label_height = 1.0 * inch  # 1 inch
        page_margin_left = 0.1875 * inch  # 3/16 inch margin on left side
        page_margin_right = 0.1875 * inch  # 3/16 inch margin on right side
        page_margin_top = 0.5 * inch  # 1/2 inch margin on top side
        page_margin_bottom = 0.5 * inch  # 1/2 inch margin on bottom side
        label_spacing_x = 0.125 * inch  # 1/8 inch between labels horizontally
        label_spacing_y = 0.0  # No space between labels vertically

        c = canvas.Canvas(output_filename, pagesize=letter)
        page_width, page_height = letter

        x_offset = page_margin_left
        y_offset = page_height - page_margin_top - label_height  # start from the top of the page

        for i, image in enumerate(images):
            if i > 0 and i % (labels_per_row * labels_per_column) == 0:
                c.showPage()
                y_offset = page_height - page_margin_top - label_height
                x_offset = page_margin_left

            row = (i // labels_per_row) % labels_per_column
            col = i % labels_per_row

            x = x_offset + col * (label_width + label_spacing_x)
            y = y_offset - row * (label_height + label_spacing_y)

            image.seek(0)  # Reset the BytesIO object position to the start
            img = Image.open(image)
            aspect_ratio = img.width / img.height

            if aspect_ratio > (label_width / label_height):
                # Scale based on width
                new_width = label_width
                new_height = label_width / aspect_ratio
            else:
                # Scale based on height
                new_height = label_height
                new_width = label_height * aspect_ratio

            img_path = f'api/sticker_wizard_imgs/image_{i}.png'
            img.save(img_path, format='PNG')
            c.drawImage(img_path, x + (label_width - new_width) / 2, y + (label_height - new_height) / 2,
                        width=new_width, height=new_height)

        c.save()

if __name__ == '__main__':
    s = StickerWizard()
    s.AveryTemplate5160([
        "12345", "12345", "12345", "12345", "12345",
        "12345", "12345", "12345", "12345", "12345",
        "12345", "12345", "12345", "12345", "12345",
        "12345", "12345", "12345", "12345", "12345",
        "12345", "12345", "12345", "12345", "12345",
        "12345", "12345", "12345", "12345", "12345",
        "12345", "12345", "12345", "12345", "12345",
    ], "test_avery.pdf")

