from os.path import join
from typing import Tuple

import face_recognition
import io
from PIL import Image, ImageDraw, ImageFilter


def show_face(image, top, right, bottom, left):
    face_image = image[top:bottom, left:right]
    pil_image = Image.fromarray(face_image)
    pil_image.show()


def location():
    input_folder = 'images'
    output_folder = 'output'
    img_path = join(input_folder, 'girl1.jpg')
    out_path = join(output_folder, 'girl1.jpg')

    image = face_recognition.load_image_file(img_path)
    face_locations = face_recognition.face_locations(image)  # model="cnn"
    # face_landmarks_list = face_recognition.face_landmarks(image)
    print(face_locations)
    # pprint(face_landmarks_list)

    pil_im = Image.fromarray(image)
    draw = ImageDraw.Draw(pil_im, 'RGBA')

    # top, right, bottom, left
    for y1, x1, y2, x2 in face_locations:
        draw.rectangle([x1, y1, x2, y2], outline='#00db2b')
        # show_face(image, y1, x1, y2, x2)
    del draw

    # write to stdout
    pil_im.save(out_path)


def make_sticker(bytes_arr: io.BytesIO) -> Tuple[io.BytesIO, str]:
    """
    :param bytes_arr: photo bytes array that should be converted to sticker
    :return: tuple of .png image buffer and associated emoji
    """
    image = Image.open(bytes_arr)
    image = image.convert('L').convert('RGBA')
    image = image.resize((512, 512))

    draw = ImageDraw.Draw(image)
    draw.rectangle((2, 2, image.size[0]-2, image.size[1]-2), outline='#ea233a')

    buff = io.BytesIO()
    image.save(buff, format='PNG')
    buff.seek(0)
    return buff, '🌚'


def main():
    input_folder = 'images'
    output_folder = 'output'
    img_path = join(input_folder, 'girl1.jpg')
    out_path = join(output_folder, 'girl1.png')

    with open(img_path, 'rb') as inp, open(out_path, 'wb') as out:
        bytes_arr = io.BytesIO(inp.read())
        sticker, emoji = make_sticker(bytes_arr)
        out.write(sticker.read())
        sticker.close()
        bytes_arr.close()


if __name__ == '__main__':
    main()
