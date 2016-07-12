#!/usr/bin/python   

import re
import praw
import requests
import os
import sys
import random
import argparse
import logging
from imgurpython import ImgurClient
from urlparse import urlparse
from os.path import splitext, basename, expanduser

### Change these to fit your needs ######
api_key_id = '#################'
api_secret = '###############################'
localFileName = 'newBackgroundImage'
home = expanduser("~")
subdirectory = home + "/Documents/scripts/backgroundImages"
MIN_SCORE = 10
subLimit = 500
reddit_user_agent = '##################'
debug_file = home + "/Documents/scripts/log.txt"

def saveLastImage():
    try:
        os.rename(os.path.join(subdirectory, localFileName), os.path.join(subdirectory,localFileName + "-old"))
    except Exception:
        pass

def MakeDir(subDir):
    try:
        os.makedirs(subDir)
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
   
    logging.info("the URL was %s" % submission.url)
    if "imgur.com/" not in submission.url:
        findImage(submissions)
        logging.debug("In first if")
    if submission.score < MIN_SCORE:
        logging.debug("In 2nd if")
        findImage(submissions)
    if 'imgur.com/a/' in submission.url:
        logging.debug("In 3rd if")
        albumId = submission.url[len('http://imgur.com/a/'):]
        album = client.get_album_images(albumId)
        
        albumLength = len(album)
        getAlbumRand = random.randint(1,albumLength-1)
        imageUrl = album[getAlbumRand].link
        downloadImage(imageUrl)
                
    elif 'i.imgur.com/' in submission.url:
        logging.debug("In first elif")
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

    elif 'imgur.com/' in submission.url:
        logging.debug("In 2nd elif")
        # This is an Imgur page with a single image.
        # change the url to redirect to i.imgur link
        url = submission.url
        disassembled = urlparse(url)
        imageId, file_ext = splitext(basename(disassembled.path))
        try:
            image = client.get_image(imageId)
            imageurl = image.link
            submission.url = imageurl
            logging.debug("imageurl is %s" % imageurl)
        #    downloadImage(imageUrl)
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

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
    description='A test script for http://stackoverflow.com/q/14097061/78845'
        )
    parser.add_argument("-d", "--debug", help="increase output verbosity",
        action="store_true")

    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(filename=debug_file, level=logging.DEBUG)
   #start imgur session
    logging.info("Start of run")
    try:
        client = ImgurClient(api_key_id, api_secret)
    except ImgurClientError as e:
        sys.exit(0)

    targetSubreddit = selectSubreddit()  
    imgurUrlPattern = re.compile(r'(http://i.imgur.com/(.*))(\?.*)?')
    filepath = subdirectory + "/" + localFileName
    MakeDir(subdirectory)
    try:
        # Note: Be sure to change the user-agent to something unique.
        r = praw.Reddit(user_agent=reddit_user_agent) 
        submissions = r.get_subreddit(targetSubreddit).get_top_from_year(limit=subLimit)
    # Or use one of these functions:
    #                                       .get_top_from_year(limit=25)
    #                                       .get_top_from_month(limit=25)
    #                                       .get_top_from_week(limit=25)
    #                                       .get_top_from_day(limit=25)
    #                                       .get_top_from_hour(limit=25)
    #                                       .get_top_from_all(limit=25)
        saveLastImage()
        findImage(submissions)
    except Exception:
        sys.exit(0)