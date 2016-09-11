#!/usr/bin/env python
import pika
import praw
import redis
import json
import datetime
import time

def getSubmissionData(iterator):
    output = []
    while True:
        try:
            match = next(iterator)


            submissionData = {
                "subreddit_name": str(match.subreddit),
                "permalink": match.permalink,
                "score": match.score,
                "url": match.url,
                "author": str(match.author),
                "created_utc": match.created_utc,
                "title": match.title
            }
            output.append(submissionData)
            print("    " + str(submissionData))
        except praw.errors.RedirectException:
            continue
        except StopIteration:
            return output
        
def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    cached = cache.get(body)
    if cached is not None and "submission_data_list" in cached.decode("utf-8"):
        print("Ignoring cached url " + str(body))
        return

    matches = r.search(body)

    iterator = iter(matches)
    cache_data = {
        "cache_timestamp_utc": int(time.mktime(datetime.datetime.utcnow().timetuple())),
        "submission_data_list": getSubmissionData(iterator)
    }
            
    searchData = json.dumps(cache_data)
    print("caching: " + searchData)
    cache.set(body, searchData, ex=3600)

if __name__ == "__main__":

    print(' [*] Waiting for messages. To exit press CTRL+C')
    while True:
        try:
            r = praw.Reddit(user_agent='subreddit finder chrome extension (alexr1993@gmail.com)')
            cache = redis.StrictRedis(host='localhost', port=6379, db=0)
            queue_name = "request queue"
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
            channel = connection.channel()
            channel.queue_declare(queue_name)
            channel.basic_consume(callback, queue=queue_name, no_ack=True)
            channel.start_consuming()
        except Exception as ex:
            print(ex)
