# coding: utf_8
from __future__ import division, print_function, unicode_literals

import codecs
import glob
import itertools
import json
import os
import sys
from future_builtins import ascii, filter, hex, map, oct, zip

import numpy
import scipy.sparse
import sklearn.utils
from sklearn.externals import joblib
from sklearn.feature_extraction import DictVectorizer
from sklearn.grid_search import RandomizedSearchCV
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVC

import features
import normalize


def best_cv_num(n):
    return int(1 + numpy.log2(n))


def best_n_iter(n):
    return numpy.ceil(10 ** 6 / n)


def isnot_shitsumon(answer):
    if answer == '質問ではない。':
        return True
    if answer == '質問ではない':
        return True
    if answer == 'これは質問ではない。':
        return True
    # if answer == '質問の意味がわからない。': return False
    return False


def load_corpus():
    url2qa = {}
    for fname in glob.iglob('corpus/*.json'):
        with open(fname) as f:
            data = json.load(f)
        for it in data:
            url2qa[it['url']] = (it['question'], it['answer'])
    return url2qa.values()


def generate_matrix():
    D = []
    y = []
    fex = features.IpadicFeature()
    progress = 0
    print('create feature dictionary')
    for q, a in load_corpus():
        D.append(list(fex.transform(q)))
        a = normalize.normalize_askfm(a, h2z=False)
        y.append(isnot_shitsumon(a))
        progress += 1
        if progress % 100 == 0:
            print(progress)

    dv = DictVectorizer()
    dv.fit(itertools.chain(*D))

    progress = 0
    print('create feature vector')
    X = []
    for ds in D:
        count = None
        for d in ds:
            v = dv.transform(d)
            if count is None:
                count = v
            else:
                count += v
        X.append(count)
        progress += 1
        if progress % 100 == 0:
            print(progress)
    X = scipy.sparse.vstack(X)
    y = numpy.array(y)
    return X, y, dv


def predict(text, dv, clf):
    fex = features.IpadicFeature()
    count = None
    for d in fex.transform(text):
        v = dv.transform(d)
        if count is None:
            count = v
        else:
            count += v
    C = clf.predict_proba(count)
    return C[0, 1]


def naive_bayes(n_samples):
    clf = MultinomialNB()
    params = {
        'alpha': numpy.linspace(0, 1, 1000)
    }
    return RandomizedSearchCV(clf, params, scoring='f1', n_iter=30, cv=best_cv_num(n_samples), verbose=1)


def sgd(n_samples):
    clf = SGDClassifier(n_iter=best_n_iter(n_samples))
    params = {
        'alpha': 10 ** numpy.linspace(-7, -1, 1000),
    }
    return RandomizedSearchCV(clf, params, scoring='f1', n_iter=30, cv=best_cv_num(n_samples), verbose=3)


def kernel_svc(n_samples):
    clf = SVC()
    params = {
        'C': 2 ** numpy.linspace(-5, 15),
        'gamma': 2 ** numpy.linspace(-15, 3),
        'class_weight': [None, 'auto'],
    }
    return RandomizedSearchCV(clf, params, scoring='f1', n_iter=30, cv=best_cv_num(n_samples), verbose=3)


def main():
    if not os.path.exists('X.pkl') or not os.path.exists('y.pkl') or not os.path.exists('dv.pkl'):
        X, y, dv = generate_matrix()
        joblib.dump(X, 'X.pkl')
        joblib.dump(y, 'y.pkl')
        joblib.dump(dv, 'dv.pkl')
    else:
        X = joblib.load('X.pkl')
        y = joblib.load('y.pkl')
        dv = joblib.load('dv.pkl')

    if not os.path.exists('clf.pkl'):
        X, y = sklearn.utils.shuffle(X, y)
        n_samples = X.shape[0]
        cv = naive_bayes(n_samples)
        # X = StandardScaler(with_mean=False).fit_transform(X)
        # cv = sgd(n_samples)
        # cv = kernel_svc(n_samples)
        cv.fit(X, y)
        print('f1 =', cv.best_score_)
        print(cv.best_params_)
        joblib.dump(cv.best_estimator_, 'clf.pkl')
        clf = cv.best_estimator_
    else:
        clf = joblib.load('clf.pkl')

    try:
        while True:
            line = raw_input('> ')
            text = line.strip().decode('utf_8')
            proba = predict(text, dv, clf)
            if proba >= 0.5:
                print('質問ではない。({:.2%})'.format(proba))
            else:
                print('質問である。({:.2%})'.format(1 - proba))
    except EOFError:
        pass

if __name__ == '__main__':
    sys.stdout = codecs.getwriter('utf_8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf_8')(sys.stderr)
    main()
