# encoding: utf-8
from __future__ import division
from __future__ import unicode_literals

import os
import datetime
import sqlite3
import re
import sys
import logging
import time
import codecs


from collections import defaultdict
from collections import deque
from em_stop_words import stop_words
from em_message import EMMessage
from em_regexp import regexp

class EMMessagesService():

    def __init__(self):
        db_path = os.path.expanduser('~/Library/Messages/chat.db')
        self.cnx = c = sqlite3.connect(db_path)
        self.cnx.create_function("REGEXP", 2, regexp)
        self.base_query = "select guid, date, text, is_from_me from message" 

#        self.df = self.count_document_frequencies()

    def count_word_sequences_in_messages(self, messages, sort_counts=True, n=2):
        counts = defaultdict(int)
        sequence = deque()
        for message in messages:
            for token in message.text.split():
                sequence.append(token)
                while len(sequence) > n:
                    sequence.popleft()

                counts[" ".join(sequence)] += 1
        if sort_counts:
            count_list = sorted(counts.items(), key=(lambda x: -x[1]))
            return count_list
        else:
            return counts

    def count_words_in_messages(self, messages, sort_counts=True):
        counts = defaultdict(int)
        for message in messages:
            for token in message.text.split():
                if not token in stop_words and len(token) > 2:
                    counts[token] += 1
        if sort_counts:
            return sorted(counts.items(), key=(lambda x: -x[1]))
        return counts


    def count_tokens_from_cursor(self, cursor):
        counts = defaultdict(int)
        for row in cursor:
            for token in row[0].lower().split():
                token = token.replace('’', "'")
                token = token.replace('&#8216;', "'")
                token = token.replace('&#8217;', "'")
                if not token in stop_words and len(token) > 2:
                    counts[token] += 1

        count_list = sorted(counts.items(), key=(lambda x: -x[1]))
        return count_list

    def count_words(self, from_me=None):
        cursor = self.cnx.cursor()

        query = 'select text from message where text is not null'
        if from_me is not None:
            query += " and is_from_me = %d " % (1 if from_me else 0)
        cursor.execute(query)
        return self.count_tokens_from_cursor(cursor)
        
    def count_word_sequences(self, n=2, from_me=None):
        counts = defaultdict(int)
        cursor = self.cnx.cursor()

        query = 'select text from message where text is not null'
        if from_me is not None:
            query += " and is_from_me = %d " % (1 if from_me else 0)

        sequence = deque()
        cursor.execute(query)
        for row in cursor:
            for token in row[0].lower().split():
                token = token.replace('’', "'")
                token = token.replace('&#8216;', "'")
                token = token.replace('&#8217;', "'")
                sequence.append(token)
                while len(sequence) > n:
                    sequence.popleft()

                counts[" ".join(sequence)] += 1

        count_list = sorted(counts.items(), key=(lambda x: -x[1]))
        return count_list

    def count_words_before(self, pattern, whole_word=True, from_me=None, sort_counts=True):
        return self.count_word_sequences_before(pattern, whole_word=whole_word, from_me=from_me, n=1, sort_counts=sort_counts)

    def count_words_after(self, pattern, whole_word=True, from_me=None, sort_counts=True):
        return self.count_word_sequences_after(pattern, whole_word=whole_word, from_me=from_me, n=1, sort_counts=sort_counts)

    def count_word_sequences_after(self, pattern, n=2, whole_word=True, from_me=None, sort_counts=True):
        messages = self.get_messages(pattern=pattern, whole_word=whole_word, from_me=from_me)
        return self.count_word_sequences_in_messages_after(pattern, messages=messages, n=n, whole_word=whole_word, sort_counts=sort_counts)

    def count_word_sequences_before(self, pattern, n=2, whole_word=True, from_me=None, sort_counts=True):
        messages = self.get_messages(pattern=pattern, whole_word=whole_word, from_me=from_me)
        return self.count_word_sequences_in_messages_before(pattern, messages=messages, n=n, whole_word=whole_word, sort_counts=sort_counts)

    def count_word_sequences_in_messages_after(self, pattern, messages, n=2, whole_word=True, sort_counts=True):
        counts = defaultdict(int)
        for message in messages:
            ngram = message.ngram_after(pattern, whole_word=whole_word, n=n)
            if ngram:
                counts[" ".join(ngram)] += 1
        if sort_counts:
            return sorted(counts.items(), key=(lambda x: -x[1]))
        return counts

    def count_word_sequences_in_messages_before(self, pattern, messages, n=2, whole_word=True, sort_counts=True):
        counts = defaultdict(int)
        for message in messages:
            ngram = message.ngram_before(pattern, whole_word=whole_word, n=n)
            if ngram:
                counts[" ".join(ngram)] += 1
        if sort_counts:
            return sorted(counts.items(), key=(lambda x: -x[1]))
        return counts

    def count_messages_with_pattern(self, pattern=None, whole_word=True, from_me=None):
        cursor = self.cnx.cursor()
        query = "select count(*) from message"
        if pattern:
            if whole_word:
                pattern = r'\b%s\b' % pattern
            query += " where lower(text) regexp ?"
            if from_me is not None:
                query += " and is_from_me = %d " % (1 if from_me else 0)

            pattern_regexp = pattern.replace("'", "('|’)?")  # a very common pattern so internalized it
            cursor.execute(query, [pattern_regexp])
        else:
            if from_me is not None:
                query += " where is_from_me = %d " % (1 if from_me else 0)
            cursor.execute(query)

        row = next(cursor)
        logging.info("%d messages counted" % row[0])
        return row[0]

    def get_mentions_with_file(self, file, whole_word=True, sort_counts=True, none_zero=True):
        with codecs.open(file, 'r', 'utf-8') as f:
            patterns = f.readlines()

        patterns = [pattern.strip('\n') for pattern in patterns]
