import cv2
import numpy as np
from io import BytesIO

from emotion_clf.emotion import load_clf, get_landmarks, detector, emotions, clahe


def associate_emoji(image_bytes: BytesIO):
    emotions_prob = get_emotion(image_bytes)
    emoji = map_emoji(emotions_prob)
    return emoji


def vectorize(image_bytes: BytesIO):
    image = np.frombuffer(image_bytes.getbuffer(), dtype=np.uint8)
    image = cv2.imdecode(image, cv2.IMREAD_UNCHANGED)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe_image = clahe.apply(gray)

    detections = detector(clahe_image, 1)  # Detect the faces in the image
    vectors = []
    for face_rect in detections:
        landmarks = get_landmarks(image, face_rect)
        vectors.append(landmarks)
    return vectors


def predict_probabilities(clf, image_bytes: BytesIO):
    vectors = vectorize(image_bytes)

    data = np.array(vectors)
    res = clf.predict_proba(data)[0]
    probs = {}
    for i, e in enumerate(emotions):
        probs[e] = res[i]
    return probs


def get_emotion(image_bytes: BytesIO):
    clf = load_clf('emotion_clf/clf.pkl')
    return predict_probabilities(clf, image_bytes)


def map_emoji(emotions_prob: dict):
    emojis = {
        '😡': {
            'anger': 10,
        },
        '😒': {
            'contempt': 10,
        },
        '😣': {
            'disgust': 10,
        },
        '😱': {
            'fear': 10,
        },
        '😀': {
            'happiness': 10,
        },
        '😢': {
            'sadness': 10,
        },
        '😮': {
            'surprise': 10,
        },
    }
    max_s = None
    result = '🌚'
    for emoji, ems in emojis.items():
        s = sum([ems.get(e, 1) * emotions_prob[e] for e in emotions])
        if not max_s or s > max_s:
            max_s = s
            result = emoji
    return result
