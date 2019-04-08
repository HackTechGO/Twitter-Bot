from requests import get
from pyquery import PyQuery
from urllib.parse import quote

from model.tweet import Tweet
from scrapper.search_mode import SearchMode
from util.util import str_number_is_greater


class Scrapper2:
    URL = "https://mobile.twitter.com/search?q={}&s={}"
    BAD_HEADER = '<?xml version="1.0" encoding="utf-8"?>'
    TWEET_TIME = "tweet_"

    def __init__(self, hash_tag, time_start, mode=SearchMode.EXACT):
        self.mode = mode
        self.hash_tag = hash_tag
        self.tweets = []
        self.time_start = time_start

    def run(self):
        # url does't support `#` symbol, it should be converted into %23
        # https://www.w3schools.com/tags/ref_urlencode.asp
        quoted_term = quote(self.hash_tag)
        # get webpage of URL constant, see above, where q=hash_tag&s=mode, by default mode=SearchMode.EXACT
        # which is sprv (see search_mode.py)
        request = get(self.URL.format(quoted_term, self.mode))
        # get response text
        response = request.text

        # remove BAD_HEADER constant, because <?xml version="1.0" encoding="utf-8"?> is incompatible with PyQuery
        # and here we create feed pyQuery object
        # https://pypi.org/project/pyquery/
        filter_idx = len(self.BAD_HEADER)
        feed = PyQuery(response[filter_idx:])

        # like in jquery ".tweet" -> class="tweet", returns us an array
        tweet_html_array = feed(".tweet")

        for element in tweet_html_array.items():
            time = element(".timestamp a").attr("name")
            # because the time object is tweet_123178237914 - we need to get rid of `tweet_` in order to get a number
            time = time[len(self.TWEET_TIME):]

            # compare time by comparing 2 strings
            if str_number_is_greater(time, str(self.time_start)):
                author = element(".username").text()
                text = element(".tweet-text .dir-ltr").text()

                tweet = Tweet(author, time, text)
                self.tweets.append(tweet)

    def get_tweets(self):
        return self.tweets
