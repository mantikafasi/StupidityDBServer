from git import Repo
import json
import os
def existsInJsonArray(array, value):
    for item in array:
        if value in item:
            return True
    return False
class Manager:
    def __init__(self) -> None:
        pass

    
    
    def addTheme(self, themeInfo:dict,theme: dict) -> None:
        # gets into themes folder adds theme json and commits the changes to github
        with open("ThemeRepo/themeList.json", "r") as f:
            themeList = json.load(f)
            
            with open ("ThemeRepo/themeList.json", "w+") as f:
                json.dump(themeList,indent=4,fp = f)
            
            if existsInJsonArray(themeList, themeInfo["name"]):
                return "Theme already exists"
            themeList.append(themeInfo)

    
        with open("ThemeRepo/themes/" + themeInfo["name"] + ".json", "x+") as f:
            json.dump(theme,indent=4, fp=f)
        
        repo = Repo(".\ThemeRepo")
        repo.git.add(all=True)
        repo.index.commit("Added theme " + themeInfo["name"])
        origin = repo.remote(name='origin')
        origin.push()
        return "Successful"


# TESTS

#manager = Manager()

# manager.addTheme(json.loads(
#     """
#         {
#         "name":"Theme Name",
#         "description":"Theme Description",
#         "author":"Author Name",
#         "authorid":"00000000000000",
#         "screenshots":[
#             "http://example.com/screenshot1.png",
#             "http://example.com/screenshot2.png"
#         ],
#         "tags":[
#             "tag1",
#             "tag2"
#         ]
#     }"""
# ),{"guh":"guh"})

        

        