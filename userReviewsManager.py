from Utils import returnJsonValue
from mysqlconnection import Manager as M
from discordutils import getUserID,exchange_code, getUserInfo
import hashlib as hasher

class Review:
    def __init__(self,userid,senderUserID:int,comment:str,star:int):
        self.userid = userid
        self.senderUserID = senderUserID
        self.comment = comment
        self.star = star

class Manager:
    def __init__(self, manager:M):
        manager.cursor().execute("CREATE TABLE IF NOT EXISTS UR_Users (ID INT NOT NULL AUTO_INCREMENT,username VARCHAR(80),discordid VARCHAR(255) NOT NULL, token VARCHAR(255) NOT NULL, PRIMARY KEY (ID))")
        manager.cursor().execute("CREATE TABLE IF NOT EXISTS UserReviews (userID INT, senderUserID INT, comment VARCHAR(2000), star INT)")
        self.manager = manager
        
    def cursor(self):
        return self.manager.cursor()

    def addUser(self,discordid: int, token: str):
        cur = self.cursor()
        userinfo = getUserInfo(token)
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


    def addReview(self,review:Review):
        #adds review
        self.cursor().execute("INSERT INTO UserReviews (userID, senderUserID, comment, star) VALUES (%s, %s, %s, %s)", (review.userid, review.senderUserID, review.comment, review.star))

    def getReviews(self,userid:int):
        cur = self.cursor()
        cur.execute("SELECT UserReviews.senderUserID,UserReviews.comment,UserReviews.star,user_info.username FROM UserReviews INNER JOIN user_info ON UserReviews.senderUserID = user_info.userID WHERE UserReviews.userID = %s",(userid,))
        vals = returnJsonValue(cur)
        return vals

