import json


from _secrets import BOT_VOTE_TOKEN, BOT_TOKEN

import discord
import requests

from discord.ext import commands
from mysqlconnection import Manager
from userReviewsManager import Manager as UserReviewsManager


psql = Manager()
manager = UserReviewsManager(psql)

bot = commands.Bot(command_prefix=".",intents=discord.Intents.all())

@bot.event
async def on_ready():
    print("Logged In As")
    print(bot.user.name)
    print("------")
    print(bot.user.id)
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, name="Nothing")
    )


@bot.listen()
async def on_message(message):  # legacy
    pass

@bot.command("search")
async def searchReview(ctx,*,query):
    if query == None:
        return await ctx.send("Put a query dumbass")
    reviews = manager.getReviewsByQuery(query)

    embeds = []

    for review in reviews[0:10]:
        reviewEmbed = discord.Embed(title = "Comment",description=review["comment"])
        reviewEmbed.add_field(name = "Sender Discord ID",value = str(review["senderdiscordid"]))
        reviewEmbed.add_field(name = "Sender User ID",value = str(review["senderuserid"]))
        reviewEmbed.add_field(name = "Review ID", value = str(review["id"]) )
        embeds.append(reviewEmbed)

        #embed.add_field(name= review["username"],value="User ID:" + str(review["senderdiscordid"]) +"\nComment:" + review["comment"] )
    
    if (len(embeds) == 0): embeds.append(discord.Embed(title = "Not Found",description=f"A review that contains {query} not found!"))
    await ctx.send(embeds=embeds)


adminListBlaBla = [287555395151593473,343383572805058560]
@bot.command("delete")
async def deleteReview(ctx,*,reviewids):
    if not (ctx.author.id in adminListBlaBla):
        await ctx.send("You are not authrorized to delete reviews")
        return

    reviews = []
    if (" " in reviewids):
        reviews = reviewids.split(" ")
    else:
        reviews = [reviewids,]

    embed = discord.Embed(title = "Status")

    for id in reviews:
        resp = manager.deleteReview(BOT_TOKEN, id)
        if resp["successful"]:
            embed.add_field(name="Success",value="Deleted review with ID:" + id)
        else :
            embed.add_field(name="Fail",value="Failed to delete review with ID:" + id)

    await ctx.send(embed=embed)

@bot.command("ban")
async def banUser(ctx,*,userids):
    if not (ctx.author.id in adminListBlaBla):
        await ctx.send("You are not authrorized to ban users blabla")
        return    
   
    users = []

    if (" " in userids):
        users = userids.split(" ")
    else : users = [userids,]

    embed = discord.Embed(title = "Status")
    embed.set_footer(text = "Ven Will Die")

    for user in users:
        resp = manager.banUser(BOT_TOKEN,userid)
        if resp["successful"]:
            embed.add_field(name="Success",value="Banned user with ID:" + user)
        else :
            embed.add_field(name="Fail",value="Failed to ban user with ID:" + user)

    await ctx.send(embeds=successEmbeds[0:10])

@bot.command("get")
async def getReview(ctx,*,reviewid):
    review = manager.getReviewWithID(reviewid)
    embed = discord.Embed(title = "Review Info",description=review["comment"])
    embed.add_field(name = "Sender Discord ID",value = str(review["senderdiscordid"]))
    embed.add_field(name = "Sender User ID",value = str(review["senderuserid"]))
    await ctx.send(embed=embed)


def createEmbed(title,content):
    return discord.Embed(title = title,description=content)

import random
@bot.command("stats")
async def stats(ctx,*,userid = None):
    if (userid != None and type(userid) == int):
        await ctx.send("Invalid User ID") # instead of implementing just return error :blobcatcozy:
        return
    
    cur = psql.cursor()
    cur.execute("SELECT COUNT(*) FROM userreviews")
    totalReviews = cur.fetchone()
    cur.execute("SELECT COUNT(*) FROM ur_users")
    totalUsers = cur.fetchone()

    embeds = []
    embeds.append(createEmbed("Total Reviews",str(totalReviews[0])))
    embeds.append(createEmbed("Total Users",str(totalUsers[0])))
    embeds.append(createEmbed("Seconds since ven did something stupit:",str(random.randint(4, 50))))

    await ctx.send(embeds=embeds)
    return


bot.run(BOT_TOKEN)
