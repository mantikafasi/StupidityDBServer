from Utils import returnJsonValue
from mysqlconnection import Manager as M

class Review:
    def __init__(self,userid,senderUserID:int,comment:str,star:int):
        self.userid = userid
        self.senderUserID = senderUserID
        self.comment = comment
        self.star = star

class Manager:
    def __init__(self, manager:M):
        manager.cursor().execute("CREATE TABLE IF NOT EXISTS UserReviews (userID INT, senderUserID INT, comment VARCHAR(2000), star INT)")
        self.manager = manager
        

    def cursor(self):
        return self.manager.cursor()

    def addReview(self,review:Review):
        #adds review
        self.cursor().execute("INSERT INTO UserReviews (userID, senderUserID, comment, star) VALUES (%s, %s, %s, %s)", (review.userid, review.senderUserID, review.comment, review.star))

    def getReviews(self,userid:int):
        cur = self.cursor()
        cur.execute("SELECT UserReviews.senderUserID,UserReviews.comment,UserReviews.star,user_info.username FROM UserReviews INNER JOIN user_info ON UserReviews.senderUserID = user_info.userID WHERE UserReviews.userID = %s",(userid,))
        vals = returnJsonValue(cur)
        return vals