#        patterns = patterns[:20]

        messages_dict = defaultdict(list)
        sys.stdout.write("|--------------------------------------------------|")
        for i, pattern in enumerate(patterns): 

            progress = round((i + 1) / len(patterns) * 50)

            for _ in range(51):
                sys.stdout.write("\b")            

            for _ in range(int(progress)):
                sys.stdout.write("=")

            for _ in range(int(50 - progress)):
                sys.stdout.write("-")            

            sys.stdout.write("|")
            sys.stdout.flush()

            messages = self.get_messages(pattern, whole_word=whole_word)
            if len(messages) > 0:
                messages_dict[pattern] = { 
                    "pattern": pattern,
                    "messages": messages,
                    "count": len(messages)
                }

        print("")

        if sort_counts:
            return sorted(messages_dict.values(), key=(lambda x: -x['count']))
        return messages_dict


    def count_messages_with_file(self, file, whole_word=True, sort_counts=True, none_zero=True):
        with codecs.open(file, 'r', 'utf-8') as f:
            patterns = f.readlines()

        patterns = [pattern.strip('\n') for pattern in patterns]

#        patterns = patterns[:20]
        count_list = []


        sys.stdout.write("|--------------------------------------------------|")
        for i, pattern in enumerate(patterns): 

            progress = round((i + 1) / len(patterns) * 50)

            for _ in range(51):
                sys.stdout.write("\b")            

            for _ in range(int(progress)):
                sys.stdout.write("=")

            for _ in range(int(50 - progress)):
                sys.stdout.write("-")            

            sys.stdout.write("|")
            sys.stdout.flush()
            messages = self.get_messages(pattern, whole_word=whole_word)            

            count = len(messages)
            if not none_zero or count > 0:
                count_list.append((pattern, count))

        print("")

        if sort_counts:
            count_list = sorted(count_list, key=(lambda x: 0 if x[1] is None else -x[1]))

        return count_list

    def count_messages(self, pattern=None, file=None, from_me=None):
        if file:
            return self.count_messages_with_file(file=file)
        else:
            return self.count_messages_with_pattern(pattern=pattern, whole_word=True, from_me=from_me)

    def get_last_message(self, from_me=None):
        cursor = self.cnx.cursor()
        query = self.base_query
        if from_me is not None:
            query += " where is_from_me = %d " % (1 if from_me else 0)

        query += " order by date desc limit 1"
        row = next(cursor.execute(query))
        return EMMessage(row)

    def get_first_message(self, from_me=None):
        cursor = self.cnx.cursor()
        query = self.base_query
        if from_me is not None:
            query += " where is_from_me = %d " % (1 if from_me else 0)

        query += " order by date asc limit 1"
        row = next(cursor.execute(query))
        return EMMessage(row)


    def get_messages(self, pattern=None, seconds=0, whole_word=True, from_me=None):
        '''
        Returns a list of message objects that match the given pattern
        '''
        cursor = self.cnx.cursor()
        query = self.base_query

        if pattern:
            if whole_word:
                pattern = r'\b%s\b' % pattern

            pattern_regexp = pattern.replace("'", "('|’)?")  # a very common pattern so internalized it
            query += " where lower(text) regexp ?"

            if from_me is not None:
                query += " and is_from_me = %d " % (1 if from_me else 0)
        else: 
            if from_me is not None:
                query += " where is_from_me = %d " % (1 if from_me else 0)

        messages = []
        cursor.execute(query, [pattern_regexp])
        for row in cursor:
            messages.append(EMMessage(row))

        if seconds > 0:
            for message in messages:
                min_ts = message.ts - seconds
                max_ts = message.ts + seconds
                query = self.base_query + " where date >= ? and date <= ?"
                cursor.execute(query, [min_ts, max_ts])
                message.context = [EMMessage(row) for row in list(cursor)]

        return messages