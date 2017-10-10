from collections import Counter
from io import BytesIO

from PIL import Image, ImageDraw, ImageOps

from . import detector


OUTLINE_RING = 0
OUTLINE_MOON = 1


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
    size[i] = int(512)
    other_index = abs(i - 1)
    size[other_index] = int(dif * size[other_index])
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


def change_bounds(bounds, x):
    return [e + x for e in bounds[:2]] + [e - x for e in bounds[2:]]


def arr_sub(arr, sub):
    return [e - sub for e in arr]


def add_outline(image: Image, t=10, style=OUTLINE_RING):
    """
    :param style:
    :param image:
    :param t: thickness in px
    :return:
    """
    size = (512, 512)
    outline = Image.new('L', size, color=0)

    # moon-like style
    draw = ImageDraw.Draw(outline)
    bounds = (0, 0) + size
    if style == OUTLINE_MOON:
        # moon-like style
        draw.ellipse(arr_sub(bounds, -1), fill=255)
        draw.ellipse(arr_sub(bounds, t), fill=0)
    else:
        # ring
        draw.ellipse(change_bounds(bounds, -1), fill=255)
        draw.ellipse(change_bounds(bounds, t), fill=0)

    outline = ImageOps.fit(outline, image.size, centering=(0.5, 0.5))
    image.paste(outline, mask=outline)
    return image


def crop_circle(image, face_landmarks, scale=1.03, outline=False, outline_style=OUTLINE_RING):
    size = (512, 512)
    mask = Image.new('L', size, 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0) + size, fill=255)

    chin_points = face_landmarks['chin']
    x1, min_y = min(chin_points, key=lambda p: p[1])
    x2, max_y = max(chin_points, key=lambda p: p[1])
    center = (x2, min_y)
    radius = (max_y - min_y) * scale

    bounds = [
        center[0] - radius,  # right
        center[1] - radius,  # bot
        center[0] + radius,  # left
        center[1] + radius,  # top
    ]

    cropped = image.crop(bounds)
    mask = ImageOps.fit(mask, cropped.size, centering=(0.5, 0.5))
    cropped.putalpha(mask)
    cropped = sticker_resize(cropped)

    if outline:
        cropped = add_outline(cropped, style=outline_style)

    buff = BytesIO()
    cropped.save(buff, format='PNG')
    buff.seek(0)
    return buff
