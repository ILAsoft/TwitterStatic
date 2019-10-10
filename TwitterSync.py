#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function

import json
import sys
from datetime import datetime

import twitter
try:
    from TwitterSyncSettings import MAX_COUNT, INCLUDE_RTS, TRIM_USER, PATH, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET
except:
    print("First rename TwitterSyncSettings.sample as TwitterSyncSettings.py and update values!")
    exit()


def get_tweets(api=None, screen_name=None, since_id=None):
    count = 0
    timeline = list()
    earliest_tweet = None
    while True:
        tweets = api.GetUserTimeline(
            screen_name=screen_name, max_id=earliest_tweet, include_rts=INCLUDE_RTS, trim_user=TRIM_USER,
            since_id=(since_id if MAX_COUNT == None else 0),
            count=(200 if (MAX_COUNT == None) else MAX_COUNT)
        )
        if tweets:
            timeline += tweets
            new_earliest = min(tweets, key=lambda x: x.id).id
            count = count + len(tweets)
            if not tweets or new_earliest == earliest_tweet or count >= (5000 if MAX_COUNT == None else MAX_COUNT):
                return timeline
            else:
                earliest_tweet = new_earliest
                print("getting more tweets before:", earliest_tweet)
        else:
            return timeline
    return timeline


if __name__ == "__main__":
    import glob
    import os
    if not os.path.isdir(PATH):
        print("Path is undefined or does not exist. Please check/configure properly first!")
        exit()
    since_id = 0
    for file in glob.glob(PATH+'tweet*'):  # , reverse=True, key=int):
        id = int(file.replace(PATH+"tweet", "").replace(".md", ""))
        since_id = id if id > since_id else since_id
    print("Latest tweet: " + str(since_id))
    if since_id == 0:
        print("Going back to the very beginning...Make sure you are not going back too far or you may be blocked...comment me out if this is intentional!")
        exit()
    api = twitter.Api(
        CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET
    )
    screen_name = "ILAsoft"
    timeline = get_tweets(api=api, screen_name=screen_name, since_id=since_id)

    for tweet in timeline:
        try:
            id = str(tweet._json["id"])
            f = open(PATH+"tweet" + id + ".md", "x")

            created_at = tweet._json["created_at"]
            #text = tweet._json["text"]
            # text = text.replace(":", "\\x3A").replace("@", "\\x40").replace("#", "\\x3A")
            embedded = api.GetStatusOembed(status_id=id)
            embedded = embedded["html"]
            tags = tweet._json["entities"]["hashtags"]

            f.write("---\ndate: " + created_at +
                    "\ntitle: " + datetime.strptime(created_at,"%a %b %d %H:%M:%S +0000 %Y").strftime("%B %d, %Y") +
                    "\ncomments: false" +
                    # "\nexcerpt: " + text +
                    "\ncategories:\n  - Tweet\n")
            if tags != None and len(tags) > 0:
                f.write("tags:\n")
                for tag in tags:
                    f.write("  - "+tag["text"] + "\n")
            f.write("---\n" + embedded)
            print("Wrote "+id)
        except FileExistsError:
            print("Skipping "+id)
