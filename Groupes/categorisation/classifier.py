"""Classifier of legal textual documents.
sk-learn version=0.20.3
Pour des raisons de compatibilité, certains algos sont commenté/modifié
LinearSVC ==> SVC
ComplementNB ==> commenté
"""
import argparse
from argparse import RawTextHelpFormatter
from sklearn import metrics
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
# from sklearn.svm import LinearSVC, SVC
from sklearn.svm import SVC

# from sklearn.naive_bayes import ComplementNB
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
# from sklearn.neural_network import MLPClassifier

from sklearn.externals import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from pandas_ml import ConfusionMatrix

from settings import *

import pickle


CLF = {
    "rf": RandomForestClassifier,
    "svm": SVC,
#     "nb": ComplementNB,
    "lr": LogisticRegression,
    # "gbdt": GradientBoostingClassifier,
    # "mlp": MLPClassifier,
    "dummy": DummyClassifier
}

def main():
    args = get_args()

    # prepare data
    X, Y = prepare_data(args.corpus, args.features)

    # train_test protocol: 8:2
    x_train, x_test, y_train, y_test = \
        train_test_split(X, Y, test_size=0.2, random_state=12)

    # build pipeline
    parameters = CLF_PARAM[args.classifier]
    clf = CLF[args.classifier](**parameters)
    vectorizer = TfidfVectorizer(
        # max_features=int(args.feature_size) if args.feature_size else
        # FEATURE_SIZE,
        strip_accents='ascii',
        max_df=0.7,
        min_df=5,
        # ngram_range=(1,3)
    )
    pipeline = Pipeline([
        ('tfidf', vectorizer),
        ('clf', clf)
    ])

    # experiment
    pipeline.fit(x_train, y_train)
    y_pred = pipeline.predict(x_test)

    # evaluation
    print(metrics.classification_report(y_test, y_pred))
    print(ConfusionMatrix(y_test, y_pred))

    # save model
    if args.output:
        joblib.dump(pipeline, open(args.output,"wb"))

def get_args():
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument('corpus')
    parser.add_argument(
        '-c', "--classifier",
        # choices=['rf', 'svm', 'nb', 'gbdt', 'lr', 'mlp', 'dummy'],
        choices=['rf', 'svm', 'lr', 'dummy'],

        default='dummy',
        help=CLF_HELP
    )
    parser.add_argument(
        '-f', "--features",
        choices=["token","lemma","lemma+pos"],
        default="token",
        help=FEAT_HELP
    )
    parser.add_argument('-s', "--feature_size")
    parser.add_argument('-o', "--output")
    return parser.parse_args()

def prepare_data(filein,feat):
    corpus = pickle.load(open(filein,"rb"))
    X = list()
    Y = list()
    for doc in corpus:
        Y.append(doc.class_)
        X.append(FEAT[feat](doc))
    return (X,Y)

def get_token(doc):
    return " ".join(doc.question.text)

def get_lemma(doc):
    return " ".join(doc.question.lemma)

def get_lp(doc):
    return " ".join([t[1]+"/"+t[2] for t in doc.question.tagged_text()])

def get_ngram(doc):
    pass

FEAT = {
    "token": get_token,
    "lemma": get_lemma,
    "lemma+pos": get_lp,
    # "ngram": get_ngram,
}

if __name__ == "__main__":
    main()
