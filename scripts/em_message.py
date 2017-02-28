# encoding: utf-8
from __future__ import division
from __future__ import unicode_literals

import datetime
import re
from em_model import EMModel 

class EMMessageText(str):
    def split(self):
        original_tokens = self.__str__().split()
        tokens = []
        for token  in original_tokens:
            match = re.match("^([a-z]+)([!\?\,\.\:\;]+)$", token)
            if match:
                tokens.append(match.group(1))
                tokens.append(match.group(2))
            else:
                tokens.append(token)
        return tokens


class EMMessage(EMModel):

    def __init__(self, array):
        self.msgId = array[0]
        self.ts = array[1]
#        text = array[2].replace(u'&#8216;', u"'").replace(u'&#8217;', u"'").lower()
        self.original_text = array[2]
        text = array[2].lower()
        replaces = {
            u"\u2026": "...",
            u"\u2018": "'",
            u"\u2019": "'",
            u"\u2014": "-",
            u"\u201c": '"',
            u"\u201d": '"'
        }

        for key, value in replaces.items():
            text = text.replace(key, value)

        self.text = EMMessageText(''.join(i for i in text if ord(i)<128))
#        self.text = EMMessageText(array[2].replace(u'&#8216;', u"'").replace(u'&#8217;', u"'").lower())
        self.is_from_me = array[3]

    def split(self, text):
        return self.tokens(text)

    def tokens(self, text=None):
        '''
        Python's default split() does not seprate the punctuations from the words
        '''

        if text is None:
            text = self.text

        original_tokens = text.split()
        tokens = []
        for token  in original_tokens:
            match = re.match("^([a-z]+)([\!\?\,\.\:\;]+)$", token)
            if match:
                tokens.append(match.group(1))
                tokens.append(match.group(2))
            else:
                tokens.append(token)
        return tokens


    def datetime(self):
        zero_datetime = datetime.datetime(2000, 1, 1)
        return zero_datetime + datetime.timedelta(seconds=self.ts)

    def ngram_before(self, pattern, whole_word=True, n=3):
        match = re.search(pattern, self.text)
        if match:
#            return self.split(self.text[:match.start()][-n:]
            return self.text[:match.start()].split()[-n:]
        return None
        
    def ngram_after(self, pattern, whole_word=True, n=3):
        match = re.search(pattern, self.text)
        if match:
#            return self.split(self.text[match.end():][:n]
            return self.text[match.end():].split()[:n]
        return None

    def index_of(self, pattern):
        match = re.search(pattern, self.text)
        if match:
#            return  len(self.split(self.text[:match.start()]))
            return len(self.text[:match.start()].split())
        return None
