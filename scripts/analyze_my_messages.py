# encoding: utf-8
from __future__ import division
from __future__ import unicode_literals

import os
import datetime
import sys
import logging
import time
import codecs
import json

from collections import defaultdict
from collections import deque

from em_messages_service import EMMessagesService
from em_message import EMMessage
from em_regexp import regexp
from em_print import print_mention_list
from em_print import print_message
from em_prompt import prompt_char
from em_prompt import prompt_int

def print_basic(ems):

    count_total = ems.count_messages()
    count_from_me = ems.count_messages(from_me=True)
    count_from_others = ems.count_messages(from_me=False)        

    print("")
    print("Counting messages in your iMessages...")
    print("")

    print("Message count in total:    %d" % count_total)
    print("Message count from you:    %d" % count_from_me)
    print("Message count from others: %d" % count_from_others)

    first_message = ems.get_first_message()
    last_message = ems.get_last_message()

    first_datetime =first_message.datetime()
    last_datetime =last_message.datetime()
    num_days = (last_datetime - first_datetime).days

    print("")
    print("First message on:          %s" % first_datetime.date().isoformat())
    print("Last message on:           %s" % last_datetime.date().isoformat())
    print("Number of days in between: %d" % num_days)
    print("Number of messages/day:    %.2f" % (count_total / num_days))

    print("")
    '''
    word_count_total = ems.count_words()
    word_count_from_me = ems.count_words(from_me=True)
    word_count_from_others = ems.count_words(from_me=False)

    print("Word count in total:       %d" % len(word_count_total))
    print("Word count from you:       %d" % len(word_count_from_me))
    print("Word count from others:    %d" % len(word_count_from_others))
    '''
    data = {
        'first_message_date': first_datetime.date().isoformat(),
        'last_message_date': last_datetime.date().isoformat(),
        'num_days': num_days,
#        'num_words': word_count_total,
#        'num_words_me': word_count_total,
#        'num_words_others': word_count_total,
        'num_messages': count_total,
        'num_messages_me': count_from_me,
        'num_messages_others': count_from_others
    }
    return data

def count_entities(ems, file, name=None, top_n=20, context=False):
    with codecs.open(file, 'r', 'utf-8') as f:
        patterns = f.readlines()
    patterns = [pattern.strip('\n') for pattern in patterns]
#    patterns = patterns[:20]

    data = defaultdict(int)

    for pattern in patterns:

        messages = ems.get_messages(pattern)

        if len(messages) == 0:
            continue

        data[pattern] = len(messages)

        pos_ngrams_before = []
        neg_ngrams_before = []

        pos_ngrams_after = []
        neg_ngrams_after = []

        pos_bow = []
        neg_bow = []

        print("")
        print("You had %d messages that mentioned %s." % (len(messages), pattern))
        print("")

        print('Are all of your mentions of %s as %s?' % (pattern, name))
        print("")
        print('  [1] Yes, all of them were mentioned as %s' % name )
        print('  [2] Only some of them were mentioned as %s' % name)
        print('  [3] None of them were mentioned as %s' % name)
        print('  [4] I have to see the messages.')
        print("")

        var = prompt_int('Select', min=1, max=4)

        if var == 1:
            print("adding all")
            for message in messages:
                ngram = message.ngram_before(pattern)
                print('ngram: ' + str(ngram))
                pos_ngrams_before.append(ngram)
                pos_ngrams_after.append(message.ngram_after(pattern))
            data['pattern' + '_true'] = len(messages)
            data['pattern' + '_false'] = 0
        elif var == 3:
            for message in messages:
                neg_ngrams_before.append(message.ngram_before(pattern))
                neg_ngrams_after.append(message.ngram_after(pattern))
            data['pattern' + '_true'] = 0
            data['pattern' + '_false'] = len(messages)
        else:
            for message in messages:
                print("")
                print_message(message)    
                print("")
                prompt = 'Is this a correctly identified %s as %s?' % (pattern, name)
                var2 = prompt_char(prompt, ('y','n'))
                if var2 == 'y':
                    pos_ngrams_before.append(message.ngram_before(pattern))
                    pos_ngrams_after.append(message.ngram_after(pattern))
                    data['pattern' + '_true'] += 1
                else:
                    neg_ngrams_before.append(message.ngram_before(pattern))
                    neg_ngrams_after.append(message.ngram_after(pattern))
                    data['pattern' + '_false'] += 1

        print("pos_before: " + str(pos_ngrams_before))

        data['pos_ngrams_before_' + pattern] = pos_ngrams_before
        data['pos_ngrams_after_' + pattern] = pos_ngrams_after
        data['neg_ngrams_before_' + pattern] = neg_ngrams_before
        data['neg_ngrams_after_' + pattern] = neg_ngrams_after

    return data
     
if __name__ == '__main__':
    data = dict()
    ems = EMMessagesService()
    data['overall'] = print_basic(ems)

    name = "restaurants"
    data[name] = count_entities(ems, name=name, file='../dictionaries/good_restaurants.lst', top_n=5, context=True)

    with open(os.path.expanduser('~/Desktop/my_messages.json'), 'w') as out_file:
        json.dump(data, out_file, indent=4, separators=(',', ': '))
