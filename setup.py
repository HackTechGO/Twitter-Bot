from model.db_hander import DbHandler

# constant for our database_name
DB_NAME = "database.db"

if __name__ == '__main__':
    db = DbHandler(DB_NAME)

    timeout = [1]  # in minutes minutes
    params = [('#nba',), ('#oslo',), ('#kardashian',)]  # tags that could interest us

    db.execute("CREATE TABLE tweets_by_hash ("
               "id INTEGER PRIMARY KEY AUTOINCREMENT, "
               "term VARCHAR(30));")
    db.execute("CREATE TABLE tweets ("
               "time INTEGER, "
               "hash_id INTEGER, "
               "author VARCHAR(100), "
               "message VARCHAR(140), "
               "tags VARCHAR(140),"
               "FOREIGN KEY(hash_id) REFERENCES tweets_by_hash(id));")
    db.execute("CREATE TABLE timeout (timeout INTEGER not null);")
    db.execute("INSERT INTO timeout VALUES (?);", timeout)
    db.execute("CREATE TABLE terms (term VARCHAR(30));")
    db.execute("INSERT INTO terms VALUES (?);", params)

    db.execute("CREATE INDEX term_idx ON tweets_by_hash (term);")
    db.execute("CREATE INDEX hash_id_idx ON tweets (hash_id);")
    db.execute("CREATE INDEX time_idx ON tweets (time);")

    db.close_connection()
