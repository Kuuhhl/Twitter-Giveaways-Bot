import config
import twitter
import time
from datetime import datetime, timezone
import random
from random import shuffle
import re
import tqdm
import json
import string


class colors:
    HEADER = "\033[95m" if config.print_in_color else ""
    OKBLUE = "\033[94m" if config.print_in_color else ""
    OKGREEN = "\033[92m" if config.print_in_color else ""
    WARNING = "\033[93m" if config.print_in_color else ""
    FAIL = "\033[91m" if config.print_in_color else ""
    ENDC = "\033[0m" if config.print_in_color else ""
    BOLD = "\033[1m" if config.print_in_color else ""
    UNDERLINE = "\033[4m" if config.print_in_color else ""


print(colors.HEADER + "Remember you can change the settings in config.py!")
# All variables related to the Twitter API
twitter_api = twitter.Api(
    consumer_key=config.twitter_credentials["consumer_key"],
    consumer_secret=config.twitter_credentials["consumer_secret"],
    access_token_key=config.twitter_credentials["access_token"],
    access_token_secret=config.twitter_credentials["access_secret"],
    sleep_on_rate_limit=True,
)

screen_name = twitter_api.VerifyCredentials().screen_name

friends = []

while len(friends) is not twitter_api.GetUser(screen_name=screen_name).friends_count:
    try:
        f = twitter_api.GetFriends(screen_name=screen_name)
        friends = [x.screen_name for x in f]
        print(colors.OKGREEN + "Friends retrieved successfully!")
        break
    except Exception as e:
        # Friends couldn't be retrieved
        print(colors.FAIL + colors.BOLD + str(e) + colors.ENDC)
        print(
            colors.FAIL
            + colors.BOLD
            + "Couldn't retrieve friends. The bot won't unfollow someone random when we start"
            " following someone else. So your account might reach the limit (following 2000"
            " users)" + colors.ENDC
        )
        if config.wait_retrieve is False:
            break
        time.sleep(600)


