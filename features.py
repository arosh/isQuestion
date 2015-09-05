# coding: utf_8
from __future__ import division, print_function, unicode_literals

from future_builtins import ascii, filter, hex, map, oct, zip
import normalize
import morph


class UnidicFeature(object):

    def __init__(self, dicdir=None):
        if dicdir is None:
            dicdir = '-d /usr/local/Cellar/mecab/0.996/lib/mecab/dic/unidic'
        self.dicdir = dicdir

    def to_pos(self, surface, features):
        return features[0], features[0] + '-' + features[1]

    def to_base(self, surface, features):
        if len(features) > 6:
            return features[7]
        else:
            return surface

    def transform(self, text):
        text = normalize.normalize_askfm(text, h2z=True)
        for surface, features in morph.parse(text, opt=self.dicdir):
            pos = self.to_pos(surface, features)
            base = self.to_base(surface, features)
            yield [pos[0], pos[1], base]


class IpadicFeature(object):

    def __init__(self, dicdir=None):
        if dicdir is None:
            dicdir = '-d /Users/arosh/opt/mecab-ipadic-neologd'
        self.dicdir = dicdir

    def to_pos(self, surface, features):
        return features[0], features[0] + '-' + features[1]

    def to_base(self, surface, features):
        if features[6] == '*':
            return surface
        else:
            return features[6]

    def transform(self, text):
        text = normalize.normalize_askfm(text, h2z=False)
        for surface, features in morph.parse(text, opt=self.dicdir):
            pos = self.to_pos(surface, features)
            base = self.to_base(surface, features)
            yield [pos[0], pos[1], base]
