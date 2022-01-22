from flask import request
import requests
import json
from datetime import timezone
import datetime
import io
import os 

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
            files = requests.get(f"https://api.github.com/repos/{devurl}}/git/trees/builds").json()
            files:dict = files["tree"]
            for file in files:
                if file["path"].endswith(".zip"):
                    downloadUrl=f"https://raw.githubusercontent.com/{devurl}/builds/{file['path']}"
                    downloadedFile = request.get(downloadUrl)
                    zipfile = zipfile.ZipFile(io.BytesIO(downloadedFile.content)).extractall(f"./extracted/{a}")
                    manifest = json.loads(open(f"./extracted/{a}/manifest.json","r").read())
                    manager.addPlugin1(a,utc_timestamp,manifest["author"],manifest["version"],downloadUrl,manifest["description"],manifest["changelog"])
                    os.rmdir(f"./extracted/")
