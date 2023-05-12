# 🐦 Twitter RSS Feed Checker 

![Python 3](https://img.shields.io/badge/Python-3-blue)
![License](https://img.shields.io/badge/License-MIT-green)

The Twitter RSS Feed Checker is a Python script that automates the process of scanning a list of RSS feeds and looking for tweets in the linked articles. When it finds a tweet, the script writes information about the tweet to a Google Sheets document, including the tweet URL, the URL of the article where the tweet was found, the domain of the website where the article was published, the username of the tweet author, and the date and time the tweet was found.

In addition to scanning for new tweets, the script also scans the same Google Sheets document for tweets that have not yet been replied to. For each of these tweets, the script composes a reply message that includes a link to the article where the tweet was found, and posts the message as a reply to the original tweet.

The script requires a set of credentials to access the Google Sheets document and the Twitter API. These credentials should be placed in a dictionary in the script named `credentials`, and the API keys should be placed in included variables.

### 🇳🇴 Check out a Norwegian implementation:

<a href="https://twitter.com/intent/follow?screen_name=sitertbot">
        <img src="https://img.shields.io/twitter/follow/sitertbot?style=social&logo=twitter"
            alt="follow on Twitter"></a>

## 📋 Requirements

The script requires the following Python packages to be installed:

- tweepy
- gspread
- requests
- feedparser
- google.oauth2
- beautifulsoup4

## ⚙️ Configuration

The script requires a set of credentials to access the Google Sheets document and the Twitter API. These credentials could be placed separately or in the dictionaries in the script named `credentials` as well as variables named `api_key`, `api_secret`, `bearer_token`, `access_token`, and `access_token_secret`.

To generate 3-legged OAuth tokens for your Twitter bot account, follow [this guide](https://medium.com/geekculture/how-to-create-multiple-bots-with-a-single-twitter-developer-account-529eaba6a576), but replace the last step with this curl command in your terminal:

`curl --request POST --url 'https://twitter.com/oauth/access_token?oauth_token=<TOKEN>&oauth_verifier=<PIN>'``

The script also requires a list of RSS feed URLs to scan, which should be placed in a list named `feeds`. The script will also use a dictionary named `display_names` to better display the name/handle of the website in the message sent to Twitter.

## 🚀 Usage

To run the script, simply execute it with Python at a regular schedule. This will populate the Google sheet and send out tweets.
