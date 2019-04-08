import logging

from scrapper.scheduler import Scheduler
from setup import DB_NAME
from util.util import read_api_key

if __name__ == '__main__':
    # log into a logfile starting with INFO tag
    # https://docs.python-guide.org/writing/logging/
    # or https://www.digitalocean.com/community/tutorials/how-to-use-logging-in-python-3
    logging.basicConfig(filename='application.log', level=logging.INFO)

    apiKey = read_api_key("api.txt")

    # using constant DB_NAME from setup.py file
    # creating Scheduler class from scrapper.scheduler
    scheduler = Scheduler(DB_NAME, apiKey)
    # running Scheduler's main method
    scheduler.run()
