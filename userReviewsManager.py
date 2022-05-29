class Review:
    def __init__(self,userid,senderUserID:int,comment:str,star:int):
        self.userid = userid
        self.senderUserID = senderUserID
        self.comment = comment
        self.star = star

class Manager:
    def __init__(self, manager):
        self.manager = manager

    def cursor(self):
        return self.manager.cursor()

    def addReview(review:Review):
        #TODO
        pass

    def getReviews(userid:int):
        #TODO
        pass


