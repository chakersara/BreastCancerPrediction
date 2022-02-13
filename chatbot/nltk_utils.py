import os
from pprint import pprint
import nltk.tokenize as tkn
from nltk.stem.porter import PorterStemmer
import numpy as np


def tokenize(sentence):
    return tkn.word_tokenize(sentence)

def stem(word):
    return PorterStemmer().stem(word.lower())

def bag_of_word(tk_sentence,all_words):
    tk_sentence=list(map(lambda w:stem(w),tk_sentence))
    bag=np.zeros(len(all_words),dtype=np.float32)
    for index,w in enumerate(all_words):
        if w in tk_sentence:
            bag[index]=1.0
    return bag

if __name__ == "__main__":
    pass