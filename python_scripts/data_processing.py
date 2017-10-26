from pymongo import MongoClient
import json
from nltk.util import ngrams
import HTMLParser, re, string, nltk
from nltk.corpus import stopwords


# from ark_twokenize import *


COLLECTION_NAME = "label"
TEXT_COLELCTION_NAME = "oneYearData"
FILE_PATH = "./data/model/training.txt"
ATTRIBUTE_FILE_PATH = "./data/model/new_attributes.txt"


p = re.compile(r'^#*[a-z]+[\'-/]*[a-z]*$', re.UNICODE)
pLink = re.compile(r'https*:\S+\.\w+', re.IGNORECASE)
pMention = re.compile(r'@[A-Za-z0-9_]+\b')
pNewLine = re.compile(r'[\r\n]+')
pRetweet = re.compile(r'\brt\b', re.IGNORECASE)
punctuation = { 0x2018:0x27, 0x2019:0x27, 0x201C:0x22, 0x201D:0x22 }
h = HTMLParser.HTMLParser()


def get_normalized_word(w):
    """
    Returns normalized word or None, if it doesn't have a normalized representation.
    """
    if pLink.match(w):
        return '[http://LINK]'
    if pMention.match(w):
        return '[@SOMEONE]'
    if type(w) is unicode:
        w = w.translate(punctuation).encode('ascii', 'ignore')  # find ASCII equivalents for unicode quotes
    if len(w) < 1:
        return None
    if w[0] == '#':
        w = w.strip('.,*;-:"\'`?!)(').lower()
    else:
        w = w.strip(string.punctuation).lower()
    if not(p.match(w)):
        return None
    return w


def filter_words(text, stopset):

    """
    Keep only words that pass get_normalized_word(), return them as a list ---- origin method
    """
    # naive tokenization
    words = text.split()

    # # ArkTweetNLP tokenizer
    # words = tokenizeRawTweetText(text)

    tokens = []
    for w in words:
        normalized_word = get_normalized_word(w)

        if normalized_word is not None:

            # remove stopwords from normalized tweet
            if normalized_word not in stopset:

                tokens.append(normalized_word)

    tokens = stemmer_lemmatizer(tokens)

    return tokens


def stemmer_lemmatizer(tokens):

    wnl = nltk.WordNetLemmatizer()
    return [wnl.lemmatize(t) for t in tokens]


def read_normalized_tweets(file_path):
    with open(file_path, 'r') as f:
        tuples = []
        lines = f.readlines()
        for line in lines:
            tokens = line.split(' ')
            tuples.append((tokens[0], ' '.join(tokens[1:])))

    return tuples


def get_attributes(data_list):
    unigrams_set = set()
    bigrams_set = set()
    trigrams_set = set()
    stopset = set(stopwords.words('english'))

    with open(ATTRIBUTE_FILE_PATH, 'w') as output_file:
        for data in data_list:
            text = filter_words(data[1], stopset)

            for unigram in text:
                unigrams_set.add(unigram.rstrip())

            bigrams = ngrams(text, 2)
            for grams in bigrams:
                if grams[0] != grams[1]:
                    bigram = grams[0] + ' ' + grams[1]
                    bigrams_set.add(bigram)

            trigrams = ngrams(text, 3)
            for grams in trigrams:
                if (grams[0] != grams[1]) and (grams[0] != grams[2]) and (grams[1] != grams[2]):
                    trigram = grams[0] + ' ' + grams[1] + ' ' + grams[2]
                    trigrams_set.add(trigram)

        for gram_set in [unigrams_set, bigrams_set, trigrams_set]:
            for ngram in gram_set:
                output_file.write(ngram.encode('utf-8') + '\n')


def get_data(db):
    data_list = []

    with open(FILE_PATH) as input_file:
        for line in input_file:
            document = line.strip().split(" ")
            data_list.append((document[0], " ".join(document[1:])))
    get_attributes(data_list)


def main():
    mongo_client = MongoClient('localhost', 3001)
    db = mongo_client.meteor
    get_data(db)


if __name__ == '__main__':
    main()
