import logging
import threading
from time import sleep

import schedule

from model.db_hander import DbHandler
from scrapper.app import Scrapper
from scrapper.app2 import Scrapper2


class Scheduler:
    logger = logging.getLogger(__name__)

    # constructor requires database name
    def __init__(self, dbname, apiKey):
        # creating our single object databaseHandler from model/db_handler
        self.db = DbHandler(dbname)
        # api_key.py
        self.apiKey = apiKey
        self._scheduler = None
        # default timeout 5 mins, but will be overwritten by db value
        self.timeout = 5

    def run(self):
        # read from db and set timeout
        self.__read_configs()

        # run twitter task at least once, because schedule.every will run the task only after timeout
        self.__run_a_task()

        # https://pypi.org/project/schedule/, please note that do(self.__run_a_task) -> __run_a_task is without ()
        schedule.every(self.timeout).minutes.do(self.__run_a_task)
        while True:
            schedule.run_pending()
            sleep(1)

    def __read_configs(self):
        timeout = self.db.execute("SELECT timeout FROM timeout LIMIT 1;")
        self.timeout = timeout[0][0]


    def __run_a_task(self):
        # read tags from db before scanning twitter, maybe some tags could be removed or added while the program is
        # running, kinda get configuration on fly
        terms = self.db.execute("SELECT term FROM terms;")

        # arrays will be used to access some created objects for later
        treads = []
        scrappers = []

        # for every hashtag do
        for term in terms:
            # MAX(time) - read the latest time, we want to skip already scanned tweets
            # term[0] is because term is [hashtag,] - an array of single element
            time_start = self.db.execute("SELECT MAX(time) FROM tweets WHERE hash_id = (SELECT id FROM tweets_by_hash WHERE term = ?)", [term[0]])
            # because returned object is [[time_start]] - array of array of single object
            time_start = time_start[0][0]

            # if we don't have any tweets with that hashtag in our database then time_start is just 0,
            # because hashtag is new
            if time_start is None:
                time_start = 0

            # init our scrapper class
            scrapper = Scrapper(term[0], time_start, self.apiKey)
            # scrapper2 is created but not used, you can rename it to scrapper and commet out the line above
            # but be aware that time is incompatible between 2 table, therefore please use different databases for
            # these 2 methods
            scrapper2 = Scrapper2(term[0], time_start)

            # branch a new thread (from the main thread) for our scrapper.run method
            t = threading.Thread(target=scrapper.run)

            # store objects in array in order to access them later
            scrappers.append(scrapper)
            treads.append(t)

            # start newly branched thread
            t.start()

        # iterate over all created threads and tell the main thread to wait for all subthreads to complete
        # before moving forward
        for t in treads:
            t.join()

        # main thread is here
        # all subthreads are completed
        # now iterating through our scrappers objects in order to retrieve some data
        for s in scrappers:
            params = []

            # s.get_tweets() -> Scrapper get_tweets returns an array, so we are iterating over that array
            # for every object tw from s.get_tweets()
            for tw in s.get_tweets():
                # to_param_query creates a db friendly array from twitter object
                # add db friendly arrays to parameter array
                params.append(tw.to_param_query())

            # get hashtag from the current scrapper
            term = s.hash_tag

            # select id of the hashtag
            id = self.db.execute("SELECT id FROM tweets_by_hash WHERE term = ?", [term])

            # if id doesn't exist, put into database and select the id again
            if id is None or len(id) == 0:
                self.db.execute("INSERT INTO tweets_by_hash VALUES (null, ?);", [term])
                id = self.db.execute("SELECT id FROM tweets_by_hash WHERE term = ?", [term])

            # just log the message
            self.logger.info("{} tweets for term:{}".format(len(params), term))

            # insert all params into tweets
            # here I used `.format(id[0][0])` which will replace `{}` with the current id, i.e. in db_handler it will
            # look like ("INSERT INTO tweets VALUES (?, 4, ?, ?, ?)", params), only of course our id is 4
            self.db.execute("INSERT INTO tweets VALUES (?, {}, ?, ?, ?)".format(id[0][0]), params)
