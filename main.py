from flask import Flask, escape, request,wrappers,jsonify,redirect
import requests
from discordutils import *
app = Flask(__name__)
from secrets import BOT_VOTE_TOKEN
from _mysqlManager import Manager,Vote
from _plugindatabasemanager import Manager as PluginDatabaseManager
import Utils
manager = Manager()
pluginManager = PluginDatabaseManager(manager.sql)

@app.route("/updatePluginRepo")
def updateRepo():
    Utils.updatePlugins(pluginManager)
@app.route("/getPlugins")
def getPlugins():
    query = request.args.get("query","")
    index = request.args.get("index",0)
    return jsonify(pluginManager.getPluginsByQuery(query,index))
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
    if(json["token"] == BOT_VOTE_TOKEN):
        return str(manager.addVote(Vote(json["discordid"],json["senderdiscordid"],json["stupidity"])))
    else:
        return "An Error Occured"

@app.route("/auth", methods=["GET"])
def route4():
    code = request.args.get("code")
    try:
        token = exchange_code(code)
        userid = getUserID(token)
        manager.addUserInfo(userid,token)
        return redirect("https://mantikralligi1.pythonanywhere.com/receiveToken/"+token, code=302)
    except Exception as e:
        return redirect("https://mantikralligi1.pythonanywhere.com/error1?e="+ e, code=302)
@app.route("/error1", methods=["GET"])
def route7():
    if request.args.get("e")!=None:
        return "An Error Occured: "+request.args.get("e")
    else:
        return "An Error Occured"
@app.route("/receiveToken/<token>", methods=["GET"])
def route5(token):
    return "You have successfully logged in! Your token is: "+token +" <br><br>You can now close this window."

import json
@app.route("/vote", methods=["GET","POST"])
def route6():
    data = json.loads(request.get_data())
    if (not "token" in data):
        return "Error: No Token"
    if not ((len(str(data["discordid"]))<=19 and len(str(data["discordid"]))>=17)):
        return "Error: Invalid Discord ID"
    
    senderid = manager.getUserIdWithToken(data["token"])
    if(senderid!=None):
        return manager.addVote(Vote(data["discordid"],senderid,data["stupidity"]))
    else:
        return "Token not valid,try reautharizing"



@app.after_request
def add_header(response:wrappers.Response):
    response.headers['Cache-Control'] = 'public,max-age=21600'
    return response


#app.run(host="0.0.0.0",port=80)