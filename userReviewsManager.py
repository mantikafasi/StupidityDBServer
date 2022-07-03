from Utils import returnJsonValue
from mysqlconnection import Manager as M
from discordutils import getUserID,exchange_code, getUserInfo
import hashlib as hasher
from cachetools import TTLCache, cached


class Review:
    def __init__(self,userid,senderUserID:int,comment:str,star:int):
        self.userid = userid
        self.senderUserID = senderUserID
        self.comment = comment
        self.star = star

class Manager:
    def __init__(self, manager:M):
        #manager.cursor().execute("CREATE TABLE IF NOT EXISTS UR_Users (ID SERIAL NOT NULL ,discordid BIGINT NOT NULL, token VARCHAR(255) NOT NULL, PRIMARY KEY (ID))")
        #manager.cursor().execute("CREATE TABLE IF NOT EXISTS UserReviews (ID SERIAL NOT NULL ,userID BIGINT, senderUserID BIGINT, comment VARCHAR(2000), star INT,timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ,PRIMARY KEY (ID))")

        self.manager = manager
        
    def cursor(self):
        return self.manager.cursor()

    def addUser(self,token: str):
        cur = self.cursor()
        userinfo = getUserInfo(token)
        discordid = userinfo["id"]
        username = userinfo["username"] +"#" + userinfo["discriminator"]
        enctoken = hasher.sha256(token.encode("utf-8")).hexdigest()
        sq = "INSERT INTO UR_Users (discordid,token,username) VALUES (%s, %s,%s)"
        values = (discordid, enctoken,username)
        # check if user exists if it exists delete it and add new one
        cur.execute("SELECT * FROM UR_Users WHERE discordid=%s", (discordid,))
        if len(cur.fetchall()) > 0:
            cur.execute(
                "UPDATE UR_Users SET token=%s,username=%s WHERE discordid=%s",
                (enctoken,username, discordid),
            )
        else:
            cur.execute(sq, values)
        return "Successful"

    def getReviewCountInLastHour(self,userid:int):
        cur = self.cursor()
        cur.execute("SELECT * FROM UserReviews WHERE senderUserID = %s AND timestamp > NOW() - INTERVAL 1 HOUR",(userid,))
        return len(cur.fetchall())

    def addReview(self,json):
        #check if user has reviewed before if its update else insert
        senderUserID = self.getIDWithToken(json["token"])
        if senderUserID == None:
            return "Invalid Token"
        cur = self.cursor()

        reviewCount = self.getReviewCountInLastHour(senderUserID)
        print(reviewCount)
        if reviewCount >= 20:
            return "You are reviewing too much"
        
        cur.execute("SELECT * FROM UserReviews WHERE userID = %s AND senderUserID = %s",(json["userid"],senderUserID))
        if len(cur.fetchall()) > 0:
            cur.execute(
                "UPDATE UserReviews SET comment=%s,star=%s WHERE userID = %s AND senderUserID = %s",
                (json["comment"],json["star"],json["userid"],senderUserID),
            )
            return "Updated your review"
        else:
            self.cursor().execute("INSERT INTO UserReviews (userID, senderUserID, comment, star) VALUES (%s, %s, %s, %s)", (json["userid"], senderUserID, json["comment"], json["star"]))
            return "Added your review"

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def getIDWithToken(self,token):
        cur = self.cursor()
        enctoken = hasher.sha256(token.encode("utf-8")).hexdigest()
        cur.execute("SELECT * FROM UR_Users WHERE token=%s", (enctoken,))
        res = returnJsonValue(cur)
        if len(res) > 0:
            return res[0]["id"]
        else:
            return None

    @cached(cache=TTLCache(maxsize=1024, ttl=60))
    def getReviews(self,userid:int):
        cur = self.cursor()
        cur.execute("SELECT UserReviews.senderUserID,UserReviews.comment,UserReviews.star,UR_Users.username,UR_Users.discordid as senderDiscordID FROM UserReviews INNER JOIN UR_Users ON UserReviews.senderUserID = UR_Users.ID WHERE UserReviews.userID = %s",(userid,))
        vals = returnJsonValue(cur)
        return vals

