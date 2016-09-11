## This file is as part of the ref bot project
"""
Tools for reading corpora from disk and converting them into feature vectors
"""

from thread_scraper import ScrapingUtils
import collections
from pprint import pprint
from os import listdir
import re

def read_corpus_from_file(path):
    '''Accepts location of txt file, returns list of words in the file'''
    f = open(path, 'r')
    contents = f.read()
    f.close()
    # split on whitespace
    corpus = re.split('\s+', contents.strip())

    return corpus

def augment_features(counter):
    '''
    Normalises features of input vector such that the values are not
    proportional to the size of the corpus

    vector is a collections.Counter
    '''
    # use highest frequency as a statistic
    most_common = counter.most_common(1)[0][1]

    for word in counter:

        # got this formula from wikipedia Tf-idf augmented frequency
        # roughly
        counter[word] *= (1 / most_common)
        #counter[word] += 0.5

    return counter

def reduce_dimensionality(vector, schema):
    '''
    Really simple dimensionality reduction - remove all words in vector which
    are not in the schema

    vector : list of [word, frequency]
    schema : list of words
    '''

    # This will involve going through the whole sum of corpora and finding
    # the 50 highest scoring words, then reducing each corpus to only
    # those words
    vector = [word for word in vector if word[0] in schema]

    non_occuring_words = set(schema).difference(set(dict(vector)))
    non_occuring_words = [(word, 0) for word in non_occuring_words]


    vector += list(non_occuring_words)


    return sorted(vector)

def create_feature_vector(corpus):
    '''
    Accepts list of words, creates feature vector based on normalised
    frequency distribution
    '''
    counter = collections.Counter(corpus)

    # normalise vector using corpus statistics
    dictionary = augment_features(counter)

    vector = dict(counter) # extra f'nality of counter not needed now

    corpus_length = len(corpus)
    vocabulary_size = len(counter)


    feat_vec = [(word, dictionary[word]) for word in dictionary \
        if word not in STOP_WORDS]
    feat_vec.sort() # want in dictionary order

    return feat_vec

def create_vocabulary_schema(feature_vecs, dimensionality, stop_words=[]):
    '''
    Create a schema of a given dimensionality based on a list of feature
    vectors. The highest scoring words will be put in the schema

    feature_vecs : list of feature vectos [[word1,freq1],...,[wordm,freqm]]
        sorted in alphabetical order
    dimensionality : number of words the output schema will contain

    This function assumes all vectors features have been normalised - ie they
    have the same scale
    '''
    total_counter = collections.Counter()

    for vec in feature_vecs:
        # remove words under 3 letters cos they're noise
        # TODO remove word length minimum when stop word f'nality is 
        # implemented
        #
        # or put len(word) > 3 if needed
        vec = [word for word in vec if word[0] not in stop_words]

        counter = collections.Counter(dict(vec))
        total_counter += counter

    schema = list(dict(total_counter.most_common(dimensionality)))

    return schema

def create_schema_using_directory(dir, name):
    '''
    dir : path to a directory containing 1 or more corpora
    dimensionality : K value for output schema

    schema is written to SCHEMA_PATH/name.txt

    dir must have a folder named 'training' containing th corpora
    '''
    path = '/'.join([DATA_ROOT, dir, 'training'])
    files = [f for f in listdir(path) if re.match('.*.txt', f)]
    vectors = []

    for file in files:
        corpus = read_corpus_from_file('/'.join([path, file]))
        vec = create_feature_vector(corpus)
        vectors.append(vec)

    schema = create_vocabulary_schema(vectors, K)
    pprint(schema)
    ScrapingUtils.write_corpus_to_file(schema, \
        '/'.join([SCHEMA_PATH, name + '.txt']))

    print("Created schema " + name + " in " + SCHEMA_PATH)

def create_feature_vector_set(dir, schema_name):
    '''
    dir : e.g. generic_corpora/training
    schema : e.g. banana
    '''
    schema = read_corpus_from_file('/'.join([SCHEMA_PATH,\
        schema_name + '.txt']))

    files = listdir('/'.join([DATA_ROOT, dir]))

    vectors = []

    for file in files:
        corpus = read_corpus_from_file('/'.join([DATA_ROOT, dir, file]))
        vec = create_feature_vector(corpus)
        vec = reduce_dimensionality(vec, schema)

        # finally strip words away so a vector of numbers remains
        vec = [pair[1] for pair in vec]

        vectors.append(vec)
    return vectors

DATA_ROOT = '/media/alex/Hitachi/raw_data'
SCHEMA_PATH = '/'.join([DATA_ROOT, 'topic_schemas'])
K = 100
STOP_WORDS = read_corpus_from_file( \
    '/'.join([DATA_ROOT, 'stop_words', 'generic.txt']))


if __name__ == "__main__":

    # import sys
    # topic = sys.argv[1]
    # data_set = sys.argv[2]



    ## Read in all downloaded corpora
    # files = [f for f in listdir('/'.join([DATA_ROOT, topic, data_set])) \
    #     if re.match('.*.txt', f)]

    #pprint(files)

    create_schema_using_directory('banana_for_scale_corpora', 'banana')
    create_schema_using_directory('generic_corpora','generic')
    create_schema_using_directory('nsa_corpora', 'nsa')

    ## CLASSIFY BANANA FOR SCALE STUFF

    ## Create feature vectors ready for training/testing
    # banana_training_vecs = \
    #     create_feature_vector_set('banana_for_scale_corpora/training', 'nsa')

    # generic_training_vecs = \
    #     create_feature_vector_set('generic_corpora/training', 'nsa')

    # nsa_training_vecs = \
    #     create_feature_vector_set('nsa_corpora/training', 'nsa')


    # # cross validation data found by surfing reddit not in search
    # banana_cv_vecs = \
    #     create_feature_vector_set('banana_for_scale_corpora/cv', 'nsa')

    # banana_test_vecs = \
    #     create_feature_vector_set('banana_for_scale_corpora/test', 'nsa')

    # generic_test_vecs = \
    #     create_feature_vector_set('generic_corpora/test', 'nsa')

    # nsa_test_vecs = \
    #     create_feature_vector_set('nsa_corpora/test', 'nsa')

    #########################################################################

    import readline # optional, will allow Up/Down/History in the console
    import code
    vars = globals().copy()
    vars.update(locals())
    shell = code.InteractiveConsole(vars)
    shell.interact()


