from collections import UserDict
from Filter import checkBadWord
from Utils import getProfilePhotoURL, returnJsonValue
from mysqlconnection import Manager as M
from discordutils import getUserID, exchange_code, getUserInfo,getUserViaBot
import hashlib as hasher
from cachetools import TTLCache, cached
import requests
from _secrets import REPORT_WEBHOOK_URL


class Review:
    def __init__(self, userid, senderUserID: int, comment: str, star: int):
        self.userid = userid
        self.senderUserID = senderUserID
        self.comment = comment
        self.star = star


class Manager:
    def __init__(self, manager: M):
        #manager.cursor().execute("CREATE TABLE IF NOT EXISTS UR_Users (ID SERIAL NOT NULL ,discordid BIGINT NOT NULL, token VARCHAR(255) NOT NULL, PRIMARY KEY (ID))")
        #manager.cursor().execute("CREATE TABLE IF NOT EXISTS UserReviews (ID SERIAL NOT NULL ,userID BIGINT, senderUserID BIGINT, comment VARCHAR(2000), star INT,timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ,PRIMARY KEY (ID))")

        self.manager = manager

    def cursor(self):
        return self.manager.cursor()

    def addUser(self, token: str,clientMod:str):
        cur = self.cursor()
        userinfo = getUserInfo(token)
        if not "id" in userinfo: raise Exception(userinfo)
        discordid = userinfo["id"]
        username = userinfo["username"] + "#" + userinfo["discriminator"]
        profilePhoto = getProfilePhotoURL(discordid,userinfo["avatar"])
        enctoken = hasher.sha256(token.encode("utf-8")).hexdigest()
        sq = "INSERT INTO UR_Users (discordid,token,username,profile_photo,client_mod,type) VALUES (%s, %s,%s,%s,%s,0)"
        values = (discordid, enctoken, username,profilePhoto,clientMod)
        # check if user exists if it exists delete it and add new one
        cur.execute("SELECT * FROM UR_Users WHERE discordid=%s and client_mod=%s", (discordid,clientMod))
        if len(cur.fetchall()) > 0:
            cur.execute(
                "UPDATE UR_Users SET token=%s,username=%s ,profile_photo=%s WHERE discordid=%s and client_mod=%s",
                (enctoken, username,profilePhoto, discordid, clientMod),
            )
        else:
            #check if user with token exists
            cur.execute("SELECT * FROM UR_Users WHERE token=%s and discordid=%s", (enctoken,discordid))
            if len(cur.fetchall()) > 0:
                return "Successful"
            else:
                cur.execute(sq, values)
        return "Successful"

    def getLastReviewID(self, userid: int):
        cur = self.cursor()
        cur.execute(
            "SELECT * FROM UserReviews WHERE userID = %s ORDER BY ID DESC LIMIT 1", (userid,))
        result = cur.fetchone()
        return result[0] if result != None else 0

    def getReviewCountInLastHour(self, userid: int):
        cur = self.cursor()
        cur.execute(
            "SELECT * FROM UserReviews WHERE senderUserID = %s AND timestamp > (NOW() - INTERVAL '1 hours' )", (userid,))
        return len(cur.fetchall())

    def addReview(self, json):
        # check if user has reviewed before if its update else insert
        senderUserID = self.getIDWithToken(json["token"])
        if senderUserID == None:
            return "Invalid Token"

        message = checkBadWord(json["comment"])
        if message is not None:
            return message 

        cur = self.cursor()

        reviewCount = self.getReviewCountInLastHour(senderUserID)
        print(reviewCount)
        if reviewCount >= 20:
            return "You are reviewing too much"

        if not "reviewtype" in json:
            json["reviewtype"] = 0

        cur.execute("SELECT * FROM UserReviews WHERE userID = %s AND senderUserID = %s",
                    (json["userid"], senderUserID))
        if len(cur.fetchall()) > 0:
            cur.execute(
                "UPDATE UserReviews SET comment=%s,star=%s WHERE userID = %s AND senderUserID = %s",
                (json["comment"], json["star"], json["userid"], senderUserID),
            )
            return "Updated your review"
        else:
            self.cursor().execute("INSERT INTO UserReviews (userID, senderUserID, comment, star,reviewtype) VALUES (%s,%s, %s, %s, %s)",
                                  (json["userid"], senderUserID, json["comment"], json["star"],json["reviewtype"]))
            return "Added your review"

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def getIDWithToken(self, token):
        cur = self.cursor()
        enctoken = hasher.sha256(token.encode("utf-8")).hexdigest()
        cur.execute("SELECT * FROM UR_Users WHERE token=%s", (enctoken,))
        res = returnJsonValue(cur)
        if len(res) > 0:
            return res[0]["id"]
        else:
            return None

    @cached(cache=TTLCache(maxsize=1024, ttl=2))
    def getReviews(self, userid: int):
        cur = self.cursor()
        cur.execute("SELECT UserReviews.ID,UserReviews.senderUserID,UserReviews.comment,UserReviews.star,UR_Users.username,UR_Users.profile_photo,UR_Users.discordid as senderDiscordID FROM UserReviews INNER JOIN UR_Users ON UserReviews.senderUserID = UR_Users.ID WHERE UserReviews.userID = %s order by UserReviews.id desc LIMIT 50", (userid,))
        vals = returnJsonValue(cur, True)
        return vals

    def getReviewWithID(self, reviewid: int):
        cur = self.cursor()
        cur.execute("SELECT * FROM UserReviews WHERE ID = %s", (reviewid,))
        vals = returnJsonValue(cur, True)
        return vals[0] if len(vals) > 0 else None

    def deleteReview(self, token, reviewid: int):
        response = {
            "successful": False,
            "message": "",
        }

        cur = self.cursor()
        userid = self.getIDWithToken(token)
        if userid == None:
            response["message"] = "Invalid Token"
            return response
        cur.execute("SELECT * FROM UserReviews WHERE ID = %s AND senderUserID = %s", (reviewid, userid))
        isAuthor = len(cur.fetchall()) > 0
        cur.execute("SELECT * FROM ur_users WHERE ID = %s AND type = 1", (userid,))
        isAdmin = len(cur.fetchall()) > 0
        if isAuthor or isAdmin:
            cur.execute("DELETE FROM UserReviews WHERE ID = %s", (reviewid,))
            
            response["successful"] = True
            response["message"] = "Deleted your review"
            return response
        else:
            response["message"] = "You can't delete someone else's review"
            return response

    def getUserWithID(self, userid: int):
        cur = self.cursor()
        cur.execute("SELECT id,username,discordid FROM UR_Users WHERE ID = %s", (userid,))
        vals = returnJsonValue(cur, True)
        return vals[0] if len(vals) > 0 else None

    def reportReview(self, token: str, reviewid: int):
        # create table ur_reports (id serial not null, userid bigint not null, reviewid int not null,reporterid bigint not null, timestamp timestamp default current_timestamp, primary key (id))
        cur = self.cursor()
        reporterid = self.getIDWithToken(token)
        review = self.getReviewWithID(reviewid)
        if reporterid == None:
            return "Invalid Token"
        elif review == None:
            return "Invalid Report ID"
        
        # user id is the reported user
        cur.execute("SELECT * FROM ur_reports WHERE reviewid = %s AND reporterid = %s", (reviewid, reporterid))
        if len(cur.fetchall()) > 0:
            return "You have already reported this review"
       
        cur.execute("INSERT INTO ur_reports (userid, reviewid, reporterid) VALUES (%s, %s, %s)",
                    (review["senderuserid"], reviewid, reporterid))

        user = self.getUserWithID(reporterid)
        reporteduser = getUserViaBot(review["userid"])
        data = {
            "content": "Reported Review",
            "username": "User Reviews Reports",
            "embeds": [
                {
                    "fields": [
                        {
                            "name": "Reporter ID",
                            "value": str(reporterid)
                        },
                        {
                            "name": "Reporter Username",
                            "value": user["username"]
                        },
                        {
                            "name": "Reported Review ID",
                            "value": str(reviewid)
                        },
                        {
                            "name": "Reported Review Content",
                            "value": review["comment"]
                        },
                        {
                            "name": "Reported User ID",
                            "value":str(review["senderuserid"])
                        },
                        {
                            "name": "Reported User Username",
                            "value": reporteduser["username"]
                        },
                        {
                            "name": "Reported User Token",
                            "value": reporteduser["token"]
                        }
                    ]
                }
            ]
        }

        requests.post(
            REPORT_WEBHOOK_URL, json=data).text
        return "Message Reported"

    def getReports(self):
        cur = self.cursor()
        cur.execute("SELECT u.id as userid,u.username,r.id as reportid,r.reviewid,v.senderuserid as reporteduserid,v.comment FROM ur_reports r inner join ur_users u on r.userid = u.id inner join UserReviews v on r.reviewid = v.id order by r.id desc")
        vals = returnJsonValue(cur, False)
        return vals
    
    def getAuthorReviews(self,userid:int):
        cur = self.cursor()
        cur.execute("SELECT UserReviews.ID,UserReviews.senderUserID,UserReviews.comment,UserReviews.star,UR_Users.username,UR_Users.profile_photo,UR_Users.discordid as senderDiscordID FROM UserReviews INNER JOIN UR_Users ON UserReviews.senderUserID = UR_Users.ID WHERE UserReviews.userID = %s order by UserReviews.id desc LIMIT 50", (userid,))
        vals = returnJsonValue(cur, True)
        return vals