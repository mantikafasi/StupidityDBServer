import mysql.connector
from secrets import db,dbpw,dbip,dbuser
class Manager:
    def __init__(self):
        self.sql = mysql.connector.connect(host=dbip,user=dbuser,password=dbpw,database=db,autocommit=True)
        self.cur = self.cursor()
    
    def cursor(self):
        try:
            self.sql.ping(reconnect=True, attempts=3, delay=5)
        except mysql.connector.Error:
            self.sql.close()  
            self.sql = mysql.connector.connect(host=dbip,user=dbuser,password=dbpw,database=db,autocommit=True)
            self.cursor()
        return self.sql.cursor()
