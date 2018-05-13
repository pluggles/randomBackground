#!/usr/bin/python
"""Summary
A python script to query reddit for images and set
an ubuntu desktop background image

Attributes:
    API_KEY_ID (str): Description
    API_SECRET (str): Description
    DEBUG_FILE (TYPE): Description
    HOME (TYPE): Description
    IMGURURLPATTERN (TYPE): Description
    LOCALFILENAME (str): Description
    MIN_SCORE (int): Description
    REDDITURLPATTERN (TYPE): Description
    SUBDIRECTORY (TYPE): Description
    SUBLIMIT (int): Description
"""
import os
from os.path import splitext, basename, expanduser
from urlparse import urlparse
import re
import time
import sys
import random
import argparse
import logging
from imgurpython import ImgurClient
from imgurpython.helpers.error import ImgurClientError
import praw
import requests

### Change these to fit your needs ######
#imgur
API_KEY_ID = '###############'
API_SECRET = '##############################'
LOCALFILENAME = 'newBackgroundImage'
HOME = expanduser("~")
SUBDIRECTORY = HOME + "/Documents/scripts/backgroundImages"
MIN_SCORE = 10
SUBLIMIT = 500
IMGURURLPATTERN = re.compile(r'(http[s]?://i.imgur.com/(.*))(\?.*)?')
REDDITURLPATTERN = re.compile(r'http[s]?://i.redd.it/.*\.(jpg|JPG||png|PNG)$')
DEBUG_FILE = HOME + "/Documents/scripts/log.txt"

def save_last_image():
    """Summary
    Renames the last image pulled in from 'newBackgroundImage'
    to a timestamp name
    """
    logging.debug("Enter::save_last_image")
    try:
        os.rename(os.path.join(SUBDIRECTORY, LOCALFILENAME),
                  os.path.join(SUBDIRECTORY, time.strftime("%Y%m%d-%H%M%S")))
    except OSError:
        logging.debug("previous image does not exist, no worries continuing")
def make_dir(sub_dir):
    """Summary
    Creates a directory to store the background images
    Args:
        subDir (str): The path to a direcotry you want to make
    """
    logging.debug("Enter::make_dir")
    try:
        if not os.path.exists(sub_dir):
            os.makedirs(sub_dir)
    except OSError as error:
        print "Error making " + sub_dir
        print error
        print "continuing though..."
def select_subreddit():
    """Summary
    Randomly selects a subreddit to try and pull an image from
    Returns:
        str: a name of a subreddit
    """
    logging.debug("Enter::select_subreddit")
    subreddits = [
        "wallpaper",
        "wallpapers",
        "MinimalWallpaper",
        "wallpaperdump",
        "comicwalls"
        ]
    subreddit = random.choice(subreddits)
    return subreddit
def download_image(image_url):
    """Summary
    Downloads an image from a direct url
    Args:
        imageUrl (str): Url of an Image
    """
    try:
        logging.debug("Enter::download_image")
        logging.debug("Geting image %s", image_url)
        response = requests.get(image_url)
        if response.status_code == 200:
            with open(os.path.join(SUBDIRECTORY, LOCALFILENAME), 'wb') as file_open:
                for chunk in response.iter_content(4096):
                    file_open.write(chunk)
            #this line changes the background
            set_background(FILEPATH)
    except requests.exceptions.RequestException as error:
        print "Error occured in download_image"
        print error
        print "exiting"
    except IOError as error:
        logging.debug("Error occured writing image...probably")
def set_background(filepath):
    """Summary
    changes the backgound on a gnome desktop
    Args:
        filepath (str): The full filepath to a file you want to set as a background image
    """
    try:
        logging.debug("Enter::set_background")
        cmd = "/usr/bin/gsettings set org.gnome.desktop.background" \
            " picture-uri " \
            "file://" + filepath
        #scale = "gsettings set org.gnome.desktop.background picture-options \"scaled\""
        os.system(cmd)
    except OSError:
        logging.debug("Error occured setting the background image")
def go_to_imgur(submission):
    """Summary
    Gets a reddit submission post, and attempts to find the linked image
    If it is an image hosted on reddit, or the direct image on
    imgur we can pull it directly
    It the post is an imgur album we attempt to randomly get an
    image from the album
    If the image is on a page in imgur we need to get the direct image url
    if the image is not from reddit or imgur we try another post
    Args:
        submission (Submission): A specific reddit post
    """
    #try:
    logging.debug("Enter::go_to_imgur")
    logging.info("the URL was %s", submission.url)
    if re.match(REDDITURLPATTERN, submission.url):
        download_image(submission.url)
    elif "imgur.com/" not in submission.url:
        logging.debug("submission link not from reddit or imgur finding a new one")
        find_image(SUBMISSIONS)
    elif submission.score < MIN_SCORE:
        logging.debug("Found reddit post is not worthy of being downloaded")
        find_image(SUBMISSIONS)
    elif 'imgur.com/a/' in submission.url:
        logging.debug("Selecting rand image from imgur album")
        get_link_from_album(submission)
    elif 'imgur.com/gallery' in submission.url:
        logging.debug("Selecting rand image from imgur gallery")
        get_link_from_gallery(submission)
    elif 'i.imgur.com/' in submission.url:
        logging.debug("Direct imgur image found")
        url_parts = IMGURURLPATTERN.search(submission.url)
        imgur_filename = url_parts.group(2)
        if '?' in imgur_filename:
            # The regex doesn't catch a "?" at the end of the filename,
            # so we remove it here.
            imgur_filename = imgur_filename[:imgur_filename.find('?')]
        download_image(submission.url)
    elif 'imgur.com/' in submission.url:
        logging.debug("Found single image on imgur page, lets get the direct link")
        get_direct_imgur_link(submission.url)
    #except Exception as error:
    #    #print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(error).__name__, error)
    #    os.execv(sys.executable, ['python'] + sys.argv)
    #    sys.exit(0)
