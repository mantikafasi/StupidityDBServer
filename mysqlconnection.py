import mysql.connector
from secrets import db,dbpw,dbip,dbuser
class Manager:
    def __init__(self,sql):
        self.sql = sql
        self.cur = self.cursor()
    
    def cursor(self):
        try:
            self.sql.ping(reconnect=True, attempts=3, delay=5)
        except mysql.connector.Error:
            self.sql.disconnect()  
            self.sql = mysql.connector.connect(host=dbip,user=dbuser,password=dbpw,database=db,autocommit=True)
            self.cursor()
        return self.sql.cursor()
