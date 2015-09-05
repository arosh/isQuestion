# coding: utf_8
from __future__ import division, print_function, unicode_literals

import fileinput
import re
import unicodedata
from future_builtins import ascii, filter, hex, map, oct, zip

import jctconv


# ref: https://github.com/neologd/mecab-ipadic-neologd/wiki/Regexp.ja
class NeologdNormalizer(object):

    @staticmethod
    def unicode_normalize(cls, s):
        pt = re.compile('([{}]+)'.format(cls))

        def norm(c):
            return unicodedata.normalize('NFKC', c) if pt.match(c) else c

        s = ''.join(norm(x) for x in re.split(pt, s))
        return s

    @staticmethod
    def remove_extra_spaces(s):
        s = re.sub('[ 　]+', ' ', s)
        blocks = ''.join(('\u4E00-\u9FFF',  # CJK UNIFIED IDEOGRAPHS
                          '\u3040-\u309F',  # HIRAGANA
                          '\u30A0-\u30FF',  # KATAKANA
                          '\u3000-\u303F',  # CJK SYMBOLS AND PUNCTUATION
                          '\uFF00-\uFFEF'   # HALFWIDTH AND FULLWIDTH FORMS
                          ))
        basic_latin = '\u0000-\u007F'

        def remove_space_between(cls1, cls2, s):
            p = re.compile('([{}]) ([{}])'.format(cls1, cls2))
            while p.search(s):
                s = p.sub(r'\1\2', s)
            return s

        s = remove_space_between(blocks, blocks, s)
        s = remove_space_between(blocks, basic_latin, s)
        s = remove_space_between(basic_latin, blocks, s)
        return s

    @staticmethod
    def normalize_neologd(s):
        s = s.strip()
        s = NeologdNormalizer.unicode_normalize('０−９Ａ-Ｚａ-ｚ｡-ﾟ', s)

        def maketrans(f, t):
            return {ord(x): ord(y) for x, y in zip(f, t)}

        s = s.translate(
            maketrans('!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~｡､･｢｣',
                      '！”＃＄％＆’（）＊＋，−．／：；＜＝＞？＠［￥］＾＿｀｛｜｝〜。、・「」'))
        s = re.sub('[˗֊‐‑‒–⁃⁻₋−]+', '-', s)  # normalize hyphens
        s = re.sub('[﹣－ｰ—―─━ー]+', 'ー', s)  # normalize choonpus
        s = re.sub('[~∼∾〜〰～]', '', s)  # remove tildes
        s = NeologdNormalizer.remove_extra_spaces(s)
        s = NeologdNormalizer.unicode_normalize(
            '！”＃＄％＆’（）＊＋，−．／：；＜＞？＠［￥］＾＿｀｛｜｝〜', s)  # keep ＝,・,「,」
        return s


def normalize_neologd(unicode_string):
    assert isinstance(unicode_string, unicode)
    return NeologdNormalizer.normalize_neologd(unicode_string)


def normalize_askfm(unicode_string, h2z):
    assert isinstance(unicode_string, unicode)
    s = unicode_string
    s = re.sub(r'\s+', ' ', s)
    s = normalize_neologd(s)
    if h2z:
        return jctconv.h2z(s, kana=True, ascii=True, digit=True)
    else:
        return s
