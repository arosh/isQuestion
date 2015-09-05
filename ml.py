# coding: utf_8
from __future__ import division, print_function, unicode_literals

import codecs
import glob
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
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelEncoder

import features
import normalize


def best_cv_num(n):
    return int(1 + numpy.log2(n))


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
    corpus = load_corpus()
    D = []
    y = []
    fex = features.IpadicFeature()
    progress = 0
    print('create feature dictionary')
    for q, a in load_corpus():
        D.extend(fex.transform(q))
        a = normalize.normalize_askfm(a, h2z=False)
        y.append(isnot_shitsumon(a))
        progress += 1
        if progress % 100 == 0:
            print(progress)

    progress = 0
    print('create feature vector')
    dv = DictVectorizer()
    dv.fit(dict(zip(xrange(len(d)), d)) for d in D)
    X = []
    for q, a in load_corpus():
        count = None
        for t in fex.transform(q):
            d = dv.transform(dict(zip(xrange(len(t)), t)))
            if count is None:
                count = d
            else:
                count += d
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
    for t in fex.transform(text):
        d = dv.transform(dict(zip(xrange(len(t)), t)))
        if count is None:
            count = d
        else:
            count += d
    C = clf.predict_proba(count)
    return C[0,1]

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

        clf = MultinomialNB()
        params = {
            'alpha': 10 ** numpy.linspace(-10, 0, 1000),
        }
        cv = RandomizedSearchCV(clf, params, scoring='f1', n_iter=30, cv=best_cv_num(X.shape[0]), verbose=1)
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
                print('質問ではない。 ({:.2%})'.format(proba))
            else:
                print('質問である。 ({:.2%})'.format(1-proba))
    except EOFError:
        pass

if __name__ == '__main__':
    sys.stdout=codecs.getwriter('utf_8')(sys.stdout)
    sys.stderr=codecs.getwriter('utf_8')(sys.stderr)
    main()
