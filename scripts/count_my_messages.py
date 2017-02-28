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
from em_stop_words import stop_words
from em_message import EMMessage
from em_regexp import regexp
from em_prompt import prompt_char


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

    word_count_total = ems.count_words()
    word_count_from_me = ems.count_words(from_me=True)
    word_count_from_others = ems.count_words(from_me=False)

    print("Word count in total:       %d" % len(word_count_total))
    print("Word count from you:       %d" % len(word_count_from_me))
    print("Word count from others:    %d" % len(word_count_from_others))

    print("")
    print("Top 20 words from you:     ")
    print_counts(word_count_from_me)
    
    print("")
    print("Top 20 words from others:  ")
    print_counts(word_count_from_others)

    data = {
        'first_message_date': first_datetime.date().isoformat(),
        'last_message_date': last_datetime.date().isoformat(),
        'num_days': num_days,
        'num_words': word_count_total,
        'num_words_me': word_count_total,
        'num_words_others': word_count_total,
        'num_messages': count_total,
        'num_messages_me': count_from_me,
        'num_messages_others': count_from_others
    }

    return data



def print_counts(counts, n=20, width=22):

    for count in counts[:n]:
        space = " "
        for _ in range(width - len(count[0])):
            space += " "
        print("    %s%s%3d" % (count[0], space, count[1])) 


