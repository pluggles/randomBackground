#!/usr/bin/python   

import re
import praw
import requests
import os
import glob
import sys
import random
from imgurpython import ImgurClient
from urlparse import urlparse
from os.path import splitext, basename, expanduser

def MakeDir():
    try:
        os.mkdir(subdirectory)
    except Exception:
        pass

def selectSubreddit():
    subreddits = [
        "wallpaper",
        "wallpapers",
        "MinimalWallpaper",
        "wallpaperdump",
        "comicwalls"
        ]
    subreddit = random.choice(subreddits)
    return subreddit

def downloadImage(imageUrl):
    response = requests.get(imageUrl)
    if response.status_code == 200:
        with open(os.path.join(subdirectory, localFileName), 'wb') as fo:
            for chunk in response.iter_content(4096):
                fo.write(chunk)
        #this line changes the background
        cmd = "/usr/bin/gsettings set org.gnome.desktop.background" \
        " picture-uri " \
        "file://" + filepath
        os.system(cmd)

def goToImgur(submission):
    if "imgur.com/" not in submission.url:
        findImage(submissions)
    if submission.score < MIN_SCORE:
        findImage(submissions)
    if 'http://imgur.com/a/' in submission.url:
        newcounter = 0
        albumId = submission.url[len('http://imgur.com/a/'):]
        album = client.get_album_images(albumId)
        
        albumLength = len(album)
        getAlbumRand = random.randint(1,albumLength-1)
        imageUrl = album[getAlbumRand].link
        downloadImage(imageUrl)
                
    elif 'http://i.imgur.com/' in submission.url:
        # The URL is a direct link to the image.
        # using regex here instead of BeautifulSoup because we are pasing
        # a url not html
        mo = imgurUrlPattern.search(submission.url) 

        imgurFilename = mo.group(2)
        if '?' in imgurFilename:
            # The regex doesn't catch a "?" at the end of the filename,
            # so we remove it here.
            imgurFilename = imgurFilename[:imgurFilename.find('?')]

        downloadImage(submission.url)

    elif 'http://imgur.com/' in submission.url:
        # This is an Imgur page with a single image.
        # change the url to redirect to i.imgur link
        url = submission.url
        disassembled = urlparse(url)
        imageId, file_ext = splitext(basename(disassembled.path))
        try:
            image = client.get_image(imageId)
            imageurl = image.link
            submission.url = imageurl
        except ImgurClientError as e:
            sys.exit(0)
        goToImgur(submission)

def findImage(submissions):
    getrand = random.randint(1,subLimit)
    counter = 0
    # Process all the submissions from the front page
    # submissions is a generator so direct addressing is dificult
    for submission in submissions:
        counter += 1
        if counter == getrand:
            goToImgur(submission)
            break

#used for imgur api
api_key_id = 'XXXXXXXXXXXXXXXXX' #get from imgur
api_secret = '#######################################' #get from imgur
#start imgur session
try:
    client = ImgurClient(api_key_id, api_secret)
except ImgurClientError as e:
    sys.exit(0)

targetSubreddit = selectSubreddit()
#dont want any pleb posts
MIN_SCORE = 10
imgurUrlPattern = re.compile(r'(http://i.imgur.com/(.*))(\?.*)?')
home = expanduser("~")
localFileName = 'newBackgroundImage'
subdirectory = home + "/Documents/scripts/backgroundImages"
filepath = subdirectory + "/" + localFileName
# Connect to reddit and download the subreddit front page
subLimit = 500
MakeDir()
try:
    # Note: Be sure to change the user-agent to something unique.
    r = praw.Reddit(user_agent='MAKE YOUR OWN') 
    submissions = r.get_subreddit(targetSubreddit).get_top_from_year(limit=subLimit)
# Or use one of these functions:
#                                       .get_top_from_year(limit=25)
#                                       .get_top_from_month(limit=25)
#                                       .get_top_from_week(limit=25)
#                                       .get_top_from_day(limit=25)
#                                       .get_top_from_hour(limit=25)
#                                       .get_top_from_all(limit=25)
    findImage(submissions)
except Exception:
    sys.exit(0)