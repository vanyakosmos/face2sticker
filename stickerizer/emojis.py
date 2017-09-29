import random

from PIL import Image


def associate_emoji(face_image: Image):
    pick = list('😀😡👍👎😱')
    emoji = random.choice(pick)  # fixme
    return emoji


def get_emotion():
    pass


def map_emoji():
    pass
