import imp, operator, os
import numpy as np
from collections import defaultdict
# import ujson as json
import timeit, math
import matplotlib.pyplot as plt

from sklearn import cross_validation, svm
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.grid_search import GridSearchCV
from sklearn.learning_curve import learning_curve, validation_curve
from sklearn.metrics import classification_report, precision_recall_curve
from sklearn.preprocessing import label_binarize
from sklearn.externals import joblib

from data_processing import *


def read_words(file_name):
    """
    Returns a list of lines read from the given file.
    """
    with open(file_name, 'r') as f:
        return f.readlines()


def load_dataset(words_work_file_name, norm_tweets_file_name):
    """
    Creates training examples X with labels y suitable for use with sklearn classifiers from preprocessed data.
    It uses CountVectorizer to create features from dictionary of words contained in words_work_file_name and
    all unigrams, bigrams and trigrams extracted from normalized tweets contained in norm_tweets_file_name.

    Input:
        words_work_file_name - (Dictionary) file containing normalized words from the whole dataset, one word per line
        norm_tweets_file_name - file containing labeled normalized tweets

    Output:
        X - matrix of training examples
        y - vector of labels
        vectorizer - sklearn CountVectorizer used for ngram tokenization
    """
    words = read_words(words_work_file_name)
    labeled_tweets = read_normalized_tweets(norm_tweets_file_name)  # list of tuples (label, string_of_normalized_words)

    vectorizer = CountVectorizer(analyzer='word', ngram_range=(1, 3), max_df=0.75, max_features=10000)
    vectorizer.fit(words)

    m = len(labeled_tweets)
    tweet_list = []
    Y = np.empty((m,))

    for idx, t in enumerate(labeled_tweets):
        Y[idx,] = t[0]
        tweet_list.append(t[1])

    X = vectorizer.transform(tweet_list)

    return X, Y, vectorizer


def check_preprocessed_data():
    """
    Checks if files created during preprocessing step exist.
    Raises an exception if they don't.
    """
    required_files = [FILE_PATH, ATTRIBUTE_FILE_PATH]
    for required_file in required_files:
        if not os.path.isfile(required_file):
            raise Exception('%s does not exist, please run preprocess.py first.' % (required_file))


def train_classifier(X_train, y_train, scoring):
    """
    Trains an SVM classifier using the training data and a grid-search to fit the estimator hyperparameters.
    """
    # optimized hyperparameters
    # weight_dicts = [{1: 1, -1: 1}, {1: 3, -1: 1}, {1: 1, -1: 3}, {1: 5, -1: 1}, {1: 1, -1: 5}, {1: 10, -1: 1},
    #               {1: 1, -1: 10}, {1: 20, -1: 1}, {1: 1, -1: 20}]

    weight_dicts = [{0: 1, 1: 1, 2: 1, 3: 1, 4: 1},
                    {0: 3, 1: 1, 2: 2, 3: 2, 4: 1},
                    {0: 40, 1: 1, 2: 9, 3: 16, 4: 5},
                    {0: 20, 1: 1, 2: 4, 3: 10, 4: 2},
                    {0: 1, 1: 20, 2: 4, 3: 2, 4: 8},
                    {0: 0.8, 1: 10, 2: 3, 3: 2, 4: 6}
                    ]

    param_grid = [
        {'C': [0.01, 0.1, 1, 10, 100, 1000], 'kernel': ['linear'], 'class_weight': weight_dicts,
         'probability': [True, False], 'shrinking': [True, False]}
    ]

    print 'Performing grid search to find an optimal estimator using scoring function %s and a parameter grid %s' % (
    scoring, param_grid)
    clf = GridSearchCV(svm.SVC(C=1, ), param_grid, cv=3, scoring=scoring)
    print

    clf.fit(X_train, y_train)
    print 'Grid search complete.'

    print_grid_search_results(clf, scoring)
    print

    return clf


def print_grid_search_results(clf, scoring):
    print 'Grid scores based on score function %s:' % (scoring)
    for params, mean_score, scores in clf.grid_scores_:
        print("%0.3f (+/-%0.03f) for %r"
              % (mean_score, scores.std() / 2, params))

    print
    print 'parameter setting that gave the best results on the hold out data:'
    print clf.best_params_

    print
    print 'score of best_estimator on the left out data:'
    print clf.best_score_

    print
    print 'estimator that was chosen by the grid search:'
    print clf.best_estimator_


def print_cv_classification_report(clf, X_test, y_test):
    """
    Prints weighted average of precision, recall and F1-score over each of the classes in the test dataset.

    see sklearn.metrics.classification_report
    """
    print 'Classification report on training data (with cross validation):'
    y_true, y_pred = y_test, clf.predict(X_test)

    target_names = ['NotGettingHired', 'GettingHired']
    print classification_report(y_true, y_pred, target_names=target_names)


def get_target_class(file_path):
    tuples = read_normalized_tweets(file_path)
    target = []
    for t in tuples:
        target.append(t[0])

    return target


def read_tweets(file_path):
    with open(file_path, 'r') as f:
        tuples = []
        lines = f.readlines()
        for line in lines:
            tokens = line.split(' ')
            tuples.append(' '.join(tokens[1:]))

    return tuples


def test_prediction():
    labeled_tweets = read_tweets("./data/model/test.txt")
    clf = joblib.load('C4_new_f1_micro_SVC.pkl')
    best_estimator = clf.best_estimator_
    vector = joblib.load('C4_new_micro_vectorizer.pkl')
    test_x = vector.transform(labeled_tweets)
    # print_most_significant_features(best_estimator.coef_, vector, 100000)

    result = clf.predict(test_x)

    test_y = get_target_class("./data/model/test.txt")
    match = 0
    for indx in range(len(result)):
        print(result[indx], test_y[indx])
        if result[indx] == test_y[indx]:
            match += 1
    print("Accuracy: {}%".format((float(match) / len(result)) * 100))

    # Confidence value
    result = clf.predict_proba(test_x)
    print(result)


def main():
    # mark the beginning time of process
    start = timeit.default_timer()

    check_preprocessed_data()

    X, y, vectorizer = load_dataset(ATTRIBUTE_FILE_PATH, FILE_PATH)
    joblib.dump(vectorizer, 'C4_new_micro_vectorizer.pkl')

    # split the data into train/test sets making test set one tenth of all data
    X_train, X_test, y_train, y_test = cross_validation.train_test_split(X, y, test_size=0.1, random_state=5)

    # scoring = 'roc_auc', 'precision', 'f1', 'recall'
    scoring = 'f1_micro'

    clf = train_classifier(X_train, y_train, scoring)
    joblib.dump(clf, 'C4_new_' + scoring + '_SVC.pkl')

    print 'Done.'

    ##### mark the ending time of process #####
    end = timeit.default_timer()
    seconds = math.ceil(end - start)
    # Convert Secs Into Human Readable Time String (HH:MM:SS)
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    print "This process took %d:%02d:%02d" % (h, m, s)


if __name__ == '__main__':
    main()