from collections import UserDict
from Filter import checkBadWord
from Utils import getProfilePhotoURL, returnJsonValue
from mysqlconnection import Manager as M
from discordutils import getUserID, exchange_code, getUserInfo, getUserViaBot
import hashlib as hasher
from cachetools import TTLCache, cached
import requests
from _secrets import REPORT_WEBHOOK_URL, BOT_TOKEN


class Review:
    def __init__(self, userid, senderUserID: int, comment: str, star: int):
        self.userid = userid
        self.senderUserID = senderUserID
        self.comment = comment
        self.star = star


class Manager:
    def __init__(self, manager: M):
        # manager.cursor().execute("CREATE TABLE IF NOT EXISTS users (ID SERIAL NOT NULL ,discordid BIGINT NOT NULL, token VARCHAR(255) NOT NULL, PRIMARY KEY (ID))")
        # manager.cursor().execute("CREATE TABLE IF NOT EXISTS UserReviews (ID SERIAL NOT NULL ,userID BIGINT, senderUserID BIGINT, comment VARCHAR(2000), star INT,timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ,PRIMARY KEY (ID))")

        self.manager = manager

    def cursor(self):
        return self.manager.cursor()

    def addUser(self, token: str, clientMod: str):
        cur = self.cursor()
        userinfo = getUserInfo(token)
        if not "id" in userinfo:
            raise Exception(userinfo)
        discordid = userinfo["id"]
        username = userinfo["username"] + "#" + userinfo["discriminator"]
        profilePhoto = getProfilePhotoURL(discordid, userinfo["avatar"])
        enctoken = hasher.sha256(token.encode("utf-8")).hexdigest()
        sq = "INSERT INTO users (discordid,token,username,profile_photo,client_mod,type) VALUES (%s, %s,%s,%s,%s,0)"
        values = (discordid, enctoken, username, profilePhoto, clientMod)
        # check if user exists if it exists delete it and add new one
        cur.execute(
            "SELECT * FROM users WHERE discordid=%s and client_mod=%s",
            (discordid, clientMod),
        )
        if len(cur.fetchall()) > 0:
            cur.execute(
                "UPDATE users SET token=%s,username=%s ,profile_photo=%s WHERE discordid=%s and client_mod=%s",
                (enctoken, username, profilePhoto, discordid, clientMod),
            )
        else:
            # check if user with token exists
            cur.execute(
                "SELECT * FROM users WHERE token=%s and discordid=%s",
                (enctoken, discordid),
            )
            if len(cur.fetchall()) > 0:
                return "Successful"
            else:
                cur.execute(sq, values)
        return "Successful"

    def getLastReviewID(self, userid: int):
        cur = self.cursor()
        cur.execute(
            "SELECT * FROM UserReviews WHERE userID = %s ORDER BY ID DESC LIMIT 1",
            (userid,),
        )
        result = cur.fetchone()
        return result[0] if result != None else 0

    def getReviewCountInLastHour(self, userid: int):
        cur = self.cursor()
        cur.execute(
            "SELECT * FROM UserReviews WHERE senderUserID = %s AND timestamp > (NOW() - INTERVAL '1 hours' )",
            (userid,),
        )
        return len(cur.fetchall())

    def addReview(self, json):
        # check if user has reviewed before if its update else insert

        user = self.getUserWithToken(token=json["token"])
        if user == None:
            return "Invalid User"

        if user["type"] == -1:
            return "You have been banned from UserReviews"

        senderUserID = user["id"]
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

        cur.execute(
            "SELECT * FROM UserReviews WHERE userID = %s AND senderUserID = %s",
            (json["userid"], senderUserID),
        )
        if len(cur.fetchall()) > 0:
            cur.execute(
                "UPDATE UserReviews SET comment=%s,star=%s WHERE userID = %s AND senderUserID = %s",
                (json["comment"], json["star"], json["userid"], senderUserID),
            )
            return "Updated your review"
        else:
            self.cursor().execute(
                "INSERT INTO UserReviews (userID, senderUserID, comment, star,reviewtype) VALUES (%s,%s, %s, %s, %s)",
                (
                    int(json["userid"]),
                    senderUserID,
                    json["comment"],
                    json["star"],
                    json["reviewtype"],
                ),
            )
            return "Added your review"

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def getIDWithToken(self, token):
        cur = self.cursor()
        enctoken = hasher.sha256(token.encode("utf-8")).hexdigest()
        cur.execute("SELECT * FROM users WHERE token=%s", (enctoken,))
        res = returnJsonValue(cur)
        if len(res) > 0:
            return res[0]["id"]
        else:
            return None

    @cached(cache=TTLCache(maxsize=1024, ttl=10))
    def getUserWithToken(self, token):
        cur = self.cursor()
        enctoken = hasher.sha256(token.encode("utf-8")).hexdigest()
        cur.execute("SELECT * FROM users WHERE token=%s", (enctoken,))
        vals = returnJsonValue(cur, True)
        return vals[0] if len(vals) > 0 else None

    @cached(cache=TTLCache(maxsize=1024, ttl=2))
    def getReviews(self, userid: int):
        cur = self.cursor()
        cur.execute(
            "SELECT reviews.ID,reviews.senderUserID,reviews.comment,reviews.star,users.username,users.profile_photo,users.discordid as senderDiscordID FROM UserReviews INNER JOIN users ON reviews.senderUserID = users.ID WHERE reviews.userID = %s order by reviews.id desc LIMIT 50",
            (userid,),
        )
        vals = returnJsonValue(cur, True)
        for review in vals:
            review["badges"] = self.getBadgesOfUser(review["senderdiscordid"])
        return vals

    @cached(cache=TTLCache(maxsize=1024, ttl=2))
    def getReviewsByQuery(self, query: str):
        cur = self.cursor()
        cur.execute(
            "SELECT reviews.ID,reviews.reviewer_id,reviews.comment,users.username,users.avatar_url,users.discord_id as senderDiscordID FROM reviews INNER JOIN users ON reviews.reviewer_id = users.ID WHERE reviews.comment LIKE %s order by reviews.id desc LIMIT 50",
            ("%" + query + "%",),
        )
        vals = returnJsonValue(cur)
        return vals

    def getReviewWithID(self, reviewid: int):
        cur = self.cursor()
        cur.execute(
            "SELECT reviews.ID,reviews.reviewer_id,reviews.comment,users.username,users.avatar_url,users.discord_id as senderDiscordID FROM reviews INNER JOIN users ON reviews.reviewer_id = users.ID WHERE reviews.id = %s order by reviews.id desc LIMIT 50",
            (reviewid,),
        )
        vals = returnJsonValue(cur, True)
        return vals[0] if len(vals) > 0 else None

    def isUserAdmin(self, token):
        if token == BOT_TOKEN:
            return True

        cur = self.cursor()
        enctoken = hasher.sha256(token.encode("utf-8")).hexdigest()
        cur.execute("SELECT * FROM users WHERE token=%s and type = 1", (enctoken,))

        return len(cur.fetchall()) > 0

    def isUserAdminID(self,discordid):
        cur = self.cursor()
        cur.execute("SELECT * FROM users WHERE discord_id=%s and type = 1", (discordid,))
        return len(cur.fetchall()) > 0

    def deleteReview(self, token, reviewid: int):
        response = {
            "successful": False,
            "message": "",
        }

        cur = self.cursor()
        userid = self.getIDWithToken(token)
        if (userid == None) and (token != BOT_TOKEN):
            response["message"] = "Invalid Token"
            return response

        cur.execute(
            "SELECT * FROM reviews WHERE ID = %s AND reviewer_id = %s",
            (reviewid, userid),
        )
        isAuthor = len(cur.fetchall()) > 0

        isAdmin = self.isUserAdmin(token)

        if isAuthor or isAdmin:
            cur.execute("DELETE FROM reviews WHERE ID = %s", (reviewid,))

            response["successful"] = True
            response["message"] = "Deleted your review"
            return response
        else:
            response["message"] = "You can't delete someone else's review"
            return response

    def getUserWithID(self, userid: int):
        cur = self.cursor()
        cur.execute(
            "SELECT id,username,discord_id FROM users WHERE ID = %s", (userid,)
        )
        vals = returnJsonValue(cur, True)
        return vals[0] if len(vals) > 0 else None

    def banUser(self, token, userid):
        response = {
            "successful": False,
            "message": "",
        }

        cur = self.cursor()
        isAdmin = self.isUserAdmin(token)

        if not isAdmin:
            response["message"] = "You are not authorized stupit"
            return response

        cur.execute("UPDATE users SET type = -1 WHERE ID = %s", (userid,))
        response["successful"] = True
        response["message"] = "Banned user"
        return response

    def unbanUser(self, token, userid):
        response = {
            "successful": False,
            "message": "",
        }

        cur = self.cursor()
        isAdmin = self.isUserAdmin(token)

        if not isAdmin:
            response["message"] = "You are not authorized stupit"
            return response

        cur.execute("UPDATE users SET type = 0, ban_id = NULL, warning_count = GREATEST(0, warning_count - 1) WHERE ID = %s", (userid,))
        response["successful"] = True
        response["message"] = "Unbanned user"
        return response

    def getUserWithDiscordId(self, discordid: int):
        cur = self.cursor()
        cur.execute(
            "SELECT id,username,discord_id FROM users WHERE discord_id = %s",
            (discordid,),
        )
        return vals[0] if len(vals) > 0 else None

    def sendNotification(self, user_discord_id, message):
        cur = self.cursor()

        user = self.getUserWithDiscordId(user_discord_id)

        cur.execute("INSERT INTO notifications (user_id, text) VALUES (%s, %s)", (user["id"], message))
        return "Successful"

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
        cur.execute(
            "SELECT * FROM ur_reports WHERE reviewid = %s AND reporterid = %s",
            (reviewid, reporterid),
        )
        if len(cur.fetchall()) > 0:
            return "You have already reported this review"

        cur.execute(
            "INSERT INTO ur_reports (userid, reviewid, reporterid) VALUES (%s, %s, %s)",
            (review["senderuserid"], reviewid, reporterid),
        )

        user = self.getUserWithID(reporterid)
        reporteduser = getUserViaBot(review["senderdiscordid"])
        data = {
            "content": "Reported Review",
            "username": "User Reviews Reports",
            "embeds": [
                {
                    "fields": [
                        {"name": "Reporter ID", "value": str(reporterid)},
                        {"name": "Reporter Username", "value": user["username"]},
                        {
                            "name": "Reported User Username",
                            "value": reporteduser["username"],
                        },
                        {"name": "Reported Review ID", "value": str(reviewid)},
                        {"name": "Reported Review Content", "value": review["comment"]},
                        {
                            "name": "Reported User ID",
                            "value": str(review["senderuserid"]),
                        },
                    ]
                }
            ],
        }

        requests.post(REPORT_WEBHOOK_URL, json=data).text
        return "Message Reported"

    def getReports(self):
        cur = self.cursor()
        cur.execute(
            "SELECT u.id as userid,u.username,r.id as reportid,r.reviewid,v.senderuserid as reporteduserid,v.comment FROM ur_reports r inner join users u on r.userid = u.id inner join UserReviews v on r.reviewid = v.id order by r.id desc"
        )
        vals = returnJsonValue(cur, False)
        return vals

    def getAuthorReviews(self, userid: int):
        cur = self.cursor()
        cur.execute(
            "SELECT reviews.ID,reviews.senderUserID,reviews.comment,reviews.star,users.username,users.profile_photo,users.discordid as senderDiscordID FROM UserReviews INNER JOIN users ON reviews.senderUserID = users.ID WHERE reviews.userID = %s order by reviews.id desc LIMIT 50",
            (userid,),
        )
        vals = returnJsonValue(cur, True)
        return vals

    #CREATE TABLE UserBadges (id serial not null, discordid bigint not null, badge_name varchar(255) not null,badge_icon varchar(255) not null,redirect_url varchar(255) ,primary key (id))
    @cached(cache=TTLCache(maxsize=1024, ttl=60))
    def getBadgesOfUser(self, discordid: int):
        badges = self.getAllBadges()
        return [badge for badge in badges if badge["discordid"] == discordid]
    
    @cached(cache=TTLCache(maxsize=1024, ttl=60))
    def getAllBadges(self):
        cur = self.cursor()
        cur.execute(
            "SELECT discordid,badge_name,badge_icon,redirect_url FROM UserBadges"
        )
        badges = returnJsonValue(cur, True)
        cur.close()
        cur = self.cursor()
        cur.execute("SELECT DISTINCT discordid,type FROM users where type = -1 or type = 1")
        for result in cur.fetchall():
            badges.append({"discordid": result[0], "badge_name": "Banned" if result[1] == -1 else "Admin", "badge_icon": "https://cdn.discordapp.com/emojis/399233923898540053.gif?size=128" if result[1] == -1 else "https://cdn.discordapp.com/emojis/1040004306100826122.gif?size=128", "redirect_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
        cur.close()

        badges += self.getVencordBadges()
        
        return badges

    def getVencordBadges(self):
        vencordbadges = requests.get("https://gist.githubusercontent.com/Vendicated/51a3dd775f6920429ec6e9b735ca7f01/raw/badges.csv").text
        badges = []
        for line in vencordbadges.split("\n")[1:-1]:
            badge = line.split(",")
            badges.append({"discordid": badge[0], "badge_name": badge[1], "badge_icon": badge[2], "redirect_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
        return badges
        
    def addBadge(self, discordid: int, badge_name: str, badge_icon: str, redirect_url: str):
        try:
            cur = self.cursor()
        
            cur.execute("SELECT * FROM user_badges WHERE target_discord_id = %s AND name = %s", (discordid,badge_name))
            if len(cur.fetchall()) > 0:
                return "Badge already exists"
            
            
            cur.execute("INSERT INTO user_badges (target_discord_id,name,icon_url,redirect_url) VALUES (%s,%s,%s,%s)", (discordid,badge_name,badge_icon,redirect_url))
            cur.close()
            return "Successful"
        except Exception as e:
            return str(e)

    def deleteAllReviewsOfUser(self, userid: int):
        cur = self.cursor()
        cur.execute("DELETE FROM reviews WHERE reviewer_id = %s", (userid,))
        cur.close()
