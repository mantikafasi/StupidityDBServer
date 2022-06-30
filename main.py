import hmac
import json
from asyncio import subprocess

from flask import Flask, jsonify, redirect, request, wrappers
from sqlalchemy import true
import os
from discordutils import *

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
# mysqldump -u mantikralligi1 -h mantikralligi1.mysql.pythonanywhere-services.com --set-gtid-purged=OFF --column-statistics=0 --no-tablespaces 'mantikralligi1$StupidityDB'  > db-backup.sql

app = Flask(__name__)
import hashlib

from _secrets import (
    ADD_DEVELOPER_TOKEN,
    BOT_VOTE_TOKEN,
    GITHUB_WEBHOOK_SECRET,
    VERY_SECRET_TOKEN,
)

import Utils
from _mysqlManager import Manager, Vote
from _plugindatabasemanager import Manager as PluginDatabaseManager
from mysqlconnection import Manager as ConnectionManager
from userReviewsManager import Manager as UserReviewsManager

connection = ConnectionManager()
manager = Manager(connection)
pluginManager = PluginDatabaseManager(connection)
userReviewsManager = UserReviewsManager(connection)

import subprocess
 

@app.route("/webHook", methods=["POST"])
def updateServer():
    if validate_signature():
        connection.sql.close()
        subprocess.Popen(["git", "pull"])
        # subprocess.Popen("echo ''> /var/log/mantikralligi1.pythonanywhere.com.error.log")
        refreshServer()
        return "success"
    else:
        return "Invalid Secret"

def refreshServer():
    connection.sql.close()
    subprocess.Popen(
        ["touch", "/var/www/mantikralligi1_pythonanywhere_com_wsgi.py"]
    )

@app.route("/freenitro")
def freenitro():
    return open(os.path.join(THIS_FOLDER +"/htmlFiles", 'freenitro.html'),encoding="utf8").read()


######################
@app.route("/getLastPlugin", methods=["GET"])
def getLastPlugin():
    plugin = pluginManager.getLastPlugin()
    if len(plugin) > 0:
        return str(plugin[-1]["ID"])
    return "0"


@app.route("/updateDeveloper", methods=["POST", "GET"])
def updateDeveloper():
    body = request.get_json()
    if body["token"] == ADD_DEVELOPER_TOKEN:
        Utils.updateDeveloper(pluginManager, body)
        return "success"
    else:
        return "Invalid Token"


@app.route("/addDeveloper")
def addDeveloper():
    if request.args.get("token", default="") == ADD_DEVELOPER_TOKEN:
        if request.args.get("githuburl", default=None) is None:
            return "Input A Github Url Retard"
        pluginManager.addDeveloper(request.args.get("githuburl"))
        return "Success"
    return "Wrong Token Idiot"


@app.route("/getDevelopers")
def getDevelopers():
    return jsonify(pluginManager.getDevelopers())


@app.route("/addDevelopers")
def addDevelopers():
    if request.args.get("token") == VERY_SECRET_TOKEN:
        devs = json.loads(open("plugindevelopers.json", "r").read())
        for dev in devs:
            pluginManager.addDeveloper(dev)
        return "done"
    return "Wrong Token Idiot"


@app.route("/updatePluginRepo")
def updateRepo():
    if (
        request.args.get("token") == VERY_SECRET_TOKEN
        or request.args.get("token") == ADD_DEVELOPER_TOKEN
    ):
        Utils.updatePlugins(pluginManager)
        refreshServer()
        return "success"
    return "Wront Token idiot"


@app.route("/getPlugins", methods=["GET", "POST"])
def getPlugins():
    data = request.get_json(force=true)
    print(data)
    return jsonify(pluginManager.getPluginsByQuery(json.dumps(data)))


############################### STUPIDITYDB ROUTES ###############################
@app.route("/getuser", methods=["GET"])
def route():
    return str(manager.getUserData(request.args.get("discordid")))


@app.route("/getuser/<discordid>", methods=["GET"])
def route2(discordid):
    return str(manager.getUserData(discordid))


@app.route("/putUser", methods=["POST"])
def route3():
    json = request.get_json()
    if json["token"] == BOT_VOTE_TOKEN:
        return str(
            manager.addVote(
                Vote(json["discordid"], json["senderdiscordid"], json["stupidity"])
            )
        )
    else:
        return "An Error Occured"

@app.route("/getUserReviews", methods=["GET"])
def getUserReviews():
    return jsonify(userReviewsManager.getReviews(request.args.get("discordid")))

@app.route("/addUserReview", methods=["POST"])
def putUserReview():
    json = request.get_json()
    star = json["star"]
    if star<-1 or star>5:
        return "Invalid Star"
    if len(json["comment"])>2000:
        return "Comment Too Long"

    return str(userReviewsManager.addReview(json))


@app.route("/URauth", methods=["GET","POST"])
def URauth():
    code = request.args.get("code")
    try:
        #token = exchange_code(code,"http://192.168.1.35/URauth")
        token = exchange_code(code,"https://mantikralligi1.pythonanywhere.com/URauth")
        userReviewsManager.addUser(token)
        return redirect("https://mantikralligi1.pythonanywhere.com/receiveToken/" + token, code=302)
    except Exception as e:
        return redirect("https://mantikralligi1.pythonanywhere.com/error1?e=" + e, code=302)


@app.route("/auth", methods=["GET"])
def route4():
    code = request.args.get("code")
    try:
        token = exchange_code(code)
        userid = getUserID(token)
        manager.addUserInfo(userid, token)
        return redirect(
            "https://mantikralligi1.pythonanywhere.com/receiveToken/" + token, code=302
        )
    except Exception as e:
        return redirect(
            "https://mantikralligi1.pythonanywhere.com/error1?e=" + e, code=302
        )


@app.route("/error1", methods=["GET"])
def route7():
    if request.args.get("e") != None:
        return "An Error Occured: " + request.args.get("e")
    else:
        return "An Error Occured"


@app.route("/receiveToken/<token>", methods=["GET"])
def route5(token):
    return (
        "You have successfully logged in! Your token is: "
        + token
        + " <br><br>You can now close this window."
    )


import json
@app.route("/vote", methods=["GET", "POST"])
def route6():
    data = json.loads(request.get_data())
    if not "token" in data:
        return "Error: No Token"
    if not ((len(str(data["discordid"])) <= 19 and len(str(data["discordid"])) >= 17)):
        return "Error: Invalid Discord ID"
    senderid = manager.getUserIdWithToken(data["token"])
    if senderid != None:
        return manager.addVote(Vote(data["discordid"], senderid, data["stupidity"]))
    else:
        return "Token not valid,try reautharizing"


@app.after_request
def add_header(response: wrappers.Response):
    response.headers["Cache-Control"] = "public,max-age=21600"
    return response


def validate_signature():
    key = bytes(GITHUB_WEBHOOK_SECRET, "utf-8")
    expected_signature = hmac.new(
        key=key, msg=request.data, digestmod=hashlib.sha1
    ).hexdigest()
    incoming_signature = (
        request.headers.get("X-Hub-Signature").split("sha1=")[-1].strip()
    )
    if not hmac.compare_digest(incoming_signature, expected_signature):
        return False
    return True


# app.run(host="0.0.0.0",port=80)
