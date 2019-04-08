import logging
import sqlite3
from threading import Lock


# a wrapper upon the database library, it must be only 1 per project
# the idea of the class is that our application will talk with database through this object
# which means that we have control over number of connections to database in order to avoid
# db connection leaks problem
# right now this class uses only 1 connection to database
class DbHandler:
    # just a logger class, see run.py how to better configure it
    # improves redability of logs
    # example of the "self.logger.error(("Error executing an error", query, params, e))"
    # Will return something like that:
    # "ERROR:model.db_hander:('Error executing an error', 'CREATE TABLE tweets_by_hash (id INTEGER PRIMARY KEY AUTOINCREMENT, term VARCHAR(30));', None, OperationalError('attempt to write a readonly database'))"

    logger = logging.getLogger(__name__)

    # constructor
    # required fields; dbname
    # optional field: timeout
    def __init__(self, dbname, timeout=5):
        self.conn = None
        self.dbname = dbname
        self.timeout = timeout

        # init of the lock, which will be used for thread safety
        self.lock = Lock()

    def execute(self, query, params=None):
        # the lock statement, the first thread will go inside, all others threads will be waiting in a queue
        # until the thread inside releases the lock, after the first thread releases the lock the first thread
        # in the waiting queue will go inside and lock this locker again
        # thread 1 -> execute
        # thread 1 -> lock.acquire() (this means that after this lock.acquire it runs the code below)
        # thread 3 -> execute
        # thread 3 -> waiting (1st in the queue) - because the thread 1 is still executing the code below
        # thread 2 -> execute
        # thread 2 -> waiting (2st in the queue)
        # thread 1 -> lock.release
        # thread 1 -> exit (return method)
        # thread 3 -> lock.acquire()
        # thread 2 -> waiting (now 1st in the queue)
        # thread 3 -> lock.release()
        # thread 3 -> exit
        # thread 2 -> lock.acquire()
        # thread 2 -> lock.release()
        # thread 2 -> exit

        self.lock.acquire()

        # init connection to the db on the first run
        # read more about sqlite3 https://docs.python.org/2/library/sqlite3.html
        if self.conn is None:
            self.conn = sqlite3.connect(self.dbname, timeout=self.timeout, isolation_level=None)

        # sqlite3 `execute` method supports Exception which throws sqlite3.Error
        # this method is called inside `__execute_query` function
        # the idea of the method is:
        # res = self.__execute_query(query, params)
        # 1) if everything is fine skip `except` block
        # 2) otherwise match exception with the one in `except` block - currently `sqlite3.Error`
        # if it matches run the code inside `except` block
        try:
            res = self.__execute_query(query, params)
        except sqlite3.Error as e:
            # log an error
            self.logger.error(("Error executing an error", query, params, e))
            # release the lock if the error occurred
            self.lock.release()
            # exit with None
            # it will not continue the code below as `return` is the exit point here
            # this is why we have to release the lock inside `except` block as well
            # otherwise this class will be forever locked on error
            return None

        # release the lock if the action succeeded
        self.lock.release()
        return res

    # close connection method also requires locking
    # because we want to make sure that nobody is running `def execute(self, query, params=None)`
    # otherwise the query wouldn't be finished which in theory may lead to corruption of data
    # example
    # thread 1 -> execute - if connection is closed it will be opened (see the body of the execute)
    # thread 1 -> lock.acquire() (this means that thread is running execute main body right now)
    # thread 3 -> close_connection
    # thread 3 -> waiting (1st in the queue) - because the thread 1 is still executing the code below
    # thread 2 -> execute
    # thread 2 -> waiting (2st in the queue)
    # thread 1 -> lock.release
    # thread 1 -> exit (return method)
    # thread 3 -> lock.acquire() inside close_connection method, it will close the connection
    # thread 2 -> waiting (now 1st in the queue)
    # thread 3 -> lock.release() - connection is closed and self.conn = None
    # thread 3 -> exit
    # thread 2 -> lock.acquire() - because connection was closed, it will open connection again
    # thread 2 -> lock.release() - connection is still opened
    # thread 2 -> exit

    def close_connection(self):
        self.lock.acquire()
        # we need to check if connection exists otherwise if we will try to close connection of None,
        # the exception will be thrown, which means the program will crash
        if self.conn is None:
            self.conn.close()
            self.conn = None
        self.lock.release()

    # here I used very simple algorithm:
    # 1) I either execute smth like CREATE TABLE ... without any parameters, thus `self.conn.execute(query).fetchall()`
    # 2) I provide 1 parameter an array with 1 element, 2 fields in 1 array [field1], [field2] => [[field1], [field2]]
    # smth like (UPDATE TABLE tbl SET a=? WHERE b=?, [[field1], [field2]]) - just 1 parameter, which consists
    # of 2 elements, thus `self.conn.execute(query, params).fetchall()`
    # 3) many parameters an array of arrays: INSERT INTO tbl VALUES (?, ?, ?),
    # [field1, field2, field3],
    # [field4, field5, field6] ...
    # examples are in setup.py
    # db.execute("CREATE TABLE terms (term VARCHAR(30));") - no params
    # db.execute("INSERT INTO timeout VALUES (?);", timeout) - timeout = [0] - one param
    # db.execute("INSERT INTO terms VALUES (?);", params) - multiple fields
    def __execute_query(self, query, params):
        if params is None:
            return self.conn.execute(query).fetchall()
        if len(params) > 1:
            return self.conn.executemany(query, params).fetchall()
        return self.conn.execute(query, params).fetchall()

    # when we didn't close the connection and this class is not used anymore somewhere in the code, it will close
    # connection during garbage collection process
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn is not None:
            self.conn.close()
