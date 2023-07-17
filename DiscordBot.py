import random

import discord
from discord.ext import commands

from _secrets import BOT_TOKEN,ADMIN_TOKEN
from mysqlconnection import Manager
from userReviewsManager import Manager as UserReviewsManager
from discord.ext import tasks
import requests
import pandas
import os
import base64

psql = Manager()

manager = UserReviewsManager(psql)


bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())


@bot.event
async def on_ready():

    print("Logged In As")

    print(bot.user.name)

    print("------")

    print(bot.user.id)

    global msg

    channel = bot.get_channel(1084587617015824456)
    msg = await channel.fetch_message(1106296105488105562)


    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="Nothing")
    )

    updateMetrics.start()


@bot.hybrid_command(name="search", description="Searches for reviews")
async def searchReview(ctx, *, query: str):

    if query is None:

        return await ctx.send("Put a query dumbass")

    reviews = manager.getReviewsByQuery(query)

    embeds = []

    for review in reviews[0:10]:
        review_embed = discord.Embed(title="Comment", description=review["comment"])
        review_embed.add_field(
            name="Sender Discord ID", value=str(review["senderdiscordid"])
        )
        review_embed.add_field(name="Sender User ID", value=str(review["reviewer_id"]))
        review_embed.add_field(name="Review ID", value=str(review["id"]))

        embeds.append(review_embed)

    if len(embeds) == 0:

        embeds.append(
            discord.Embed(
                title="Not Found",
                description=f"A review that contains {query} not found!",
            )
        )

    await ctx.send(embeds=embeds)

@bot.hybrid_command("delete")
async def deleteReview(ctx, *, reviewids: str = None):
    if reviewids is None:
        await ctx.send("Please include review ids")

    if not manager.isUserAdminID(discordid=ctx.author.id):
        await ctx.send("You are not authrorized to delete reviews.")
        return

    reviews = []
    if " " in reviewids:
        reviews = reviewids.split(" ")
    else:
        reviews = [
            reviewids,
        ]

    embed = discord.Embed(title="Status")
    for id in reviews:
        resp = manager.deleteReview(BOT_TOKEN, id)
        if resp["successful"]:
            embed.add_field(name="Success", value="Deleted review with ID:" + id)
        else:
            embed.add_field(name="Fail", value="Failed to delete review with ID:" + id)
    await ctx.send(embed=embed)

@bot.hybrid_command("ban")
async def banUser(ctx, *, userids: str):
    if not manager.isUserAdminID(ctx.author.id):
        await ctx.send("You are not authrorized to ban users blabla")
        return
    users = []

    if " " in userids:
        users = userids.split(" ")
    else:
        users = [
            userids,
        ]

    embed = discord.Embed(title="Status")

    embed.set_footer(text="Ven Will Die")

    successCount = 0
    for user in users:
        resp = manager.banUser(BOT_TOKEN, user)
        if resp["successful"]:
            successCount += 1
            embed.add_field(name="Success", value="Banned user with ID:" + user)
        else:
            embed.add_field(name="Fail", value="Failed to ban user with ID:" + user)
    embed.set_footer(text=f"Banned {str(successCount)}/{len(users)} users")
    await ctx.send(embed=embed)

@bot.hybrid_command("unban")
async def unbanUser(ctx, *, userids: str):
    if not manager.isUserAdminID(ctx.author.id):
        await ctx.send("You are not authrorized to unban users")
        return
    users = []

    if " " in userids:
        users = userids.split(" ")

    else:
        users = [
            userids,
        ]

    embed = discord.Embed(title="Status")
    embed.set_footer(text="Ven Will Die")
    for user in users:
        resp = manager.unbanUser(BOT_TOKEN, user)

        if resp["successful"]:

            embed.add_field(name="Success", value="Unbanned user with ID:" + user)

        else:

            embed.add_field(name="Fail", value="Failed to unban user with ID:" + user)

    await ctx.send(embed=embed)

@bot.hybrid_command("get")
async def getReview(ctx, *, reviewid):

    review = manager.getReviewWithID(reviewid)

    embed = discord.Embed(title="Review Info", description=review["comment"])

    embed.add_field(name="Sender Discord ID", value=str(review["senderdiscordid"]))

    embed.add_field(name="Sender User ID", value=str(review["reviewer_id"]))

    await ctx.send(embed=embed)

def createEmbed(title, content):

    return discord.Embed(title=title, description=content)

@bot.hybrid_command("stats")
async def stats(ctx, *, userid=None):
    embeds = []
    embed,userCountEmbed = createMetricsEmbed()
    embeds.append(embed)
    embeds.append(userCountEmbed)

    embeds.append(
        createEmbed(
            "Seconds since ven did something stupit:", str(random.randint(4, 50))
        )
    )
    await ctx.send(embed=embed)
    return

@bot.hybrid_command("sql")
async def sql(ctx, *, query: str):

    if not manager.isUserAdminID(ctx.author.id):
        await ctx.send("You are not authrorized to run sql queries")
        return

    if "drop" in query.lower():
        await ctx.send("You are insane")
        return
    
    if not query.endswith(";"):
        await ctx.send("Add ; to the end of your query idiot")
        return

    cur = psql.cursor()
    try:
        cur.execute(query)
        query = pandas.read_sql_query(query, psql.sql)
        pandas.options.display.float_format = '{:.2f}'.format

        pandas.DataFrame(query).to_markdown("sqlcommand.md", index=False)        
        
        await ctx.send(file=discord.File("sqlcommand.md"))
        os.remove("sqlcommand.md")

    except Exception as e:
        await ctx.send(str(e))

