import requests
import json
from _plugindatabasemanager import Manager as PluginDatabaseManager
from _plugindatabasemanager import Plugin
from datetime import timezone
import datetime


def returnJsonValue(cur):
    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    for result in rv:
        json_data.append(dict(zip(row_headers,result)))
    return (json_data)

def updatePlugins():
    developers = []
    manager = PluginDatabaseManager()
    with open("plugindevelopers.json","r") as f:
        developers = json.loads(f)
    for dev in developers:
        devurl = dev.split("https://github.com/")[1]
        dt = datetime.datetime.now(timezone.utc)
    
        utc_time = dt.replace(tzinfo=timezone.utc)
        utc_timestamp = utc_time.timestamp()
        jsonf:dict = json.loads(requests.get(f"https://raw.githubusercontent.com/{devurl}/builds/updater.json").text)
        for a in jsonf.keys():
            plugin = jsonf[a]
            manager.addPlugin(Plugin(0,a,utc_timestamp,0,plugin["version"],plugin["build"],""))
