## This file is a part of ref bot project

## need to look at writing a corpus tools module, with support for
#  normalising words and manipulating the corpus until it represents a
#  feature vector or something that can easily be transformed into one
"""
Implements the capability of turning threads on Reddit into text corpora
"""

import json
import praw
import praw.errors
import re
from stemming.porter2 import stem
import training_data_finder
from bot_globals import *

class ThreadScraper:
    """
    Contains methods which turn reddit threads/comment trees into text
    corpora ready for classification
    """
    def __init__(self, urls=None, dir=""):

        if type(urls) is list:
            self.urls = urls
        elif urls is None:
            self.urls = []
        else:
            self.urls = [urls]

        if dir:
            assert dir[-1] == '/', "Input directory must end in /"
        self.dir = GENERIC_FOLDER + dir


    @staticmethod
    def __normalise_word(word):
        '''Processes word so it can be inserted into text corpus'''

        # don't strip chars out of hyperlinks/subreddit links
        if not re.match('https?://|/r/|www', word):
            word = re.sub('\W', '', word) # remove non word characters
            word = stem(word) # don't want to stem if giving to nltk
            word = ""
        word = word.lower()
        return word

    @staticmethod
    def __get_thread(url, timelimit=20):
        '''
        Returns list of praw comment objects

        Can be passed an URL to a whole thread, or a specific comment, only
        issue is when given a comment URL only returns the comment, not the
        comment + all its children

        Timelimit in seconds is roughly assured as praw will only send requests
        every 2s, so if the limit is 20 there will be maximum 10 extra requests
        sent.
        '''
        thread = REDDIT.get_submission(url)
        max_calls = int(timelimit / 2)


        if len(thread.comments) == 1:
            print("Fetching children for comment!")
            comment = thread.comments[0]
            thread = training_data_finder.PRAWUtil\
                .get_all_child_comments(comment, max_calls)

        # When it is a single comment (probably meaning a permalink has been)
        # supplied
        else:
            print("Fetching children for submission!")
            ## replace_more_comments will replace limit morecomments objects, remove
            # the rest of the morecomments objects and return them from the method
            #
            # Every morecomments that is replaced with take an additional 2s at least
            thread.replace_more_comments(limit=max_calls, threshold=0)
            thread = thread.comments # ditch everything but comments

            print("got comme`nts")

        #for comment in thread:
        #   assert(isinstance(comment, praw.objects.Comment)), type(comment)

        return thread

    @staticmethod
    def __normalise_corpus(corpus):
        '''Accepts list of strings. Feeds each word to __normalise_word'''
        normalised_corpus = []

        # need to clean up corpus
        for i in range(len(corpus)):
            normalised_word = ThreadScraper.__normalise_word(corpus[i])
            # Ignore all non-link words
            if len(normalised_word) == 0:
                continue
            normalised_corpus.append(normalised_word)

        return normalised_corpus

    @staticmethod
    def __create_corpus(thread):
        '''Accepts list of praw.comments and returns list of words'''
        thread_string = ""

        for comment in thread:
            thread_string += comment.body + ' '

        ## must ensure that words are separated correctly before they are passed
        #  on to be individually normalised

        # remove square and round brackets as they are used for embedding image
        # links in quotes
        thread_string = re.sub('[\[\]\(\)]', ' ', thread_string)

        # split on any form of whitespace
        corpus = re.split('\s+', thread_string)

        normalised = ThreadScraper.__normalise_corpus(corpus)

        normalised = sorted(normalised)

        # Add subreddits where this link has been posted
        output = []
        for link in normalised:
            output.append(link)
            matches = REDDIT.search(link)

            iterator = iter(matches)
            while True:
                try:
                    match = next(iterator)
                    url = match.subreddit.url
                    output.append("    " + url)
                except StopIteration:
                    break
                except praw.errors.RedirectException:
                    url = thread.getSubredditUrl()
                    output.append("    " + url)

        return output

    @staticmethod
    def __scrape_thread(url, directory=None):
        '''
        Accepts an URL, fetches praw comments from it, converts them into a
        corpus, then writes the corpus to a file in directory dir, with a
        generated unique name
        If no dir is given corpus is returned
        '''

        thread = ThreadScraper.__get_thread(url)
        root = thread[0]

        # unique idenditifer for a comment tree/thread
        if root.author:
            thread_id = root.author.name
        else:
            thread_id = 'deleted'
        thread_id += '_' + root.name

        corpus = ThreadScraper.__create_corpus(thread)

        if directory:
            ScrapingUtils.write_corpus_to_file(corpus, url, directory + thread_id + '.txt')
        else:
            return corpus

    def scrape(self):
        """
        Public method, scrapes all given/taken urls to given directory
        """
        for url in self.urls:
            try:
                output = ThreadScraper.__scrape_thread(url, directory=self.dir)
            except:
                print("Failed to scrape " + url)
                continue

    def find(self, search_term, limit=20):
        """
        Searches for threads and adds them to the urls which can then be
        scraped
        """
        results = MULTI_REDDIT.search(search_term, limit=limit)
        urls = [sub.permalink for sub in results]
        self.urls += urls

    def addHotList(self, limit=20):
        results = MULTI_REDDIT.get_hot(limit=limit)
        urls = [sub.permalink for sub in results]
        self.urls += urls

class ScrapingUtils:
    
    @staticmethod
    def write_corpus_to_file(corpus, url, path):
        '''Accepts list of strings and a path *.txt'''
        f = open(path, 'w')
        f.write("Scraped from " + url + " as part of the subreddit " + SUBREDDIT_STRING_ID)
        f.write("\n")
        f.write('\n'.join(corpus))
        f.close()
        print("Wrote corpus to " + path)


    #############################################################################

if __name__ == "__main__":



    ###########################################################################
    ## Main

    # banana for scale urlsf = open('corpus.txt', 'w')

    # for word in corpus:
    #   f.write(word)
    #   f.write(' ')

    # f.close()

    # these 5 banana for scale urls have my peel of approval
    #saving these for test data
    banana1 = 'http://www.reddit.com/r/worldnews/comments/1qluvy/indian_train_strikes_herd_of_40_elephants/cde4vvv'
    banana2 = 'http://www.reddit.com/r/pics/comments/1rcx07/caught_a_little_octopus_in_costa_rica/cdm6mj2'
    banana3 = 'http://www.reddit.com/r/funny/comments/1reeuf/we_bought_a_big_ass_pizza_today_my_wife_asked_me/'
    banana4 = 'http://www.reddit.com/r/funny/comments/1rj8l8/reddit_right_now_fixed/'
    banana5 = 'http://www.reddit.com/r/aww/comments/1rkij9/my_girlfriend_works_at_an_animal_shelterso_when/'


    #bananaposts = MULTI_REDDIT.search('banana for scale', limit=40)
    #nsaposts = REDDIT.search('nsa', limit=80)



    banana_for_scale_urls = [banana1, banana2, banana3, banana4, banana5]

    #front_page = MULTI_REDDIT.get_top(limit=25)

    # these links are the threads which will be scraped
    # links = [submission.permalink for submission in nsaposts]

    # for url in links:MULTI_REDDIT
    #   ThreadScraper(url, 'nsa_corpora/')

    ts = ThreadScraper()
    #ts.find('nsa', 80)
    ts.addHotList(3)

    ts.scrape()


#############################################################################
#start_interactive_shell()

    import readline # optional, will allow Up/Down/History in the console
    import code
    vars = globals().copy()
    vars.update(locals())
    shell = code.InteractiveConsole(vars)
    shell.interact()