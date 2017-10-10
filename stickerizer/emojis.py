import numpy as np

from emotion_clf.emotion import load_clf, vectorize, emotions


clf = load_clf('emotion_clf/clf2.pkl')


def associate_emojis(face_landmarks):
    emotions_probs = predict_probabilities(face_landmarks)
    emoji = map_emoji(emotions_probs)
    return emoji


def predict_probabilities(face_landmarks: dict):
    landmarks = []
    for points in face_landmarks.values():
        landmarks.extend(points)

    vector = vectorize(landmarks)

    data = np.array([vector])
    res = clf.predict_proba(data)[0]
    probs = {}
    for i, e in enumerate(emotions):
        probs[e] = res[i]
    return probs


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
