## This file is a part of the ref bot project

"""
Implements the conversion of preprocessed data (feature vectors) into
decisions regarding the output of the bot (e.g. a comment linking this topic
to previous topics).
"""

import numpy as np
from sklearn.naive_bayes import MultinomialNB

class TopicStoreManager:
    """
    Handles CRUD operations concerning the topics which are being observed in
    the Reddit comments.

    Use cases involve creating new topics which haven't been seen before,
    retrieving topics to classify threads against, updating the
    representation of topics as more data is consumed, and potentially
    deleting topics if a criteria is met to merge 2 topics into one

    Topics can be represented by a vocabulary or some for of vector plotted
    in n-dimensional space
    """

    ## Singleton class
    def __init__(self):
        if TS_MANAGER:
            return None

class Classifier:
    """
    Has the capability to learn parameters for the given mathematical model
    and use the mathematical model to classifier a given feature vector as
    belonging to one of the classes contained in the topic store.

    Can report on topics which had not been seen before and therefore must be
    added to the topic store

    Can report on topics which are similar enough to merge into one
    e.g. 'government security internet' and 'nsa snowden whisteblower'
    """

class FeatureVector:

if __name__== "__main__":

    X = banana_training_vecs + generic_training_vecs # concat all training data
    # create list of labels
    y = [1 for x in banana_training_vecs] + [0 for x in generic_training_vecs]


    clf = MultinomialNB()
    clf.fit(X,y)
    print(clf.predict(generic_test_vecs[0])) # should be 0 for all generic vecs

    # useful for viewing vec in order 
    # pprint(sorted(vec, key=lambda word: word[1]))