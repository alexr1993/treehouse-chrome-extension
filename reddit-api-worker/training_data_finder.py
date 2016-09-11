# This file is a part of ref_bot
#
#
#
#
"""
Contains code created to aid the procurement of training data for ref_bot
"""

from abc import ABCMeta
from abc import abstractmethod
import praw
import re
import math
import time

global NEWLINE
global TAB_LENGTH
global OUTPUT_WIDTH
NEWLINE = '\n'
TAB_LENGTH = 4
OUTPUT_WIDTH = 140

class SnapshotTree:
    """Snapshot tree: NON PRAW objects hold 3 levels of comments

    Top level is the root, which contains just one comment.

    The second level contains the comment which the snapshot is focusing on,
    along with all of its siblings.

    The bottom level contains all first generation descendents of the second
    level, essentially giving a well-defined, uniform slice into potenetially
    huge comment trees.

    The idea is that when a comment has "reference" in it, we want to check
    if its parent is a reference, so we use the parent as the starting
    point, look at the siblings for more support and then check the children
    for corroboration. 
    """

    def __init__(self, root, tier2, tier3):
        """
        root must be a Submission
        tier2 must be a list of comments
        tier3 must be nested lists of comments
        """
        # TODO essentially implement what I tried to put in ref_bot but do it
        # with better OO and less memory intensive
        self.root  = root
        self.tier2 = tier2
        self.tier3 = tier3
        
        assert len(tier2) == len(tier3), "Tier 2 and Tier 3 should have the same length"

    def to_string(self):

        out = OtherUtils.create_text_headline("Snapshot Start", '=', OUTPUT_WIDTH)
        # root string
        out += self.root.to_string()

        for i in range(0, len(self.tier2)):

            t2 = self.tier2[i] # a tier 2 comment
            tier3 = self.tier3[i] # all of this comment's children

            depth = 1

            out += NEWLINE * 2
            out += t2.to_string(depth) # direct child comment

            for t3 in tier3:

                depth = 2

                out += NEWLINE * 2
                out += t3.to_string(depth) # grandchild


        out += OtherUtils.create_text_headline("Snapshot End", '=' ,OUTPUT_WIDTH)

        return out




class Post:
    """Base class for comment and submission"""
    __metaclass__ = ABCMeta

    def __init__(self, data):
        """Data is either a praw comment or praw submission"""

        if data.author:
            self.author  = data.author.name
        else:
            self.author  = "DELETED"

        self._id         = data.id # id is private as mongo likes that
        self.name        = data.name

    def to_string(self):
        assert False, "Abstract Method called"

class Comment(Post):

    def __init__(self, data):

        super().__init__(data)

        self.parent_id = data.parent_id
        self.body = data.body

    def to_string(self, depth=0):

        text_width = OUTPUT_WIDTH - TAB_LENGTH * depth

        num_output_lines = math.ceil(len(self.body) / text_width)

        no_nls = self.body.replace('\n', "//")
        
        formatted = (' ' * TAB_LENGTH * depth) + "|ID: " + self._id + ', Author: ' \
            + self.author


        for i in range(num_output_lines):

            start = text_width * i

            if i > len(no_nls) - 1:
                end = len(no_nls) - 1

            else:
                end = start + text_width - 1


            formatted += NEWLINE + (' ' * TAB_LENGTH * depth) + '|' + no_nls[start:end]

        return formatted

class Submission(Post):

    def __init__(self, data):

        super().__init__(data)

        self.title = data.title
        self.selftext = data.selftext
        self.url = data.url
        self.subreddit = data.subreddit.display_name # this is the actual sub name

    def to_string(self):

        output = "Title: " + self.title + '(/r/' + self.subreddit + ')' + NEWLINE * 2
        output += "Author: " + self.author + NEWLINE * 2

        if self.selftext:
            output += "=" * OUTPUT_WIDTH + NEWLINE
            output += self.selftext
            output += NEWLINE + "=" * OUTPUT_WIDTH
            output += NEWLINE * 2


        return output


