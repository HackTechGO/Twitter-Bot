import twitter

from model.tweet import Tweet


class Scrapper:
    # we need hash_tag to scan,
    # start_time - the time to compare our tweets in order to decide if they are newer or not
    # tweets - an array to collect all new tweets
    def __init__(self, hash_tag, time_start, apiKey):
        self.hash_tag = hash_tag
        self.time_start = time_start
        self.apiKey = apiKey
        self.tweets = []

    def run(self):
        # init api
        # https://github.com/bear/python-twitter
        api = twitter.Api(consumer_key=self.apiKey.consumer_key,
                          consumer_secret=self.apiKey.consumer_secret,
                          access_token_key=self.apiKey.access_token_key,
                          access_token_secret=self.apiKey.access_token_secret)

        # search for hashtag
        search = api.GetSearch(self.hash_tag)
        for tweet in search:
            # extract time
            time = tweet.created_at_in_seconds

            # compare if time of the current tweet is less the our desirable time then go back to for loop
            if self.time_start >= time:
                continue

            message = tweet.text
            author = tweet.user.name

            # convert into tweeter_obj and store it in the array
            tweet_obj = Tweet(author, time, message)
            self.tweets.append(tweet_obj)

    def get_tweets(self):
        return self.tweets
