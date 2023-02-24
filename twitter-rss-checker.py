import os
import time
import tweepy
import gspread
import requests
import feedparser
import google.oauth2
from bs4 import BeautifulSoup
from datetime import datetime
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials

# Dictionary of Google credentials
credentials = {
  "type": "service_account",
  "project_id": "name of your project",
  "private_key_id": "your private key id",
  "private_key": "-----BEGIN PRIVATE KEY-----your private key-----END PRIVATE KEY-----\n",
  "client_email": "example@projectid.iam.gserviceaccount.com",
  "client_id": "your client id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/example%40yourprojectname.iam.gserviceaccount.com"
}

# Credentials for accessing the Twitter API
api_key= "API key or consumer key to account that will access API"
api_secret= "API secret key or consumer secret key to account that will access API"
bearer_token= "bearer token to account that will access API"
access_token= "access token to account that will tweet"
access_token_secret= "access token secret to account that will tweet"

# List of RSS feed URLs to scan
feeds = [
    'https://www.vg.no/rss/feed',
    'https://www.dagbladet.no/?lab_viewport=rss',
    'https://www.nrk.no/nyheter/siste.rss',
    'https://www.aftenposten.no/rss/',
    'https://www.tv2.no/rest/cms-feeds-dw-rest/v2/cms/article/nyheter',
    'https://services.dn.no/api/feed/rss/',
    'https://www.nettavisen.no/service/rich-rss',
    'https://www.dagsavisen.no/rss',
    'https://www.tek.no/api/rss/rss2/medium/collections',
    'https://ws.finansavisen.no/api/articles.rss',
    'https://dinside.dagbladet.no/data/?lab_viewport=rss',
    'https://www.seher.no/rss/',
    'https://e24.no/rss',
    'https://www.eurosport.no/rss.xml',
    'https://www.abcnyheter.no/api/article.rss?category=nyheter',
    'https://aftenbladet.no/rss',
    'https://bt.no/rss',
    'https://www.nationen.no/?feed=tunrss',
]

# Dictionary of website names
display_names = {
    "www.vg.no": "VG",
    "www.dagbladet.no": "Dagbladet",
    "www.nrk.no": "NRK",
    "www.aftenposten.no": "Aftenposten",
    "www.tv2.no": "TV 2",
    "www.dn.no": "Dagens Næringsliv",
    "www.nettavisen.no": "Nettavisen",
    "www.dagsavisen.no": "Dagsavisen",
    "www.tek.no": "Tek.no (VG)",
    "www.finansavisen.no": "Finansavisen",
    "dinside.dagbladet.no": "DinSide (Dagbladet)",
    "www.seher.no": "Se & Hør",
    "www.e24.no": "E24",
    "www.eurosport.no": "Eurosport Norge",
    "www.abcnyheter.no": "ABC Nyheter",
    "www.aftenbladet.no": "Aftenbladet",
    "www.bt.no": "Bergens Tidende",
    "www.nationen.no": "Nationen"
}

# Authorize and access the Google Sheet (remember to give Google service account access, i.e. "example@iam.gserviceaccount.com")
gc = gspread.service_account_from_dict(credentials)
sheet_link = "link to Google spreadsheet"
sh = gc.open_by_url(sheet_link)
worksheet = sh.sheet1

# Function to check for tweets in HTML
def check_for_tweets(html):
    soup = BeautifulSoup(html, 'html.parser')
    tweets = []
    for a in soup.find_all('a', href=True):
        if '/status/' in a['href']:
            tweets.append(a['href'])
    return tweets

# Function to write to Google Sheets
def write_to_google_sheets(tweet, url, domain, current_date, current_time, username):
    row = [current_date, current_time, domain, username, url, tweet]
    # Check for duplicates
    for i, existing_row in enumerate(worksheet.get_all_values()):
        if i == 0:  # skip header row
            continue
        if existing_row[4] == row[4] and existing_row[5] == row[5]:
            print(f'Skipping duplicate row: {row}')
            return
    # Add new row to worksheet
    worksheet.append_row(row)
    print(f'New tweet found: {tweet}')