class SnapshotTreeFactory: 
    """Take (p)raw materials, return snapshot"""

    def __init__(self, root, tier2, tier3):
        """accept root, t2, t3"""

        assert isinstance(root, praw.objects.Submission) or \
               isinstance(root, praw.objects.Comment), type(root)
        for t2 in tier2:
            assert isinstance(t2, praw.objects.Comment), type(t2)
        for t3 in tier3:
            assert isinstance(t3, list), type(t3)

        self.root = root
        self.tier2 = tier2
        self.tier3 = tier3

    def CreateSnapshotTree(self):

        if isinstance(self.root, praw.objects.Comment):
            root = Comment(self.root)
        elif isinstance(self.root, praw.objects.Submission):
            root = Submission(self.root)
        else:
            raise TypeError("Snapshot tree must have submission/comment as root")

        # create comment objects for root's direct children
        tier2 = [Comment(t2) for t2 in self.tier2]

        tier3 = []

        # create comment objects for each grandchildren sublist
        for sublist in self.tier3:
            tier3.append([Comment(t3) for t3 in sublist])

        return SnapshotTree(root, tier2, tier3)

class PRAWUtil:
    """
    Functions which accept PRAW Objects such as praw.Comment and
    praw.Submission"""
    def get_comment_by_id(permalink, id_):
        """Return a PRAW.Comment objects for a given permalink"""
        comment_permalink = permalink + id_

        # The submission returned will have the permalinked comment as its first
        return REDDIT.get_submission(comment_permalink).comments[0]

    ## actually get all comment objects to be efficient
    def get_all_direct_children(post):
        """Get all top level replies for a given PRAW post"""


        assert isinstance(post, praw.objects.Comment) or \
               isinstance(post, praw.objects.Submission), type(post)

        permalink = post.permalink
        name = post.name

        if isinstance(post, praw.objects.Comment):
            replies = post.replies
        else:
            replies = post.comments

        output = []

        while True:

            # list for the more comments so we can tell when there have been
            # two in the same set
            more = []

            for r in replies:

                # append child comments to output
                if r.parent_id == name and \
                        isinstance(r, praw.objects.Comment):
                        
                    output.append(r) # Recursively instantiate children... possibly needs to be changed.

                # there should only be one morecomments object for each parent per reply set
                # set more comments variable
                elif r.parent_id == name and isinstance(r, praw.objects.MoreComments):
                    more.append(r)

                # non-direct children are to be discarded
                else:
                    continue

            # sometimes there are multiple more comments for one parent, feature or bug?
            # assert len(more) <= 1

            # no more replies
            if more == []:

                # print(str(len(output)) + " replies found for " + permalink + "\n")

                for reply in output:
                    assert(isinstance(reply, praw.objects.Comment))

                return output

            # update variant
            replies = []

            # keep pumping in more comments
            for m in more:

                # This true/false stuff is to prevent MoreComments.comments (praw\objects.py ln6 00)
                # from crashing the script
                update = False

                # if submission does not exist we must request it again
                if not m.submission:
                    update = True

                try:    
                    replies += m.comments(update)

                except Exception:
                    error_string = ""
                    error_string += "After " + str(len(output)) + " comments were collected, morecomments.comments()"
                    error_string += " failed for " + permalink + "\n"
                    error_string += "See http://www.reddit.com/r/redditdev/comments/1ijb3m/error_when_running_a_praw_script/\n"

                    print(error_string)
                    continue

    def get_all_child_comments(post, depthlimit=None, depth=0):
        '''
        Accepts PRAW.objects.Comment
        Returns depthlimit layers of child comments in flat list'''

        assert(depthlimit >= 1)
        assert(depth >= 0)
        assert(isinstance(post, praw.objects.Comment)), type(post)

        if(depth + 1 == depthlimit):
            return [post] + PRAWUtil.get_all_direct_children(post)

        else:
            output = [post]
            for child in PRAWUtil.get_all_direct_children(post):
                # output.append(child) this causes duplication
                output += PRAWUtil.get_all_child_comments(child, depthlimit, \
                    depth + 1)
            return output

class OtherUtils:
    def create_text_headline(headline, char, width):
        """Create text dividiers e.g. ------New Section------ char is the
        filler on either side
        """
        sidelength = math.floor((width - len(headline)) / 2)
        line = (char * sidelength) + headline + (char * sidelength)

        return NEWLINE + line + NEWLINE
