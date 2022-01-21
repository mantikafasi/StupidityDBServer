import mysql.connector
import json
from cachetools import cached, LRUCache, TTLCache
from mysql.connector import cursor
import hashlib as hasher
from secrets import prdb,dbpw,dbip,dbuser
from Utils import returnJsonValue

class Plugin:
    def __init__(self,id:int,plugin_name:str,timestamp:int,author:int,version:str,download_link:str,description:str):
        self.id = id
        self.plugin_name = plugin_name
        self.timestamp = timestamp
        self.author = author
        self.version = version
        self.description = description
        self.download_link = download_link
    def __str__(self):  
        return '{} {} {}'.format(self.id,self.plugin_name,self.timestamp)

class Manager:
    def __init__(self):
        self.sql = mysql.connector.connect(host=dbip,user=dbuser,password=dbpw,database=prdb,autocommit=True)
        self.cur = self.cursor()
    
    def cursor(self):
        try:
            self.sql.ping(reconnect=True, attempts=3, delay=5)
        except mysql.connector.Error:
            self.sql.disconnect()  
            self.sql = mysql.connector.connect(host=dbip,user=dbuser,password=dbpw,database=prdb,autocommit=True)
            self.cursor()
        return self.sql.cursor()

    @cached(cache=TTLCache(maxsize=1024, ttl=86400))
    def getPluginsByQuery(self,query:Plugin,index = 0):
        cur = self.cursor()
        cur.execute("SELECT * FROM plugin_repo WHERE plugin_name LIKE %s AND ID>=%s LIMIT 50",("%"+query+"%",index))
        #returns array of plugins
        return returnJsonValue(cur)
        
    def addPlugin(self,plugin:Plugin):
        cur = self.cursor()
        sq = "INSERT INTO plugin_repo(plugin_name,timestamp,download_link,version,description) VALUES (%s, %s,%s,%s,%s)"
        values = (plugin.plugin_name,plugin.timestamp,plugin.download_link,plugin.version,plugin.description)
        cur.execute("SELECT * FROM plugin_repo WHERE plugin_name=%s",(plugin.plugin_name,))
        if len(cur.fetchall()) > 0:
            pass
            #cur.execute("UPDATE plugin_repo SET token=%s WHERE discordid=%s",(enctoken,discordid))
        else:
            cur.execute(sq,values) 
        self.sql.commit()
        return "Successful"
    def addPlugin1(self,id:int,plugin_name:str,timestamp:int,author:int,version:str,download_link:str,description:str):
        self.addPlugin(Plugin(id,plugin_name,timestamp,author,version,download_link,description))

