import mysql.connector
import json
from cachetools import cached, LRUCache, TTLCache
from mysql.connector import cursor
import hashlib as hasher
from Utils import returnJsonValue
import requests
class Plugin:
    def __init__(self,id:int,plugin_name:str,timestamp:int,author:int,version:str,download_link:str,description:str,changelog:str,authorid:int):
        self.id = id
        self.plugin_name = plugin_name
        self.timestamp = timestamp
        self.author = author
        self.version = version
        self.description = description
        self.download_link = download_link
        self.changelog = changelog
        self.authorid=authorid
    def __str__(self):  
        return '{} {} {}'.format(self.id,self.plugin_name,self.timestamp)

class Manager:
    def __init__(self,manager):
        self.manager = manager

    def cursor(self):
        return self.manager.cursor()

    @cached(cache=TTLCache(maxsize=1024, ttl=86400))
    def getPluginsByQuery(self,data):
        data = json.loads(data)
        cur = self.cursor()
        queryFilter = ""
        if ("author" in data):
            queryFilter += f" AND author_id = '{data['author']}'"
        if ('sort_by' in data):
            sort = data['sort_by']
            if (sort == 'repo_stars' or sort == 'ID' or sort == 'timestamp'):
                if (sort == 'ID'): sort = "pr.ID"
                queryFilter+=f" ORDER BY {sort} desc"
                
            
        if ('query' not in data): data['query'] = ''
        if ('index' not in data): data['index'] = 0
        cur.execute(f"SELECT * FROM plugin_repo pr INNER JOIN pluginrepo_developers pd ON (pr.author_id = pd.ID) WHERE plugin_name LIKE %s AND pr.ID>=%s {queryFilter} LIMIT 50",   ("%"+data['query']+"%",data['index']))
        #returns array of plugins
        return returnJsonValue(cur)
    
    def getDevelopers(self):
        cur = self.cursor()
        cur.execute("SELECT * FROM pluginrepo_developers")
        return returnJsonValue(cur)

    def addDeveloper(self,repoURL:str):
        devName = repoURL.split("https://github.com/")[1].split("/")[0]
        repoName= repoURL.split("https://github.com/"+devName+"/")[1]
        repo_info = requests.get(f"https://api.github.com/repos/{devName}/{repoName}").json()
        #pluginrepo_developers table fields: github_username,github_url,plugins_repo_name,repo_stars
        #adds developer to database
        star_count = repo_info["stargazers_count"]
        cur = self.cursor()
        cur.execute("SELECT * FROM pluginrepo_developers WHERE github_username=%s",(devName,))
        if len(cur.fetchall()) > 0:
            cur.execute("UPDATE pluginrepo_developers SET github_username=%s,plugins_repo_name=%s,repo_stars=%s WHERE github_username=%s",(devName,repoName,star_count,devName))
        else:
            cur.execute("INSERT INTO pluginrepo_developers(github_username,plugins_repo_name,repo_stars) VALUES (%s,%s,%s)",(devName,repoName,star_count))
        return "Successful"
        
    def addPlugin(self,plugin:Plugin):
        cur = self.cursor()
        sq = "INSERT INTO plugin_repo(plugin_name,timestamp,download_link,version,description,changelog,author,authorid) VALUES (%s, %s,%s,%s,%s,%s,%s,%s)"
        values = (plugin.plugin_name,plugin.timestamp,plugin.download_link,plugin.version,plugin.description,plugin.changelog,plugin.author,plugin.authorid)
        cur.execute("SELECT * FROM plugin_repo WHERE plugin_name=%s",(plugin.plugin_name,))
        if len(cur.fetchall()) > 0:
            cur.execute("UPDATE plugin_repo SET download_link=%s,version=%s,description=%s,changelog=%s, author=%s,author_id=%s WHERE plugin_name=%s",(plugin.download_link,plugin.version,plugin.description,plugin.changelog,plugin.author,plugin.authorid,plugin.plugin_name))
        else:
            cur.execute(sq,values) 
        self.manager.sql.commit()
        return "Successful"
    def addPlugin1(self,plugin_name:str,timestamp:int,author:str,version:str,download_link:str,description:str,changelog:str,authorid:int):
        self.addPlugin(Plugin(0,plugin_name,timestamp,author,version,download_link,description,changelog,authorid))

