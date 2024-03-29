import subprocess
from userReviewsManager import Manager as UserReviewsManager
from mysqlconnection import Manager as ConnectionManager
from _mysqlManager import Manager, Vote
from _secrets import (
    BOT_VOTE_TOKEN,
    GITHUB_WEBHOOK_SECRET,
)
import hashlib
import hmac
import json
import subprocess
import logging
from flask import Flask, jsonify, redirect, request, wrappers
import os
from discordutils import *
import flask_monitoringdashboard as dashboard

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    static_url_path="/static",
    static_folder="./ArtGallery/static",
    template_folder="./ArtGallery",
)
dashboard.bind(app)

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)


print("Creating connection")
connection = ConnectionManager()
print("Connection Created")

print("Loading StupidityDB Manager")
manager = Manager(connection)
print("Loading User Reviews Manager")
userReviewsManager = UserReviewsManager(connection)
print("All loaded!")


@app.route("/")
def mainPage():
    return open("./ArtGallery/index.html", "r").read()


@app.route("/webHook", methods=["POST"])
def updateServer():
    if validate_signature():
        connection.sql.close()
        subprocess.Popen(["git", "pull"])
        subprocess.Popen(["pm2", "restart", "0"])
        # subprocess.Popen("echo ''> /var/log/mantikralligi1.pythonanywhere.com.error.log")
        refreshServer()
        return "success"
    else:
        return "Invalid Secret"


def refreshServer():
    connection.sql.close()
    subprocess.Popen(["pm2", "restart", "0"])


@app.route("/freenitro")
def freenitro():
    return open(
        os.path.join(THIS_FOLDER + "/htmlFiles", "freenitro.html"), encoding="utf8"
    ).read()


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


@app.route("/getLastReviewID", methods=["GET"])
def getLastReviewID():
    return str(userReviewsManager.getLastReviewID(request.args.get("discordid")))


@app.route("/getReports")
def getReports():
    return jsonify(userReviewsManager.getReports())


@app.route("/getAuthorReviews")
def getAuthorReviews():
    # userid not discordid !
    return jsonify(userReviewsManager.getAuthorReviews(request.args.get("userid")))


@app.route("/reportReview", methods=["POST"])
def reportReview():
    json = request.get_json(force=True)
    if not "reviewid" in json or not "token" in json:
        return "Invalid Request"
    elif json["token"] == "":
        return "Token Is Null"

    return str(userReviewsManager.reportReview(json["token"], json["reviewid"]))


@app.route("/deleteReview", methods=["GET", "POST"])
def deleteReview():
    json = request.get_json(force=True)
    if not "reviewid" in json or not "token" in json:
        return "Invalid Request"
    elif json["token"] == "":
        return "Token Is Null"

    return jsonify(userReviewsManager.deleteReview(json["token"], json["reviewid"]))


@app.route("/getUserReviews", methods=["GET"])
def getUserReviews():
    reviews = userReviewsManager.getReviews(request.args.get("discordid"))
    if request.args.get("snowflakeFormat") == "string":
        for review in reviews:
            review["senderdiscordid"] = str(review["senderdiscordid"])

    if request.headers.get("User-Agent", "Horror") == "Aliucord (https://github.com/Aliucord/Aliucord)" and request.args.get("noAds","false") == "false":
        reviews.insert(0, {
            "comment":"Use ReviewDB on Desktop by using Vencord \nhttps://github.com/Vendicated/Vencord \nYou can disable this in settings",
            "id":0,
            "profile_photo":"https://cdn.discordapp.com/icons/1015060230222131221/f0204a918c6c9c9a43195997e97d8adf.webp?size=128",
            "senderdiscordid":343383572805058560,
            "senderuserid":28,
            "star":-1,
            "username":"ReviewDB",
            "isSystemMessage":True
        })

    return jsonify(reviews)


@app.route("/addUserReview", methods=["POST", "GET"])
def putUserReview():
    data = json.loads(request.get_data())
    star = data["star"]
    if star < -1 or star > 5:
        return "Invalid Star"
    if len(data["comment"]) > 1000:
        return "Comment Too Long"

    return str(userReviewsManager.addReview(data))


clientMods = ["aliucord", "powercordv2", "goosemod", "betterdiscord", "vencord"]


@app.route("/URauth", methods=["GET", "POST"])
def URauth():
    code = request.args.get("code")
    returnType = request.args.get("returnType", default="redirect")
    clientMod = request.args.get("clientMod", default="aliucord")
    if not clientMod in clientMods:
        return "Unknown Client Mod"
    try:
        # token = exchange_code(code,"http://192.168.1.35/URauth")
        token = exchange_code(code, "https://manti.vendicated.dev/URauth")
        userReviewsManager.addUser(token, clientMod)
        if returnType == "json":
            return jsonify({"token": token, "status": 0})
        return redirect("https://manti.vendicated.dev/receiveToken/" + token, code=302)
    except Exception as e:
        print(str(e))
        if returnType == "json":
            return jsonify(
                {"error": f"An Error Occured", "status": 1, "errorMessage": str(e)}
            )
        return redirect("https://manti.vendicated.dev/error1", code=302)


@app.route("/auth", methods=["GET"])
def route4():
    code = request.args.get("code")
    try:
        token = exchange_code(code)
        userid = getUserID(token)
        manager.addUserInfo(userid, token)
        return redirect("https://manti.vendicated.dev/receiveToken/" + token, code=302)
    except Exception as e:
        return redirect("https://manti.vendicated.dev/error1?e=" + e, code=302)


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
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
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


@app.errorhandler(404)
def notfodund(e):
    return open("./ArtGallery/index.html", "r").read()


# app.run(host="0.0.0.0",port=80)
