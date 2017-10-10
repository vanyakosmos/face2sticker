import glob
import random

import numpy as np
import math
from sklearn.svm import SVC
from sklearn.externals import joblib

from stickerizer.detector import face_landmarks


emotions = ["anger", "contempt", "disgust", "fear", "happiness", "sadness", "surprise"]


def get_files(emotion, train=0.8):  # Define function to get file list, randomly shuffle it and split 80/20
    files = glob.glob(f'./dataset/{emotion}/*')
    random.shuffle(files)
    limit = int(len(files) * train)
    training = files[:limit]
    prediction = files[limit:]
    return training, prediction


def get_random_files(k=10):
    files = glob.glob(f'./dataset/*/*')
    return random.choices(files, k=k)


def make_sets(train=0.8):
    training_data = []
    training_labels = []
    prediction_data = []
    prediction_labels = []
    for index, emotion in enumerate(emotions):
        print(f'Collecting data for "{emotion}"...')
        training, prediction = get_files(emotion, train=train)

        # Append data to training and prediction list, and generate labels 0-7
        for image_path in training:
            populate(image_path, training_data, training_labels, index)

        for image_path in prediction:
            populate(image_path, prediction_data, prediction_labels, index)

    return training_data, training_labels, prediction_data, prediction_labels


def populate(image_path, vectors, labels, index):

    with open(image_path) as image:
        _, landmarks = face_landmarks(image.buffer)
        for face_marks in landmarks:
            marks = []
            for points in face_marks.values():
                marks.extend(points)
            vector = vectorize(marks)
            vectors.append(vector)
            labels.append(index)


def vectorize(landmarks):
    xs = [e[0] for e in landmarks]
    ys = [e[1] for e in landmarks]

    xmean = np.mean(xs)
    ymean = np.mean(ys)
    meannp = np.asarray((ymean, xmean))

    xs_central = [(x - xmean) for x in xs]
    ys_central = [(y - ymean) for y in ys]

    landmarks_vectorised = []
    for cx, cy, x, y in zip(xs_central, ys_central, xs, ys):
        landmarks_vectorised.append(x)
        landmarks_vectorised.append(y)
        coornp = np.asarray((y, x))
        dist = np.linalg.norm(coornp - meannp)
        landmarks_vectorised.append(dist)
        landmarks_vectorised.append(int(math.atan((cy - ymean) / (cx - xmean)) * 360 / math.pi))
    return landmarks_vectorised


def learn_and_save(clf, clf_file_name='clf'):
    accuracies = []
    experiments = 1
    for i in range(experiments):
        print('\n' + '- ' * 50 + '\n')
        print(f"Experiment #{i+1}...")
        training_data, training_labels, prediction_data, prediction_labels = make_sets(train=0.9)

        npar_train = np.array(training_data)

        print("Training linear SVM...")  # train SVM
        clf.fit(npar_train, training_labels)

        print("Getting accuracy...")  # Use score() function to get accuracy
        npar_pred = np.array(prediction_data)
        pred_lin = clf.score(npar_pred, prediction_labels)
        print("Accuracy:", pred_lin)
        accuracies.append(pred_lin)  # Store accuracy in a list

    mean = np.mean(accuracies)
    print(f"Mean value for linear SVM experiences: {mean}")

    joblib.dump(clf, clf_file_name + '.pkl')
    print('saved')


def load_clf(clf_file_name='clf.pkl'):
    return joblib.load(clf_file_name)


def predict_probability(clf):
    data = []
    num = 1
    # files = get_random_files(k=num)
    files = ['neut.jpg']
    for image_path in files:
        populate(image_path, data, [], 0)

    data = np.array(data)
    res = clf.predict_proba(data)
    for j in range(num):
        file = files[j]
        print(f'Image #{j+1}: {file}')
        for i, e in enumerate(emotions):
            pred = res[j, i] * 100
            print(f'{e:15s}: {pred:2.2f}%')


def main():
    clf = SVC(kernel='linear', probability=True, tol=1e-3)
    learn_and_save(clf, clf_file_name='clf2')


if __name__ == '__main__':
    main()
