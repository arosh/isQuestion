from __future__ import division, print_function, unicode_literals
import sqlite3
import json
import codecs
import glob
import sys
import re

def init():
    sys.stdin = codecs.getreader('utf_8')(sys.stdin)
    sys.stdout = codecs.getwriter('utf_8')(sys.stdout)
    sys.stderr = codecs.getwriter('utf_8')(sys.stderr)

def trim(s):
    s = re.sub('^\s+', '', s)
    s = re.sub('\s+$', '', s)
    s = re.sub('\n', ' ', s)
    s = re.sub('\s+', ' ', s)
    return s

def main():
    init()

    with sqlite3.connect('ezoe_qa.sqlite3') as con:
        con.row_factory = sqlite3.Row

        for fname in glob.glob('database/*.json'):
            with codecs.open(fname, 'r', 'utf_8') as f:
                o = json.load(f)
                for qa in o:
                    c = con.execute('SELECT COUNT(*) FROM ezoe_qa WHERE url=:url', qa)
                    if c.fetchone()[0] == 0:
                        qa['question'] = trim(qa['question'])
                        qa['answer'] = trim(qa['answer'])
                        qa['url'] = trim(qa['url'])
                        con.execute('INSERT INTO ezoe_qa (question, answer, url) VALUES (:question, :answer, :url)', qa)

if __name__ == '__main__':
    main()
