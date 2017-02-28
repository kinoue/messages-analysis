# encoding: utf-8
from __future__ import division
from __future__ import unicode_literals

import unittest
from pathlib import Path
import sys
app_dir = Path(__file__).resolve().parent.parent

if app_dir not in sys.path:
  sys.path.append(str(app_dir))

from em_message import EMMessage

class TestEmMessage(unittest.TestCase):
  def setUp(self):

    self.m0 = EMMessage([0, 0, "apple orange banana", 1])
    self.m1 = EMMessage([1, 10, "apple orange banana", 1])
    self.m2 = EMMessage([2, 20, "dog cat", 1])

  def test_unigram_before(self):
  	unigram = self.m0.ngram_before('orange', n=1)
  	self.assertEqual(unigram[0], 'apple')

  def test_unigram_before2(self):
  	unigram = self.m0.ngram_before('orange banana', n=1)
  	self.assertEqual(unigram[0], 'apple')

  def test_bigram_before(self):
  	bigram = self.m0.ngram_before('banana', n=2)
  	self.assertEqual(bigram[0], 'apple')
  	self.assertEqual(bigram[1], 'orange')

  def test_index_of_word(self):

    self.assertEqual(self.m0.index_of('apple'), 0)


  def test_index_of_word_squence(self):

    self.assertEqual(self.m0.index_of('orange banana'), 1)

  def test_count_word_squence(self):

    self.assertIsNone(self.m0.index_of('orange melon'))


if __name__ == '__main__':
    unittest.main()
