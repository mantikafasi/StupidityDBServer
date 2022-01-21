import requests
import json
from datetime import timezone
import datetime


def returnJsonValue(cur):
    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    for result in rv:
        json_data.append(dict(zip(row_headers,result)))
    return (json_data)

def updatePlugins(manager):
    developers = []
    with open("plugindevelopers.json","r") as f:
        developers = json.loads(f.read())
    for dev in developers:
        devurl = dev.split("https://github.com/")[1]
        dt = datetime.datetime.now(timezone.utc)
    
        utc_time = dt.replace(tzinfo=timezone.utc)
        utc_timestamp = utc_time.timestamp()
        jsonf:dict = json.loads(requests.get(f"https://raw.githubusercontent.com/{devurl}/builds/updater.json").text)
        for a in jsonf.keys():
            plugin = jsonf[a]
            if "build" in plugin:
                manager.addPlugin1(0,a,utc_timestamp,0,plugin["version"],plugin["build"],"")
