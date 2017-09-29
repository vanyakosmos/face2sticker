from io import BytesIO
from os.path import join
from collections import Counter

import face_recognition
from PIL import Image, ImageOps, ImageDraw

from . import detector


def save_image(image: Image, folder_path: str, sup=Counter(), ext='.png'):
    sup[folder_path] += 1
    index = sup[folder_path]
    path = f'{folder_path}_{index}{ext}'
    with open(path, 'wb') as out:
        out.write(image.tobytes())


def calc_size(size):
    size = list(size)
    i, x = max(enumerate(size), key=lambda e: e[1])
    dif = 512 / x
    size[i] = 512
    other_index = abs(i - 1)
    size[other_index] = dif * size[other_index]
    return size


def sticker_resize(image: Image) -> Image:
    """
    Sticker dimensions must not exceed 512px, and either width or height must be exactly 512px
    """
    size = calc_size(image.size)
    return image.resize(size)


def show_landmarks(image_bytes: BytesIO):
    im, landmarks = detector.face_landmarks(image_bytes)

    draw = ImageDraw.Draw(im)
    for face in landmarks:
        for part, points in face.items():
            draw.polygon(points, outline='cyan')
    del draw
    im.show()


def add_circle_outline(image: Image):
    pass


def crop_circle(image_bytes: BytesIO, add_outline=False):
    image, landmarks = detector.face_landmarks(image_bytes)

    size = (512, 512)
    mask = Image.new('L', size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0) + size, fill=255)

    for face in landmarks:
        chin_points = face['chin']
        x1, min_y = min(chin_points, key=lambda p: p[1])
        x2, max_y = max(chin_points, key=lambda p: p[1])
        center = (x2, min_y)
        radius = (max_y - min_y) * 1.02

        bounds = [
            center[0] - radius,  # right
            center[1] - radius,  # bot
            center[0] + radius,  # left
            center[1] + radius,  # top
        ]

        # new image cropped with bounds
        cropped = image.crop(bounds)
        output = ImageOps.fit(cropped, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)
        yield sticker_resize(output)


def show_circle_crop(image_bytes: BytesIO):
    image, landmarks = detector.face_landmarks(image_bytes)

    mask = Image.new('L', image.size, 0)
    mask_draw = ImageDraw.Draw(mask)

    for face in landmarks:
        chin_points = face['chin']
        x1, min_y = min(chin_points, key=lambda p: p[1])
        x2, max_y = max(chin_points, key=lambda p: p[1])
        center = (x2, min_y)
        radius = (max_y - min_y) * 1.02

        mask_draw.ellipse([
            center[0] - radius,  # right
            center[1] - radius,  # bot
            center[0] + radius,  # left
            center[1] + radius,  # top
        ], fill=255)
    image.putalpha(mask)
    image.show()