@bot.hybrid_command("addbadge")
async def addBadge(ctx, discordid:str, badgename:str,badgeicon:str,redirecturl = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"):
    if not manager.isUserAdminID(ctx.author.id):
        await ctx.send("You are not authrorized to add badges")
        return
    
    await ctx.send(manager.addBadge(discordid, badgename, badgeicon, redirecturl))

@bot.hybrid_command("deleteall",description="Deletes all reviews of user")
async def deleteAllReviews(ctx, *, userids:str):
    if not manager.isUserAdminID(ctx.author.id):
        await ctx.send("You are not authrorized to delete all reviews")
        return

    if userids is None:
        await ctx.send("Please provide a user id")
        return

    users = []
    
    if " " in userids:
        users = userids.split(" ")
    else:
        users = [
            userids,
        ]

    for user in users:
        manager.deleteAllReviewsOfUser(user)
    await ctx.send("Deleted all reviews of user(s)")

@bot.hybrid_command("synccommands")
async def syncCommands(ctx):
    if not manager.isUserAdminID(ctx.author.id):
        await ctx.send("You are not authrorized to sync commands")
        return
    await bot.tree.sync()
    await ctx.send("Synced commands")


@bot.hybrid_command("stupid")
async def stupit(ctx):
    await ctx.send("Ven is stupit")

@bot.hybrid_command("stupit")
async def stupit(ctx, *, user: discord.Member):
    if user is None:
        await ctx.send(f"{ctx.author.mention} is 100% stupit for not providing user")
    random.seed(user.id)
    await ctx.send(f"{user.mention} is {str(random.randint(1, 100))}% stupit")

@bot.hybrid_command("getuseridswithcomment")
async def getUserIDsWithComment(ctx, interval:int,comment:str):
    if not manager.isUserAdminID(ctx.author.id):
        await ctx.reply("You are not authrorized to run this command")
        return

    cur = psql.cursor()

    cur.execute("SELECT DISTINCT ON (reviewer_id) reviewer_id FROM reviews WHERE comment LIKE %s AND timestamp > NOW() - INTERVAL '%s hour'", (f"%{comment}%",interval))
    results = (str(a[0]) for a in cur.fetchall())
    res = " ".join(results)
    await ctx.reply(res)

@bot.hybrid_command("getfilters")
async def getFilters(ctx):
    if not manager.isUserAdminID(ctx.author.id):
        await ctx.reply("You are not authrorized to run this command")
        return

    res = requests.get("https://manti.vendicated.dev/api/reviewdb/admin/filters",headers={"Authorization": ADMIN_TOKEN})
    await ctx.reply(res.text)
@bot.hybrid_command("addfilter")
async def addFilter(ctx, *, word:str, filtertype:str):
    if not manager.isUserAdminID(ctx.author.id):
        await ctx.reply("You are not authrorized to run this command")
        return

    if filtertype not in ["profane","lightProfane"]:
        await ctx.reply("filter type must be profane or lightProfane")
        return

    res = requests.put("https://manti.vendicated.dev/api/reviewdb/admin/filters",
        headers={"Authorization": ADMIN_TOKEN},
        json={"word":word,"type":filtertype})

    if res.status_code == 200:
        await ctx.reply("Added filter")
    else:
        await ctx.reply("exploded " + res.text)

@bot.hybrid_command("deletefilter")
async def deleteFilter(ctx, *, word:str, filtertype:str):
    if not manager.isUserAdminID(ctx.author.id):
        await ctx.reply("You are not authrorized to run this command")
        return

    res = requests.delete("https://manti.vendicated.dev/api/reviewdb/admin/filters",headers={"Authorization": ADMIN_TOKEN},json={"word":word,"type":filtertype})
    if res.status_code == 200:
        await ctx.reply("Deleted filter")
    else:
        await ctx.reply("exploded " + res.text)

@bot.hybrid_command("resettoken")
async def resetToken(ctx, *, reviewdbuserid: number):
    if not manager.isUserAdminID(ctx.author.id):
        await ctx.reply("You are not authrorized to run this command")
        return

    cursor = manager.manager.cursor()
    cursor.execute("UPDATE users SET token = %s WHERE id = %s", (generate_token(), reviewdbuserid))

def generate_token():
    b = os.urandom(64)
    token = base64.urlsafe_b64encode(b).rstrip(b'=')
    return 'rdb.' + token.decode('utf-8')
    
def createMetricsEmbed():
    embed = discord.Embed(title="Metrics")

    userCountEmbed = discord.Embed(title="User Count By Client Mod")

    cursor = manager.manager.cursor()
    cursor.execute("""
    select client_mod, count(*)
        from (
        select unnest(client_mods) as client_mod
        from users
        ) t
        group by client_mod;
    """)
    for row in cursor.fetchall():
        userCountEmbed.add_field(name=f"{row[0]}", value=row[1])

    data = requests.get("http://localhost:4444/metrics").text
    for line in data.split("\n"):   

        if line.startswith("user_count"):
            embed.add_field(name="Total User Count", value=line.split(" ")[1])
        elif line.startswith("review_count"):
            embed.add_field(name="Review Count", value=line.split(" ")[1])
    return [embed ,userCountEmbed]

@bot.hybrid_command("metrics")
async def metrics(ctx):
    embed,usercountembed = createMetricsEmbed()
    await ctx.send(embeds=createMetricsEmbed())

msg:discord.message.Message = None
@tasks.loop(seconds=20)
async def updateMetrics():
    if msg is None:
        return

    await msg.edit(embeds=createMetricsEmbed())

bot.run(BOT_TOKEN)