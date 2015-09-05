# coding: utf_8
from __future__ import division, print_function, unicode_literals

from future_builtins import ascii, filter, hex, map, oct, zip

import MeCab


def parse(unicode_string, encoding='utf_8', opt=''):
    assert isinstance(unicode_string, unicode)
    assert isinstance(opt, unicode)
    byte_string = unicode_string.encode(encoding)
    tagger = MeCab.Tagger(opt.encode(encoding))
    node = tagger.parseToNode(byte_string)
    while node:
        surface = node.surface.decode(encoding)
        if len(surface) > 0:
            features = node.feature.decode(encoding).split(',')
            yield (surface, features)
        node = node.next
