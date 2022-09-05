import requests
from _secrets import CLIENT_ID, CLIENT_SECRET,BOT_TOKEN

API_ENDPOINT = "https://discord.com/api/v10"
REDIRECT_URI = "https://manti.vendicated.dev/auth"

def exchange_code(code,redirect_uri=REDIRECT_URI):
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post("%s/oauth2/token" % API_ENDPOINT, data=data, headers=headers)
    r.raise_for_status()
    return r.json()["access_token"]


def getUserID(token):
    heder = {"Authorization": f"Bearer {token}"}
    res = requests.get("https://discord.com/api/v8/users/@me", headers=heder).json()
    return res["id"]


def getUserInfo(token):
    res = requests.get("https://discord.com/api/v8/users/@me", headers= {"Authorization": f"Bearer {token}"}).json()
    return res

def getUserViaBot(userid,bottoken = BOT_TOKEN):
    return requests.get(f"https://discord.com/api/v10/users/{userid}",headers = {"Authroization":f"Bot {token}"}).json()
