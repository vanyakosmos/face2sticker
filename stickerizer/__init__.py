import io
from os.path import join
from typing import Tuple

from . import features, emojis, detector


def make_stickers(image_bytes: io.BytesIO) -> Tuple[io.BytesIO, str]:
    """
    :param image_bytes: photo bytes array that should be converted to sticker
    :return: tuple of .png image buffer and associated emoji
    """

    for image in features.crop_circle(image_bytes, scale=1.04, outline=True, outline_style=features.OUTLINE_RING):
        buff = io.BytesIO()
        image.save(buff, format='PNG')
        buff.seek(0)
        emoji = emojis.associate_emoji(image)
        yield buff, emoji


def main():
    img_name = 'girl1'
    img_path = join('images', f'{img_name}.jpg')
    out_path = join('output', img_name)

    with open(img_path, 'rb') as image_file:
        image_bytes = io.BytesIO(image_file.read())

        # features.show_landmarks(image_bytes)
        # features.show_circle_crop(image_bytes)

        image_bytes.close()


if __name__ == '__main__':
    main()
