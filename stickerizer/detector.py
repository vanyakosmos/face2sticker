from io import BytesIO

import face_recognition
from PIL import Image


def face_locations(image_bytes: BytesIO):
    """
    Find faces locations, cut faces and yield as `PIL.Image`
    :param image_bytes:
    :return:
    """
    image = face_recognition.load_image_file(image_bytes)
    locations = face_recognition.face_locations(image)  # model="cnn"

    for top, right, bottom, left in locations:
        cropped_face = image[top:bottom, left:right]
        yield Image.fromarray(cropped_face)


def face_landmarks(image_bytes: BytesIO) -> (Image, list):
    """
    Find landmarks and return them with PIL.Image
    :param image_bytes:
    :return:
    """
    image = face_recognition.load_image_file(image_bytes)
    landmarks = face_recognition.face_landmarks(image)

    im = Image.fromarray(image)
    return im, landmarks
