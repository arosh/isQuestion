# coding: utf_8
from __future__ import division, print_function, unicode_literals

import codecs
import glob
import itertools
import json
import operator
import os
import sys
from future_builtins import ascii, filter, hex, map, oct, zip

import numpy
import scipy.sparse
import sklearn.utils
from sklearn.externals import joblib
from sklearn.grid_search import RandomizedSearchCV
from sklearn.naive_bayes import MultinomialNB
from sklearn.preprocessing import LabelBinarizer

import features
import normalize


def best_cv_num(n):
    return int(1 + numpy.log2(n))


def load_all_texts():
    '''
    Returns
    -------
    {text}
    '''
    ret = []
    for fname in glob.iglob('corpus/*.json'):
        with open(fname) as f:
            data = json.load(f)
        for it in data:
            ret.append(it['question'])
    return set(ret)


def load_supervised_texts():
    '''
    Returns
    -------
    {text -> label}
    '''
    filename = 'supervised.json'
    if not os.path.exists(filename):
        return {}
    with open(filename) as f:
        data = json.load(f)
    return data


def save_supervised_texts(data):
    '''
    Parameters
    ----------
    {text -> label}
    '''
    filename = 'supervised.json'
    with open(filename, 'w') as f:
        json.dump(data, f)


def learn(X, y):
    '''
    Parameters
    ----------
    X : input matrix
    y : output label

    Returns
    -------
    classifier
    '''
    n_samples = X.shape[0]
    clf = MultinomialNB()
    params = {
        'alpha': numpy.linspace(0, 1, 1000)
    }
    cv = RandomizedSearchCV(
        clf, params, scoring='f1', n_iter=30, cv=best_cv_num(n_samples), verbose=1)
    cv.fit(X, y)
    print('f1 =', cv.best_score_)
    print(cv.best_params_)
    return cv.best_estimator_

cache = {}


def to_base(text):
    global cache
    if text in cache:
        return cache[text]
    fex = features.IpadicFeature()
    cache[text] = list(fex.segmentation(text))
    return cache[text]


def vectorize_with_learn(texts):
    words = []
    progress = 0
    for text in texts:
        # LabelBinarizer.transformがiteratorを受け付けないのでlist化
        w = to_base(text)
        words.append(w)
        progress += 1
        if progress % 1000 == 0:
            print(progress)
    lb = LabelBinarizer(sparse_output=True)
    lb.fit(list(itertools.chain(*words)))
    X = []
    progress = 0
    for w in words:
        cat = lb.transform(w)
        count = cat.sum(axis=0)
        count = scipy.sparse.csr_matrix(count)
        X.append(count)
        progress += 1
        if progress % 1000 == 0:
            print(progress)
    X = scipy.sparse.vstack(X)
    return X, lb


def vectorize(texts, lb):
    X = []
    progress = 0
    for text in texts:
        w = to_base(text)
        cat = lb.transform(w)
        count = cat.sum(axis=0)
        count = scipy.sparse.csr_matrix(count)
        X.append(count)
        progress += 1
        if progress % 1000 == 0:
            print(progress)
    X = scipy.sparse.vstack(X)
    return X


def candidate(texts, clf, lb):
    # 確率の差が小さい上位10個を返す
    X = vectorize(texts, lb)
    C = clf.predict_proba(X)
    diff = numpy.abs(C[:, 0] - C[:, 1])
    l = list(zip(diff, texts))
    l.sort(key=operator.itemgetter(0))
    return list(map(operator.itemgetter(1), l[:10]))


def test():
    texts = ['動的計画法書ける？', 'プロプロプロ']
    clf = MultinomialNB()
    X, lb = vectorize_with_learn(texts)
    clf.fit(X, [False, True])
    print('/'.join(candidate(texts, clf, lb)))


def main():
    texts = load_all_texts()
    supervised = load_supervised_texts()
    while True:
        supervised_texts = supervised.keys()
        y = supervised.values()
        texts -= set(supervised_texts)
        X, lb = vectorize_with_learn(supervised_texts)
        clf = learn(X, y)
        cand = candidate(texts, clf, lb)
        for t in cand:
            n = normalize.normalize_askfm(t, h2z=False)
            print(n)
            while True:
                i = raw_input('クソリプ？(y/n) ')
                if i == 'y' or i == 'n':
                    break
            if i == 'y':
                supervised[t] = True
            else:
                supervised[t] = False
        save_supervised_texts(supervised)

if __name__ == '__main__':
    sys.stdout = codecs.getwriter('utf_8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf_8')(sys.stderr)
    main()
