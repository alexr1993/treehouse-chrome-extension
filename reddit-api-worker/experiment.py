from flask import Flask
from flask import request
app = Flask(__name__)

from flask.ext.cors import CORS
CORS(app)

from celery import Celery
app = Celery('tasks', backend='amqp', broker='amqp://')

import json
import praw

r = praw.Reddit(user_agent='subreddit finder chrome extension')

# matches = r.search("http://www.politico.eu/article/german-intelligence-warns-of-is-hit-squads-among-refugees/")
# iterator = iter(matches)
# subreddit_cache = {}

# while True:
#     try:
#         match = next(iterator)
#         print("    " + str(match.subreddit))
#     except StopIteration:
#         break
#     except praw.errors.RedirectException:
#         continue

cache = {}

@app.route("/reddit")
def hello():
    link = request.args.get("url")
    print(link)
    if link in cache:
        return cache[link]

    matches = r.search(link)

    iterator = iter(matches)
    output = []
    while True:
        try:
            match = next(iterator)
            sub = str(match.subreddit)
            output.append("/r/" + sub)
            print("    " + sub)
        except StopIteration:
            break
        except praw.errors.RedirectException:
            continue
            
    response =  json.dumps(output)
    cache[link] = response
    return response

if __name__ == "__main__":
    app.run()
