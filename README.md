# randomBackground
Finds an image link from multiple reddit wallpaper subreddits, downloads the image and sets it as a wallpaper

#Needed packages (installed through pip)
imgurpython 

praw

urlparse

pyopenssl 

ndg-httpsclient

pyasn1

#Using the Script
You will need to set up an Imgur api key:
http://api.imgur.com/

once you get your client ID and client secret put them in the script for their respective api_key_id and api_secret variables

You will need to do something similar for the reddit connection as well:
https://github.com/reddit-archive/reddit/wiki/OAuth2-Quick-Start-Example#first-steps

You can add and remove any subreddits you want to get images from in the selectSubreddit() function.

The script will make a directory to store the current image to use as a wallpaper, you can chage that location by changing the subdirectory variable. 

The filename of the image can also be changed by changing the localFileName variable.

The subLimit varible is used to select from the first X amount of submissions from the subreddit
