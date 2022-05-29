import hashlib as hasher
import json

import mysql.connector
from cachetools import LRUCache, TTLCache, cached
from mysql.connector import cursor

getPostsQuery = "SELECT p.discordid, p.stupitity FROM stupit_table p "


class Vote:
    def __init__(self, discordid: int, senderdiscordid: int, stupidity: int):
        self.discordid = discordid
        self.stupidity = stupidity
        self.senderdiscordid = senderdiscordid

    def __str__(self):
        return "{} {} {}".format(self.discordid, self.senderdiscordid, self.stupidity)


class Manager:
    def __init__(self, manager):
        self.manager = manager

    def getSql(self):
        return self.manager.sql

    def cursor(self):
        return self.manager.cursor()

    # checks if the user has already voted ; returns true if he has
    def checkVote(self, vote: Vote):
        cur = self.cursor()
        cur.execute(
            "SELECT * FROM stupit_table WHERE discordid=%s AND senderdiscordid=%s LIMIT 2",
            (vote.discordid, vote.senderdiscordid),
        )
        length = len(cur.fetchall())
        print(length)
        return 0 < length

    def addUserInfo(self, discordid: int, token: str,username:str):
        cur = self.cursor()
        enctoken = hasher.sha256(token.encode("utf-8")).hexdigest()
        sq = "INSERT INTO user_info(username,discordid,token) VALUES (%s ,%s, %s)"
        values = (username,discordid, enctoken)
        # check if user exists if it exists delete it and add new one
        cur.execute("SELECT * FROM user_info WHERE discordid=%s", (discordid,))
        if len(cur.fetchall()) > 0:
            cur.execute(
                "UPDATE user_info SET token=%s ,username=%s WHERE discordid=%s",
                (enctoken,username, discordid),
            )
        else:
            cur.execute(sq, values)

        return "Successful"

    def getUserIdWithToken(self, token):
        cur = self.cursor()
        enctoken = hasher.sha256(token.encode("utf-8")).hexdigest()
        cur.execute("SELECT * FROM user_info WHERE token=%s", (enctoken,))
        res = self.returnJsonValue(cur)
        if len(res) > 0:
            return res[0]["discordid"]
        else:
            return None

    def getUserWithToken(self,token):
        #lazy to edit code, so just copied and edited it
        cur = self.cursor()
        enctoken = hasher.sha256(token.encode("utf-8")).hexdigest()
        cur.execute("SELECT * FROM user_info WHERE token=%s", (enctoken,))
        res = self.returnJsonValue(cur)
        if len(res) > 0:
            return res[0]
        else:
            return None

    @cached(cache=TTLCache(maxsize=1024, ttl=86400))
    def getUserData(self, discordid: int):
        cur = self.cursor()
        cur.execute(getPostsQuery + "WHERE p.discordid= %s", (discordid,))

        values = self.returnJsonValue(cur)
        cur.close()
        if len(values) == 0:
            return None
        meanval = 0
        for value in values:
            if value["stupitity"] != None:
                meanval += value["stupitity"]
        meanval = meanval / len(values)
        return int(meanval)

    def addVote(self, vote: Vote):
        if vote.stupidity > 100 or vote.stupidity < 0:
            return "Vote should be between 0 and 100"
        if not self.checkVote(vote):
            cur = self.cursor()
            sq = "INSERT INTO stupit_table(discordid,stupitity ,senderdiscordid) VALUES (%s, %s ,%s)"
            values = (vote.discordid, vote.stupidity, vote.senderdiscordid)
            cur.execute(sq, values)
            return "Successful"
        else:
            # update vote
            cur = self.cursor()
            sq = "UPDATE stupit_table SET stupitity=%s WHERE discordid=%s AND senderdiscordid=%s"
            values = (vote.stupidity, vote.discordid, vote.senderdiscordid)
            cur.execute(sq, values)
            return "Your Vote Updated"

    def returnJsonValue(self, cur):
        row_headers = [x[0] for x in cur.description]
        rv = cur.fetchall()
        json_data = []
        for result in rv:
            json_data.append(dict(zip(row_headers, result)))
        return json_data
