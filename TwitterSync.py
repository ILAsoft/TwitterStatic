#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import print_function
import os
import json
import sys
import configparser
import requests
from datetime import datetime
import twitter

configfile = configparser.ConfigParser()
CONFIG_PATH = os.path.join(os.path.dirname(
    os.getcwd()), 'TwitterSyncSettings.ini')
try:
    configfile.read(CONFIG_PATH)
    config = configfile['DEFAULT']
    PATH = os.path.join(os.getcwd(), config['PATH'])
    IMGPATH = os.path.join(os.getcwd(), config['IMGPATH'])
    IMGURL = config['IMGURL']
    SCREEN_NAME = config['SCREEN_NAME']

    config = configfile['TWITTER']
    MAX_COUNT = config.getint('MAX_COUNT', 0)
    INCLUDE_RTS = config.getboolean('INCLUDE_RTS')
    CONSUMER_KEY = config['CONSUMER_KEY']
    CONSUMER_SECRET = config['CONSUMER_SECRET']
    ACCESS_TOKEN_KEY = config['ACCESS_TOKEN_KEY']
    ACCESS_TOKEN_SECRET = config['ACCESS_TOKEN_SECRET']
except Exception as e:
    print(e)
    print("Can't read settings! Once installed, use sample from https://github.com/ILAsoft/TwitterStatic/blob/master/TwitterSyncSettings.sample to create TwitterSyncSettings.ini one folder above your site's folder and then run TwitterSync.py from the website's folder itself.")
    exit()

if len(sys.argv) > 1:
    TWEET_ID = int(sys.argv[1])
    MAX_COUNT = 0
    print("Arguments passed - setting max count as 0 and using specific override tweet id: " + str(TWEET_ID))
else:
    TWEET_ID = 0


def parse_tweet_text(id):
    embedded = api.GetStatusOembed(
        status_id=id, omit_script=True, hide_media=False, hide_thread=False)
    print(json.dumps(embedded, indent=4))
    embedded = embedded["html"]
    # embedded = embedded.replace('<script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>',"")
    return embedded


def replace_nitter_href(href):
    # .replace('src="/', 'src="'+IMGURL)
    return href.replace('href="/', 'href="https://nitter.net/')


def parse_nitter_text(id):
    url = 'https://nitter.net/'+SCREEN_NAME+'/status/'+id
    page = requests.get(url)
    page.encoding = 'utf-8'

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(page.text, "html.parser")
    inner_html = soup.select("div.tweet-body")[0]
    # soup.select("a.tweet-avatar")[0].extract()
    soup.select("p.tweet-published")[0].decompose()
    soup.select("div.tweet-stats")[0].decompose()

    for img in inner_html.find_all('img'):
        src = img.get('src')
        if(src != None and src[0] == "/"):
            try:
                print("Checking on " + src)
                imgpath = os.path.join(IMGPATH, os.path.basename(src))
                print("To write to " + imgpath)
                f = open(imgpath, "xb")
                url = 'https://nitter.net' + src
                print("From " + url)
                image = requests.get(url)
                f.write(image.content)
                print("Wrote out " + imgpath)
            except FileExistsError:
                print("Already exists, skipping!")
            img['src'] = IMGURL + os.path.basename(src)

    html = replace_nitter_href(str(inner_html))

    return html


def extract_hash_tags(s):
    import re
    return set(re.sub(r'\W+', '', part[1:]) for part in s.split() if part.startswith('#'))


