import mysql.connector
from secrets import db,dbpw,dbip,dbuser
class Manager:
    def __init__(self):
        try:
            self.sql = mysql.connector.connect(host=dbip,user=dbuser,password=dbpw,database=db,autocommit=True)
            self.cur = self.cursor()
        except Exception as e:
            print(e)
    def cursor(self):
        try:
            self.sql.ping(reconnect=True, attempts=3, delay=5)
        except mysql.connector.Error:
            if self.sql != None : self.sql.close()  
            self.sql = mysql.connector.connect(host=dbip,user=dbuser,password=dbpw,database=db,autocommit=True)
        return self.sql.cursor()