# Sets to keep track of already processed tweets and urls
processed_tweets = set()
processed_urls = set()

# Loop through RSS feeds
for feed_url in feeds:
    print(f'Scanning feed: {feed_url}')
    feed = feedparser.parse(feed_url)
    for entry in feed.entries:
        url = entry.link
        domain = url.split('//')[-1].split('/')[0]
        print(f'Checking url: {url}')

        # Skip if URL has already been processed or if any exception are listed
        if url in processed_urls or url.startswith('https://www.dagbladet.no/studio/'):
            continue
        processed_urls.add(url)
        # Get HTML from URL
        try:
            response = requests.get(url)
            response.raise_for_status()
            html = response.text
        except requests.exceptions.RequestException as e:
            print("Error: ", e)

        # Check for tweets in HTML
        tweets = check_for_tweets(html)
        # Write tweets to Google Sheets
        for tweet in tweets:
            # Skip if tweet has already been processed
            if tweet in processed_tweets:
                continue
            processed_tweets.add(tweet)
            now = datetime.now()
            current_date = now.strftime("%Y-%m-%d")
            current_time = now.strftime("%H:%M:%S")
            username = tweet.split("/")[-3]
            write_to_google_sheets(tweet, url, domain, current_date, current_time, username)

print(f'Finished scanning {len(processed_urls)} URLs, found {len(processed_tweets)} new tweets.')

print(f'Continuing script...')

# Set up the headers for the Twitter API
headers = {"Authorization": f"Bearer {bearer_token}"}

# Create an OAuth2BearerHandler object
auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)

# Create an API object with the OAuth2BearerHandler as the authentication handler
api = tweepy.API(auth)

# Check if we can connect to the Twitter API
print('Starting Twitter authentication...')
try:
    api.verify_credentials()
    print("Authentication successful")
except tweepy.TweepyException as e:
    print("Error during authentication")
    print(e)

# Define the message to send as a reply to new tweets
message = 'Your tweet was cited in this article {webpage_url}'

# Check the Google Sheet for new tweets and reply to them
print('Scanning Google sheet for unreplied tweets and tweeting them')
while True:
    for i, row in enumerate(worksheet.get_all_values()[1:], start=2):
        _, _, domain, _, webpage_url, tweet_url, replied, _ = row
        if not tweet_url.startswith('https://twitter.com/'):
            continue
        if replied.lower() == 'yes':
            continue
        tweet_id = tweet_url.split('/')[-1].split('?')[0]
        try:
            response = requests.get(f'https://api.twitter.com/1.1/statuses/show.json?id={tweet_id}', headers=headers)
            if response.status_code != 200:
                print(f'Could not find tweet {tweet_id}')
                continue
            tweet = response.json()
            print(f'Found tweet {tweet_id}')
        except requests.exceptions.RequestException:
            print(f'Could not find tweet {tweet_id}')
            continue
        if 'in_reply_to_user_id' in tweet and tweet['in_reply_to_user_id'] is not None:
            continue
        display_name = display_names.get(domain)
        reply_text = message.format(webpage_url=webpage_url)
        reply_text = reply_text.replace('article', f'article from {display_name}')
        try:
            response = api.update_status(status=reply_text, in_reply_to_status_id=tweet['id'], auto_populate_reply_metadata=True)
            if response:
                print(f'Replied to tweet {tweet_id} with message: {reply_text}')
                worksheet.update_cell(i, 8, time.strftime('%Y-%m-%d %H:%M:%S'))
                worksheet.update_cell(i, 7, 'Yes') # Update the "replied" flag
        except tweepy.TweepyException as e:
            print(f'Error replying to tweet {tweet_id}: {e}')
    print('Finished checking for new tweets and replying to them.')

print('Script finished running.')