def check():
    print(
        colors.OKGREEN
        + "Started Analyzing ("
        + str(time.gmtime().tm_hour)
        + ":"
        + str(time.gmtime().tm_min)
        + ":"
        + str(time.gmtime().tm_sec)
        + ")"
    )
    print()
    # Retrieving the last 1000 tweets for each tag and appends them into a list
    just_retweet_streak = 0

    searched_tweets = []
    for x in config.search_tags:
        searched_tweets += twitter_api.GetSearch(term=x, count="1")

    #  Also search timeline (followed users)
    for tweet in twitter_api.GetHomeTimeline(
        count="1",
        exclude_replies=True,
        contributor_details=True,
        include_entities=True,
    ):
        for searchTag in config.search_tags:
            if searchTag in tweet.text:
                searched_tweets.append(tweet)
    for tweet in searched_tweets:
        print(tweet.text)
        print()
    exit()
    for tweet in tqdm.tqdm(searched_tweets, total=len(searched_tweets)):
        time.sleep(1)
        # In this section, we first find out some info
        # about the tweet that we need
        # to accurately process it.

        # We convert the tweet to lowercase for easier parsing.
        tweet.text = tweet.text.lower()
        # Then, we remove punctuation aswell.
        tweet.text = tweet.text.translate(str.maketrans("", "", string.punctuation))

        # If set, we check for mandatory words.
        # Tweets that don't contain them will be skipped.
        if config.useMandatoryWords == True:
            for word in config.MandatoryWords:
                if word in tweet.text:
                    found = True
            if found != True:
                continue

        # get tweet publish date
        tweet_date = datetime.strptime(tweet.created_at, "%a %b %d %H:%M:%S %z %Y")
        # get current date and time
        now = datetime.now(timezone.utc)
        difference = now - tweet_date

        # check if tweet contains any of the words in BadList
        Bad = False
        for BadWord in config.BadList:
            if BadWord in tweet.text:
                Bad = True
                break

        # check if we have to reply with friend tags
        Tag = False
        numberOfTags = None
        for TagWord in config.TagWordsList:
            # Try to find the tag word.
            # If not found, try the next
            try:
                index = tweet.text.split(" ").index(TagWord)
            except ValueError:
                continue

            # This section only gets executed if the TagWord was found.
            Tag = True

            # Here, we check for any numbers, etc.
            # to find out how many friends to mention.

            # Example string: Tag 5 friends
            # Gets number from after the TagWord
            if type(tweet.text.split(" ")[index + 1]) == int:
                numberOfTags = tweet.text.split(" ")[index + 1]
                break

            # Example string: Tag a friend
            # Recognizes "a" and "one" from after the TagWord > one friend
            elif (
                tweet.text.split(" ")[index + 1] == "a"
                or "one" in tweet.text.split(" ")[index + 1]
            ):
                numberOfTags = 1
                break
            # Example string: Tag friends
            # Tries matching the multiple friend indicators from the list
            # If it succeeds, it will default to 3 people.
            for friendsWord in config.friendsWordsList:
                if friendsWord in tweet.text:
                    numberOfTags = 3
                    break

            # Example string: Tag friend
            # Is assigned 1 as default value if the other checks were negative.
            if numberOfTags == None:
                numberOfTags = 1

        # Check to see if we have to reply
        replyString = None
        # for this, we iterate over all the defined indicators.
        for replyComment in config.replyCommentsList:
            # Then iterate over the tweet's text lines
            for tweetLine in tweet.text.splitlines():
                # Here, we try to find out
                # if and where the tags exist
                # in the tweet's text-line
                try:
                    index = tweetLine.split(" ").index(replyComment)
                except ValueError:
                    continue

                # This only gets executed if the indicator was found.

                # We try to find text wrapped in quotes,
                # as it is very likely
                # to be the text we need to reply.
                # Example: Reply "done" (where 'done' is wrapped in quotes.)
                # First, we try with double quotes. > ("text")
                inQuotes = re.search('"([^"]*)"', tweetLine)
                # Then, we try with single quotes. > ('text')
                if inQuotes == None:
                    inQuotes = re.search("'([^']*)'", tweetLine)

                # If we can find a string in quotes, we
                # use it as our reply string
                if inQuotes != None:
                    replyString = inQuotes
                    break

                # If we can't find a string in quotes, we
                # search for the word using the 'with'-indicator.
                # That means, we simply take the word after 'with'.
                # Example: Reply with text
                # (where 'text' is the word after 'with'.)
                else:
                    # For this, we iterate over the list
                    # of words we can parse as 'with'.
                    for withWord in config.withWordsList:
                        # If we find it, we set the word after the 'with' as our reply string.
                        try:
                            if tweetLine.split(" ")[index + 1] == withWord:
                                replyString = "".join(tweetLine.split(" ")[index + 2])
                                break
                        except IndexError:
                            replyString = None
                            break
                    # If we didn't find a string, we just use
                    # the word after 'reply'
                    if replyString == None:
                        try:
                            # Comment word after 'reply'
                            replyString = "".join(tweetLine.split(" ")[index + 1])
                        except:
                            # we use 'done' as the fallback reply.
                            replyString = "done"
                        break

        # Here, is the part where we have the info and just do the actions.
        # We will only retweet if tweet has a minumum number of retweets
        # and is not over the set age-limit.
        if (
            tweet.retweet_count >= config.minimumRetweets
            and difference.days <= config.MaximumDays
        ):
            if not (Bad):  # if tweet doesn't contain bad words
                # The script only cares about contests that require retweeting.
                if any(x in tweet.text.split() for x in config.retweet_tags):
                    # This clause checks if the text contains any retweet_tags
                    if tweet.retweeted_status is not None:
                        # In case it is a retweet, we switch to the original one
                        if any(
                            x in tweet.retweeted_status.text.split()
                            for x in config.retweet_tags
                        ):
                            tweet = tweet.retweeted_status
                        else:
                            continue
                    if tweet.user.screen_name.lower() in config.banned_users or any(
                        x in tweet.user.name for x in config.banned_name_keywords
                    ):
                        # If it's the original one, we check if the author is banned
                        continue

                    try:
                        # RETWEET
                        # This is ran under a try clause because there's always an error when trying to retweet something
                        # already retweeted. So if that's the case, the except is called and we skip this tweet
                        # If the tweet wasn't retweeted before, we retweet it and check for other stuff
                        twitter_api.PostRetweet(status_id=tweet.id)
                        just_retweet_streak += 1

                        # REPLY with tags we need to
                        if Tag:
                            friendTagsList = config.friendTagsList
                            # Share with random retweeters if not enough tags specified.
                            if numberOfTags > len(config.friendTagsList):
                                try:
                                    userIds = twitter_api.GetRetweeters(
                                        tweet.id,
                                        count=numberOfTags - len(config.friendTagsList),
                                        stringify_ids=True,
                                    )
                                    for userId in userIds:
                                        config.friendTagsList.append(
                                            "@"
                                            + str(
                                                twitter_api.GetUser(
                                                    user_id=userId
                                                ).screen_name
                                            )
                                        )
                                except:
                                    # If it doesn't work, just tag less
                                    pass
                            # Try posting reply until it works.
                            # Twitter doesn't allow you to post the same tweet too often,
                            # so we just shuffle the order of tags each time it doesn't work.
                            while True:
                                # shuffles the order of our tags to keep it more random
                                shuffle(friendTagsList)
                                # Creates a string with the number of tags needed
                                tagsString = " ".join(friendTagsList[0:numberOfTags])
                                # Try-catch for the Twitter-Error (too many similar replies)
                                try:
                                    # Post reply with tags
                                    twitter_api.PostUpdate(
                                        tagsString,
                                        in_reply_to_status_id=tweet.id,
                                        auto_populate_reply_metadata=True,
                                    )
                                except Exception as e:
                                    # Wait a bit before trying again
                                    time.sleep(5)
                                    continue
                                break
                        # Gets executed if we have to reply something
                        if replyString != None:
                            # Here, we have a loop to try posting again if it
                            # didn't work for some reason.
                            while True:
                                try:
                                    # Post reply
                                    twitter_api.PostUpdate(
                                        replyString,
                                        in_reply_to_status_id=tweet.id,
                                        auto_populate_reply_metadata=True,
                                    )
                                except twitter.error.TwitterError as error:
                                    if json.loads(error)[0]["code"] == 187:
                                        replyString += "🍀"
                                        time.sleep(5)
                                        continue
                                    else:
                                        raise
                        # MESSAGE
                        try:
                            # So we don't skip the tweet if we get the "You cannot send messages to users who are not following you." error
                            if config.use_msgs is True and any(
                                x in tweet.text for x in config.message_tags
                            ):
                                # If the tweet contains any of the message_tags, we send a DM to the author with a random
                                # sentence from the message_text list
                                twitter_api.PostDirectMessage(
                                    text=config.message_text[
                                        random.randint(0, len(config.message_text) - 1)
                                    ],
                                    screen_name=tweet.user.screen_name,
                                )
                                just_retweet_streak = 0
                                # 1 every 86.4s guarantees we won't pass the 1000 DM per day limit
                                # time.sleep(config.msg_rate)
                        except:
                            pass

                        # FOLLOW
                        if any(x in tweet.text for x in config.follow_tags):
                            # If the tweet contains any follow_tags, it automatically follows all the users mentioned in the
                            # tweet (if there's any) + the author
                            addFriends = []
                            friends_count = twitter_api.GetUser(
                                screen_name=screen_name
                            ).friends_count
                            if tweet.user.screen_name not in friends:
                                twitter_api.CreateFriendship(
                                    screen_name=tweet.user.screen_name
                                )
                                addFriends.append(tweet.user.screen_name)
                                just_retweet_streak = 0
                                # time.sleep(config.follow_rate)

                            for name in tweet.user_mentions:
                                if (
                                    name.screen_name in friends
                                    or name.screen_name in addFriends
                                ):
                                    continue
                                twitter_api.CreateFriendship(
                                    screen_name=name.screen_name
                                )
                                addFriends.append(name.screen_name)
                                just_retweet_streak = 0
                                # time.sleep(config.retweet_rate)
                            # Twitter sets a limit of not following more than 2k people in total (varies depending on followers)
                            # So every time the bot follows a new user, its deletes the first one
                            if friends_count >= 2000:
                                while (
                                    friends_count
                                    < twitter_api.GetUser(
                                        screen_name=screen_name
                                    ).friends_count
                                ):
                                    try:
                                        x = friends[0]
                                        twitter_api.DestroyFriendship(screen_name=x)
                                        friends.remove(x)
                                    except Exception as e:
                                        print(e)
                            friends.extend(addFriends)
                        # LIKE
                        try:
                            # So we don't skip the tweet if we get the "You have already favorited this status." error
                            if any(x in tweet.text for x in config.like_tags):
                                # If the tweets contains any like_tags, it automatically likes the tweet
                                twitter_api.CreateFavorite(status_id=tweet.id)
                                just_retweet_streak = 0
                        except:
                            pass
                        # Max is 2400 tweets per day in windows of half an hour. Thus, 36s as interval guarantees as we won't
                        # pass that amount
                        time.sleep(config.retweet_rate * (just_retweet_streak + 1))
                        print(f"Analized: \n{tweet.text}")
                    except Exception as e:
                        # In case the error contains sentences that mean the app is probably banned or the user over daily
                        # status update limit, we cancel the function
                        if "retweeted" not in str(e):
                            return
                    # And continues with the next item
    print(
        colors.OKGREEN
        + "Finished Analyzing ("
        + str(len(searched_tweets))
        + " tweets analyzed)"
    )


# print("\n")
check()
# print(f"Restarting in {config.search_rate} second(s)...")
# This is here for the delay between searches
# time.sleep(config.search_rate)
