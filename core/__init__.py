from os.path import join

import face_recognition
from PIL import Image, ImageDraw


def show_face(image, top, right, bottom, left):
    face_image = image[top:bottom, left:right]
    pil_image = Image.fromarray(face_image)
    pil_image.show()


def main():
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


if __name__ == '__main__':
    main()
