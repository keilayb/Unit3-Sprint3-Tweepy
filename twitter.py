from os import getenv
import tweepy

auth = tweepy.OAuthHandler(getenv("API_KEY"), getenv("API_KEY_SECRET"))
auth.set_access_token(getenv("ACCESS_TOKEN"), getenv("ACCESS_TOKEN_SECRET"))
twitter = tweepy.API(auth)

def get_info(username):
    try:
        twitter_user = twitter.get_user(screen_name=username)
        tweets = twitter.user_timeline(
            screen_name=username,
            count=700,
            exclude_replies=True,
            include_rts=False,
            tweet_mode="Extended"
        )
        tweets_text = []
        for i,tweet in enumerate(tweets):
            text = tweets[i]._json["text"]
            tweets_text.append(text)
        
        return twitter_user, tweets_text

    except Exception as e:
        print("Error Processing %s: %s" % (username, e))

def get_followers_avg_favorites(username):
    # User info
    twitter_user = twitter.get_user(screen_name=username)
    # Follower count
    followers = twitter_user.followers_count
    # Get tweets
    tweets = twitter.user_timeline(
            screen_name=username,
            count=500,
            exclude_replies=True,
            include_rts=False,
            tweet_mode="Extended"
        )
    # Get each tweet's number of favorites
    favorites = []
    for i, tweet in enumerate(tweets):
        favorite_number = tweets[i]._json["favorite_count"]
        favorites.append(favorite_number)
    
    avg_favorites = sum(favorites)/len(favorites)
    return followers, avg_favorites
    
