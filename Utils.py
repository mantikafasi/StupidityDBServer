from flask import request
import requests
import json
from datetime import timezone
import datetime
import io
from shutil import rmtree
import zipfile
from threading import Thread

def returnJsonValue(cur):
    row_headers=[x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    for result in rv:
        json_data.append(dict(zip(row_headers,result)))
    return (json_data)

def updatePlugins(manager):
    developers = []
    developers = manager.getDevelopers()
    for dev in developers:
        devurl = f"{dev['github_username']}/{dev['plugins_repo_name']}"
        plugins = requests.get(f"https://raw.githubusercontent.com/{devurl}/builds/updater.json").json()

        for pluginName in plugins.keys():
            plugin = plugins[pluginName]
            if "build" in plugin:
                plugin["build"] = plugin["build"].replace("%s",pluginName)
                updatePlugin(manager,pluginName,plugin["build"],dev)
                #Thread(target=updatePlugin,args=(manager,a,downloadUrl)).start()

def updatePlugin(manager,pluginName,downloadUrl:str,dev:dict):
    try:
        dt = datetime.datetime.now(timezone.utc)
        utc_time = dt.replace(tzinfo=timezone.utc)
        utc_timestamp = utc_time.timestamp()
        downloadedFile = requests.get(downloadUrl)
        zipfile.ZipFile(io.BytesIO(downloadedFile.content)).extractall(f"./extracted/{pluginName}")
        manifest = json.loads(open(f"./extracted/{pluginName}/manifest.json","r").read())
        manager.addPlugin1(pluginName,utc_timestamp,str(manifest["authors"]),manifest["version"],downloadUrl,manifest["description"],manifest["changelog"],dev["ID"])
        rmtree("./extracted/")
    except Exception as e:
        print("shit" + str(pluginName))
        print(str(e))