def analyze_and_print(ems, file, name=None, top_n=20, context=False):

    first_message = ems.get_first_message()
    last_message = ems.get_last_message()

    first_datetime =first_message.datetime()
    last_datetime =last_message.datetime()
    num_days = (last_datetime - first_datetime).days

    print("")
    print("Counting %s mentioned in your iMessages..." % name)

    count_list = ems.count_messages_with_file(file=file)
    n = top_n if top_n < len(count_list) else len(count_list)

    print("")
    print("Top %d %s mentioned in your messages:" % (top_n, name))

    for i, count in enumerate(count_list[:top_n]):
        print("%3d: %s (%d)" % (i, count[0], count[1]))

    print("")
    total_count  = sum([c[1] for c in count_list])
    per_day = (total_count / num_days)
    print("Number of mentions in total: %d" % total_count)
    print("Number of mentions per day:  %.2f" % per_day)

    if per_day < 0.1:
        print("(Ok... you don't seem to be into %s...)" % name)
    if per_day > 0.5:
        print("(Man you like talking about %s!)" % name)

    print("")

    data = {}

    if context and per_day > 0.25:

        top_counts = count_list[:10]
        print("Now let's see how you talked about them...")

        total_word_count_in_context = defaultdict(int)
        total_bigram_count_in_context = defaultdict(int)
        total_trigram_count_in_context = defaultdict(int)

        total_word_count_before = defaultdict(int)
        total_word_count_after = defaultdict(int)
        total_bigram_count_before = defaultdict(int)
        total_bigram_count_after = defaultdict(int)


        for count in top_counts:
            pattern = count[0]
            messages = ems.get_messages(pattern, seconds=60)

            word_count_in_context = ems.count_words_in_messages(messages, sort_counts=False)
            for key, value in word_count_in_context.items():
                total_word_count_in_context[key] += value

            bigram_count_in_context = ems.count_word_sequences_in_messages(messages, n=2, sort_counts=False)
            for key, value in bigram_count_in_context.items():
                total_bigram_count_in_context[key] += value

            trigram_count_in_context = ems.count_word_sequences_in_messages(messages, n=3, sort_counts=False)
            for key, value in trigram_count_in_context.items():
                total_trigram_count_in_context[key] += value

            
            word_count_before = ems.count_words_before(pattern, sort_counts=False)
            for key, value in word_count_before.items():
                total_word_count_before[key] += value

            word_count_after = ems.count_words_after(pattern, sort_counts=False)
            for key, value in word_count_after.items():
                total_word_count_after[key] += value

            bigram_count_before = ems.count_word_sequences_before(pattern, n=2, sort_counts=False)
            for key, value in bigram_count_before.items():
                total_bigram_count_before[key] += value


            bigram_count_after = ems.count_word_sequences_after(pattern, n=2, sort_counts=False)
            for key, value in bigram_count_after.items():
                total_bigram_count_after[key] += value

            '''
            print("")
            print("Top 20 words in the context for %s:" % pattern) 
            print_counts(word_count_in_context)

            print("")
            print("Top 20 two-word sequences in the context for %s:" % pattern) 
            print_counts(bigram_count_in_context)

            print("")
            print("Top 10 words right before %s:" % pattern) 
            print_counts(word_count_before, n=10)

            print("")
            print("Top 10 words rght after %s:" % pattern) 
            print_counts(word_count_after, n=10)

            print("")
            print("Top 10 2-word sequences right before %s:" % pattern) 
            print_counts(bigram_count_before, n=10)

            print("")
            print("Top 10 2-word sequences right after %s:" % pattern) 
            print_counts(bigram_count_after, n=10)
            '''
            '''
            print("For %s:" % pattern)

            for message in messages:
                dt = message.datetime()
                print("  On %d-%d-%d: " % (dt.year, dt.month, dt.day))

                for m in message.context:
                    print("    " + m.text)

                print("")
            print("")
            print("")
            '''
            data[pattern] = {
                'word_count_in_context': word_count_in_context,
                'bigram_count_in_context': word_count_in_context,
                'word_count_before': word_count_before,
                'bigram_count_before': word_count_before,
                'word_count_after': word_count_after,
                'bigram_count_after': word_count_after
            }

        print("")
        print("Top 10 words in the context for %s:" % name) 
        print_counts(sorted(total_word_count_in_context.items(), key=lambda x: -x[1]), n=10)

        print("")
        print("Top 10 two-word sequences in the context for %s:" % name) 
        print_counts(sorted(total_bigram_count_in_context.items(), key=lambda x: -x[1]), n=10)

        print("")
        print("Top 10 three-word sequences in the context for %s:" % name) 
        print_counts(sorted(total_trigram_count_in_context.items(), key=lambda x: -x[1]), n=10)

        print("")
        print("Top 10 words right before %s:" % name) 
        print_counts(sorted(total_word_count_before.items(), key=lambda x: -x[1]), n=10)

        print("")
        print("Top 10 words rght after %s:" % name) 
        print_counts(sorted(total_word_count_after.items(), key=lambda x: -x[1]), n=10)

        print("")
        print("Top 10 2-word sequences right before %s:" % name) 
        print_counts(sorted(total_bigram_count_before.items(), key=lambda x: -x[1]), n=10)

        print("")
        print("Top 10 2-word sequences right after %s:" % name) 
        print_counts(sorted(total_bigram_count_after.items(), key=lambda x: -x[1]), n=10)

    return data


if __name__ == '__main__':
    ems = EMMessagesService()
    data = print_basic(ems)

    if prompt_char('Do you want to count messages about sports?', ['y','n']) == 'y':
        data['sports'] = analyze_and_print(ems, name="sports", file='../dictionaries/sports_lower.lst', context=True)


    if prompt_char('Do you want to count messages about sport teams?', ['y','n']) == 'y':
        data['sport teams'] = analyze_and_print(ems, name="sport teams", file='../dictionaries/teams_lower.lst', context=True)
    
    if prompt_char('Do you want to count messages about restaurants?', ['y','n']) == 'y':
        data['restaurants'] = analyze_and_print(ems, name="restaurants", file='../dictionaries/good_restaurants.lst', context=True)

    if prompt_char('Do you want to count messages about food categories?', ['y','n']) == 'y':
        data['food categories'] = analyze_and_print(ems, name="food categories", file='../dictionaries/food_lower.lst', context=True)

    with open(os.path.expanduser('~/Desktop/my_message_counts.json'), 'w') as out_file:
        json.dump(data, out_file, indent=4, separators=(',', ': '))



