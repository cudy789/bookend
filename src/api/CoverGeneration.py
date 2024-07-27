#!/usr/bin/python3

import cv2
import numpy as np
from io import BytesIO
from random import choice

background_color_list = [
    "924F5E", # china rose
    "907F9F", # mountbatten pink
    "17301C", # dark green
]

text_color_list = [
    "F4B393", # peach
    "90E0EF", # non photo blue
    "D0F4DE", # nyanza
]

def hex2rgb(hex):
    rgb = tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))
    print(rgb)
    return rgb[::-1]

def background():
    img = np.zeros((192, 128, 3), dtype=np.uint8)
    color = choice(background_color_list)
    img[:, :] = hex2rgb(color)
    return img, color

def cover_initials(initials: list): # only 2 initials will fit
    img, b_color = background()
    for i in range(min(len(initials), 2)):
        t_color = choice(text_color_list)
        cv2.putText(img, initials[i].upper(), (10, i*80 + 80), cv2.FONT_HERSHEY_SIMPLEX, 2.5, hex2rgb(t_color), 4, cv2.LINE_AA)
    return img

def gen_cover(initials: list):
    img = cover_initials(initials)
    is_success, buffer = cv2.imencode(".png", img)
    io_buf = BytesIO(buffer)
    return io_buf


if __name__ == "__main__":

    cv2.imshow("img", cover_initials(['c', 'k']))
    cv2.waitKey(0)

    # closing all open windows
    cv2.destroyAllWindows()
    print("done")