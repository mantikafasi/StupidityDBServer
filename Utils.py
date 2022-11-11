import datetime
import io
import json
import zipfile
from datetime import timezone
from shutil import rmtree

import requests


def returnJsonValue(cur, reverse=False):
    row_headers = [x[0] for x in cur.description]
    rv = cur.fetchall()
    if reverse:
        rv.reverse()
    json_data = []
    for result in rv:
        json_data.append(dict(zip(row_headers, result)))
    return json_data


def updatePlugins(manager):
    developers = manager.getDevelopers()
    for dev in developers:
        updateDeveloper(manager, dev)


def updateDeveloper(manager, dev: dict):
    devurl = f"{dev['github_username']}/{dev['plugins_repo_name']}"
    try:
        plugins = requests.get(
            f"https://raw.githubusercontent.com/{devurl}/builds/updater.json"
        ).json()
    except Exception as e:
        print(f"This developer is stupit ({dev}) " + str(e))
        return

    for pluginName in plugins.keys():
        try:
            if pluginName == "default":
                continue
            plugin = plugins[pluginName]
            if not "build" in plugin:
                plugin[
                    "build"
                ] = f"https://raw.githubusercontent.com/{devurl}/builds/%s.zip"
            plugin["build"] = plugin["build"].replace("%s", pluginName)
            updatePlugin(manager, pluginName, plugin["build"], dev)
        except Exception as e:
            print("shit")
            print(str(e))


def updatePlugin(manager, pluginName, downloadUrl: str, dev: dict):
    try:
        dt = datetime.datetime.now(timezone.utc)
        utc_time = dt.replace(tzinfo=timezone.utc)
        utc_timestamp = utc_time.timestamp()
        downloadedFile = requests.get(downloadUrl)
        zipfile.ZipFile(io.BytesIO(downloadedFile.content)).extractall(
            f"./extracted/{pluginName}"
        )
        manifest = json.loads(
            open(f"./extracted/{pluginName}/manifest.json", "r").read()
        )
        manager.addPlugin1(
            pluginName,
            utc_timestamp,
            str(manifest["authors"]),
            manifest["version"],
            downloadUrl,
            manifest["description"],
            manifest["changelog"],
            dev["ID"],
        )
        rmtree("./extracted/")
    except Exception as e:
        print("shit" + str(pluginName))
        rmtree("./extracted/")
        print(str(e))


discordImageURL = "https://cdn.discordapp.com/avatars/{}/{}?size=80"


def getProfilePhotoURL(userid, avatarHash: str):
    if avatarHash == None:
        return None
    return discordImageURL.format(
        userid, avatarHash + (".gif" if avatarHash.startswith("a_") else ".png")
    )
