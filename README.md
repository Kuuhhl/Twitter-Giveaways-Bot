# Twitter Giveaways Bot

A bot that will constantly look for new *giveaways* and *contests* on **Twitter**; and enter to *all* of them!
It will do whatever it's needed, either retweeting or liking something, or even following and DMing someone :D

Limits are pretty high; the bot can enter to more than **1000 giveaways per day**, so it's likely that you'll win several giveaways :)

## What's new in my fork? 😃
* Pull tweets from timeline
* require words (only participate if it contains certain words)
* auto-reply if it is a requirement
* tag friends if it is a requirement

## Getting Started

These instructions will get your bot started in minutes.

### Prerequisites

Things you need to have installed in order to be able to run the script.

```
Python 3.x
python-twitter
```

### Installing

First of all, if you don't already have Python in your system, [download](https://www.python.org/downloads/) and install it now. Once that's done, for the 
script to be able to work with Twitter you'll need to install its API

```
pip install python-twitter
```
You should also download both scripts: ``main.py`` and ``config.py``. Preferably, put them in the same folder.

Once there, open the ``config.py`` file with a text editor; don't run it!
This file has all the variables the main script will use. Give each one of them the values you want, or just leave them by default.

However, you do need to change the first variable: ``twitter_credentials``. As it contains all the credentials related to the Twitter API; 
they can't stay blank (what's by default) if you want the bot to connect to Twitter.

#### Twitter App
This is meant to be a short guide on how to get the twitter credentials your bot will need. Here I assume you already have Twitter account, if you don't please make one now. 
##### Steps: 
* Enter to [Twitter Apps](https://apps.twitter.com/) and click the `Create New App` button
* Fill out all details and create the app
* Enter to the ``Keys and Access Token`` section and create a new access token. 
* Now copy ``Consumer Key``, ``Consumer Secret``, ``Access Token``, ``Access Token Secret`` and paste them into their right place inside
the ``config.py``'s ``twitter_credentials`` variable.

If you've followed the steps correctly, now to start the bot you just need to run the ``main.py`` script. **Experiment with the variables at your own risk.**

## Disclaimer
The bot is currently not functional and has a lot of bugs. Once I feel it is stable enough, I will remove this disclaimer.

This is entirely for educational purpose. Use at your own risk and responsibility, there's a possibility that your Twitter account gets banned. I hold no liability for what you use the bot for or the consequences.

