import io
from os.path import join
from typing import Tuple

from PIL import Image

from . import cropper, emojis, detector
from . import detector


def make_stickers(image_bytes: io.BytesIO) -> Tuple[io.BytesIO, str]:
    """
    :param image_bytes: photo bytes array that should be converted to sticker
    :return: tuple of .png image buffer and associated emoji
    """
    image, landmarks = detector.face_landmarks(image_bytes)
    for face_landmarks in landmarks:
        face_buffer = cropper.crop_circle(image, face_landmarks, outline=True)
        ems = emojis.associate_emojis(face_landmarks)
        yield face_buffer, ems


def main():
    img_name = 'dude5'
    img_path = join('images', f'{img_name}.png')
    out_path = join('output', img_name)

    with open(img_path, 'rb') as image_file:
        image_bytes = io.BytesIO(image_file.read())
        for buff, es in make_stickers(image_bytes):
            im = Image.open(buff)
            im.show()
            print(es)
        image_bytes.close()


if __name__ == '__main__':
    main()