def get_link_from_album(submission):
    """Summary
    Gets a direct image url from an album of images
    Args:
        submission (Submission): a reddit submission
    """
    try:
        submission.url = clean_url(submission.url)
        album_id = submission.url[len('https://imgur.com/a/'):]
        album = CLIENT.get_album_images(album_id)
        album_length = len(album)
        if album_length == 0:
            logging.debug("This particular album is empty")
            os.execv(sys.executable, ['python'] + sys.argv)
            sys.exit(0)
        get_album_rand = random.randint(1, album_length-1)
        image_url = album[get_album_rand].link
        download_image(image_url)
    except ImgurClientError as error:
        print error
        os.execv(sys.executable, ['python'] + sys.argv)
        sys.exit(0)
    except OSError as error:
        os.execv(sys.executable, ['python'] + sys.argv)
        sys.exit(0)
def get_link_from_gallery(submission):
    """Summary
    Gets a direct image url from a gallery of images
    Args:
        submission (Subission): A reddit submission
    """
    try:
        submission.url = clean_url(submission.url)
        album_id = submission.url[len('https://imgur.com/gallery/'):]
        album = CLIENT.get_album_images(album_id)
        album_length = len(album)
        if album_length == 0:
            logging.debug("This particular album is empty")
            os.execv(sys.executable, ['python'] + sys.argv)
            sys.exit(0)
        get_album_rand = random.randint(1, album_length-1)
        image_url = album[get_album_rand].link
        download_image(image_url)
    except ImgurClientError:
        os.execv(sys.executable, ['python'] + sys.argv)
        sys.exit(0)
    except OSError:
        os.execv(sys.executable, ['python'] + sys.argv)
        sys.exit(0)
def clean_url(url):
    """cleans up and standardizes an imgur url
    Args:
        url (TYPE): Description
    Returns:
        string: A cleaned up URL
    """
    if url.startswith("http://"):
        url = url.replace('http://', 'https://', 1)
    if url.endswith("?gallery"):
        url = url.replace('?gallery', '')
    if url.endswith("#0"):
        url = url.replace('#0', '')
    return url
def get_direct_imgur_link(url):
    """Summary
    Expects ann imgur page with a single image on it
    Extracts the direct img url
    Args:
        url (str): imgur url page with an image
    """
    disassembled = urlparse(url)
    image_id = splitext(basename(disassembled.path))[0]
    try:
        image = CLIENT.get_image(image_id)
        imageurl = image.link # pylint: disable=maybe-no-member
        download_image(imageurl)
    except ImgurClientError:
        logging.debug("error occured, probably a 404 restarting")
        os.execv(sys.executable, ['python'] + sys.argv)
        sys.exit(0)
def find_image(submissions):
    """Summary
    randomely selects a post from a previsouly selected subreddit
    Args:
        submissions (Submission): A reddit post
    """
    logging.debug("Enter::find_image")
    get_rand = random.randint(1, SUBLIMIT)
    logging.debug("COUNT is: %d", get_rand)
    counter = 0
    # Process all the submissions from the front page
    # submissions is a generator so direct addressing is a bit tough
    for submission in submissions:
        counter += 1
        if counter == get_rand:
            logging.debug("Found a submission")
            go_to_imgur(submission)
            break
def establish_reddit_connection():
    """Summary
    create the reddit connection
    Returns:
        Reddit : Description
    """
    #client_id = 'callmederpGetWallpaper'
    try:
        reddit_app_key = '##############'
        reddit_app_secret = '########################'
        # Note: Be sure to change the user-agent to something unique.
        reddit_user_agent = 'SOME UNIQUE USER AGENT'
        reddit_connection = praw.Reddit(user_agent=reddit_user_agent, client_id=reddit_app_key,
                                        client_secret=reddit_app_secret)
        return reddit_connection
    except praw.exceptions.PRAWException:
        logging.debug("Error occured trying to create a reddit connection")
if __name__ == '__main__':
    PARSER = argparse.ArgumentParser(
        description='A script to set a random background'
        )
    PARSER.add_argument("-d", "--debug", help="increase output verbosity",
                        action="store_true")

    ARGS = PARSER.parse_args()
    if ARGS.debug:
        logging.basicConfig(filename=DEBUG_FILE, level=logging.DEBUG)
   #start imgur session
    logging.info("#################Start of run###########################")
    try:
        logging.debug("Trying to connect to Imgur")
        CLIENT = ImgurClient(API_KEY_ID, API_SECRET)
        logging.info("Imgur connection established")
        logging.debug("Trying to connect to reddit")
        REDDIT = establish_reddit_connection()
        logging.info("Reddit connection established")
    except ImgurClientError as error:
        logging.debug("Exiting due to ImgurClient Error")
        sys.exit(0)
    TARGETSUBREDDIT = select_subreddit()
    FILEPATH = SUBDIRECTORY + "/" + LOCALFILENAME
    make_dir(SUBDIRECTORY)
    try:
        logging.debug("getting submissions")
        SUBMISSIONS = REDDIT.subreddit(TARGETSUBREDDIT).top('all', limit=SUBLIMIT)
        save_last_image()
        find_image(SUBMISSIONS)
    except praw.exceptions.PRAWException as ex:
        print "error:", sys.exc_info()[0]
        print ex
        sys.exit(0)
        