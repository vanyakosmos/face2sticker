import io
from os.path import join
from typing import Tuple

from . import features, emojis, detector


def make_stickers(image_bytes: io.BytesIO) -> Tuple[io.BytesIO, str]:
    """
    :param image_bytes: photo bytes array that should be converted to sticker
    :return: tuple of .png image buffer and associated emoji
    """

    for face_image in detector.face_locations(image_bytes):
        face_image = face_image.convert('L')
        emoji = emojis.associate_emoji(face_image)
        buff = io.BytesIO()
        face_image.save(buff, format='PNG')
        buff.seek(0)
        yield buff, emoji


def main():
    img_name = 'girl1'
    img_path = join('images', f'{img_name}.jpg')
    out_path = join('output', img_name)

    with open(img_path, 'rb') as image_file:
        image_bytes = io.BytesIO(image_file.read())

        # features.show_landmarks(image_bytes)

        # features.show_circle_crop(image_bytes)
        index = 0
        for image in features.crop_circle(image_bytes):
            index += 1
            image.save(out_path + '_' + str(index) + '.png')
        # for sticker, emoji in make_stickers(bytes_arr):
        #     features.save_image(sticker, out_path, ext='.png')
        #     sticker.close()

        image_bytes.close()


if __name__ == '__main__':
    main()