def parse_nitter_text_hashtags(html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text()
    tags = extract_hash_tags(text)
    return tags


def get_last_saved_tweet():
    import glob
    if not os.path.isdir(PATH):
        print("Path " + PATH +
              " is undefined or does not exist. Please check/configure properly first!")
        exit()
    since_id = 0
    for file in glob.glob(PATH+'tweet*'):  # , reverse=True, key=int):
        try:
            id = int(file.replace(PATH+"tweet", "").replace(".md", ""))
        except:
            continue
        since_id = id if id > since_id else since_id
    print("Latest tweet: " + str(since_id))
    return since_id


def get_hashtags(id):
    tweet = api.GetStatuses(
        status_ids=[id], trim_user=True, include_entities=True)
    return tweet[0]._json["entities"]["hashtags"]


def get_tweets(api=None, screen_name=None, since_id=None):
    count = 0
    timeline = list()
    earliest_tweet = None
    while True:
        print("Since id: " + str(since_id))
        tweets = api.GetUserTimeline(
            screen_name=screen_name,
            max_id=earliest_tweet,
            include_rts=INCLUDE_RTS, trim_user=True,
            since_id=(since_id if (MAX_COUNT == 0) else 0),
            count=(200 if (MAX_COUNT == 0)
                   else MAX_COUNT)
        )
        if tweets:
            timeline += tweets
            new_earliest = min(tweets, key=lambda x: x.id).id
            count = count + len(tweets)
            if not tweets or new_earliest == earliest_tweet or count >= (5000 if MAX_COUNT == 0 else MAX_COUNT):
                return timeline
            else:
                earliest_tweet = new_earliest
                print("getting more tweets before:", earliest_tweet)
        else:
            return timeline
    return timeline


if __name__ == "__main__":
    api = twitter.Api(
        CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN_KEY, ACCESS_TOKEN_SECRET
    )
    if TWEET_ID != None and TWEET_ID > 0:
        timeline = api.GetStatuses(
            status_ids=[TWEET_ID], trim_user=True, include_entities=True)
    else:
        since_id = get_last_saved_tweet()
        if since_id == 0:
            print("Going back to the very beginning...Make sure you are not going back too far or you may be blocked...comment me out if this is intentional!")
            exit()

        timeline = get_tweets(
            api=api, screen_name=SCREEN_NAME, since_id=since_id)
    # print(*timeline)

    for tweet in timeline:
        try:
            id = tweet._json["id_str"]
            # Attempt creating new file - if it fails, we can just skip it
            if(TWEET_ID != None and TWEET_ID > 0):
                f = open(PATH+"tweet" + id + ".md", "w")
            else:
                f = open(PATH+"tweet" + id + ".md", "x")
            created_at = tweet._json["created_at"]
            # text = tweet._json["text"]
            # text = text.replace(":", "\\x3A").replace("@", "\\x40").replace("#", "\\x3A")
            embedded = parse_nitter_text(id)

            tags = list()
            '''tags += tweet._json["entities"]["hashtags"]
            if TWEET_ID != None:
                print(json.dumps(tweet._json, indent=4))
            if ("quoted_status" in tweet._json):
                tags += tweet._json["quoted_status"]["hashtags"]
            if ("retweeted_status" in tweet._json):
                tags += tweet._json["retweeted_status"]["entities"]["hashtags"]
            if ("in_reply_to_status_id" in tweet._json and tweet._json["in_reply_to_status_id"] != None):
                moretags = get_hashtags(tweet._json["in_reply_to_status_id"])
                tags += moretags
            print(type(tags))'''
            moretags = parse_nitter_text_hashtags(embedded)
            tags += moretags
            print(tags)

            f.write("---\ndate: " + created_at +
                    "\ntitle: " + datetime.strptime(created_at, "%a %b %d %H:%M:%S +0000 %Y").strftime("%B %d, %Y") +
                    "\ncomments: false" +
                    # "\nexcerpt: " + text +
                    "\ncategories:\n  - Tweet\n")
            if tags != None and len(tags) > 0:
                f.write("tags:\n")
                for tag in tags:
                    f.write("  - "+tag + "\n")
            f.write("---\n" + embedded)
            '''if ("quoted_status" in tweet._json):
                print("Appending original tweet")
                rt_id = str(tweet._json["quoted_status"]["id_str"])
                rt_embedded = parse_tweet_text(rt_id)
                f.write("\n" + rt_embedded)'''
            print("Wrote "+id)
        except FileExistsError:
            print("Skipping "+id)
