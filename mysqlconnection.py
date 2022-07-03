from _secrets import db, dbip, dbpw, dbuser
import psycopg2 as connector

class Manager:
    def __init__(self):
        try:
            print("creating new connection")
            self.sql = connector.connect(
                host=dbip, user=dbuser, password=dbpw, database=db
            )
            print(self.sql.closed)
            self.cur = self.cursor()
        except Exception as e:
            self.sql = None
            print(e)

    def cursor(self):
        if self.sql.closed>0:
            if self.sql != None:
                self.sql.close()
            self.sql = connector.connect(
                host=dbip, user=dbuser, password=dbpw, database=db
            )
        return self.sql.cursor()
