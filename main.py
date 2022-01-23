from asyncio import subprocess
import hmac
from flask import Flask, escape, request,wrappers,jsonify,redirect
import requests
from discordutils import *
app = Flask(__name__)
from _secrets import BOT_VOTE_TOKEN,GITHUB_WEBHOOK_SECRET,ADD_DEVELOPER_TOKEN,VERY_SECRET_TOKEN
from _mysqlManager import Manager,Vote
from _plugindatabasemanager import Manager as PluginDatabaseManager
import Utils
from mysqlconnection import Manager as ConnectionManager
import hashlib  
connection = ConnectionManager()
manager = Manager(connection)
pluginManager = PluginDatabaseManager(connection)


import subprocess

@app.route("/webHook",methods=["POST"])
def updateServer():
    if validate_signature():
        connection.sql.close()
        subprocess.Popen(["git","pull"])
        subprocess.Popen("echo ''> /var/log/mantikralligi1.pythonanywhere.com.error.log")
        subprocess.Popen(["touch","/var/www/mantikralligi1_pythonanywhere_com_wsgi.py"])
        return "success"
    else: return "Invalid Secret"
            
######################
@app.route("/addDeveloper")
def addDevekıoer():
    if (request.args.get("token")==ADD_DEVELOPER_TOKEN):
        manager.addDeveloper(request.args.get("discordid"))
        return "Success"
    return "Wrong Token Idiot"

@app.route("/getDevelopers")
def getDevelopers():
    return jsonify(pluginManager.getDevelopers())

@app.route("/addDevelopers")
def addDevelopers():
    if(request.args.get("token")==VERY_SECRET_TOKEN):
        devs = json.loads(open("plugindevelopers.json","r").read())
        for dev in devs:
            pluginManager.addDeveloper(dev)
        return "done"
    return "Wrong Token Idiot"
    
@app.route("/updatePluginRepo")
def updateRepo():
    if(request.args.get("token")==VERY_SECRET_TOKEN):
        Utils.updatePlugins(pluginManager)
        return "success"
    return "Wront Token idiot"

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

def validate_signature():
    key = bytes(GITHUB_WEBHOOK_SECRET, 'utf-8')
    expected_signature = hmac.new(key=key, msg=request.data, digestmod=hashlib.sha1).hexdigest()
    incoming_signature = request.headers.get('X-Hub-Signature').split('sha1=')[-1].strip()
    if not hmac.compare_digest(incoming_signature, expected_signature):
        return False
    return True


#app.run(host="0.0.0.0",port=80)