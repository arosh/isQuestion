# coding: utf_8
from __future__ import division, print_function, unicode_literals

from future_builtins import ascii, filter, hex, map, oct, zip

import morph
import normalize


class UnidicFeature(object):

    def __init__(self, dicdir=None):
        if dicdir is None:
            dicdir = '-d /usr/local/Cellar/mecab/0.996/lib/mecab/dic/unidic'
        self.dicdir = dicdir

    def to_pos(self, surface, features):
        return features[0]

    def to_pos1(self, surface, features):
        return features[0] + '-' + features[1]

    def to_base(self, surface, features):
        if len(features) > 6:
            return features[7]
        else:
            return surface

    def transform(self, text):
        text = normalize.normalize_askfm(text, h2z=False)
        fn = {'pos': self.to_pos, 'pos1': self.to_pos1,
              'base': self.to_base}
        for surface, features in morph.parse(text, opt=self.dicdir):
            yield {name: func(surface, features) for name, func in fn.iteritems()}


class IpadicFeature(object):

    def __init__(self, dicdir=None):
        if dicdir is None:
            dicdir = '-d /Users/arosh/opt/mecab-ipadic-neologd'
        self.dicdir = dicdir

    def to_pos(self, surface, features):
        return features[0]

    def to_pos1(self, surface, features):
        return features[0] + '-' + features[1]

    def to_pos2(self, surface, features):
        return features[0] + '-' + features[1] + '-' + features[2]

    def to_cform(self, surface, features):
        return features[5]

    def to_base(self, surface, features):
        if features[6] == '*':
            return surface
        else:
            return features[6]

    def transform(self, text):
        text = normalize.normalize_askfm(text, h2z=False)
        # fn = {'pos': self.to_pos, 'pos1': self.to_pos1, 'pos2': self.to_pos2,
        #       'cform': self.to_cform, 'base': self.to_base}
        for surface, features in morph.parse(text, opt=self.dicdir):
            # yield {name: func(surface, features) for name, func in fn.iteritems()}
            yield {'base': self.to_base(surface, features)}
    
    def segmentation(self, text):
        for surface, features in morph.parse(text, opt=self.dicdir):
            yield self.to_base(surface, features)
