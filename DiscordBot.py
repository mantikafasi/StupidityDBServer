import random

import discord
from discord.ext import commands

from _secrets import BOT_TOKEN
from mysqlconnection import Manager
from userReviewsManager import Manager as UserReviewsManager

psql = Manager()

manager = UserReviewsManager(psql)


bot = commands.Bot(command_prefix=".", intents=discord.Intents.all())


@bot.event
async def on_ready():

    print("Logged In As")

    print(bot.user.name)

    print("------")

    await bot.tree.sync()

    print(bot.user.id)

    await bot.change_presence(
        activity=discord.Activity(type=discord.ActivityType.watching, name="Nothing")
    )


@bot.hybrid_command(name="search", description="Searches for reviews")
async def searchReview(ctx, *, query: str):

    if query is not None:

        return await ctx.send("Put a query dumbass")

    reviews = manager.getReviewsByQuery(query)

    embeds = []

    for review in reviews[0:10]:
        review_embed = discord.Embed(title="Comment", description=review["comment"])
        review_embed.add_field(
            name="Sender Discord ID", value=str(review["senderdiscordid"])
        )
        review_embed.add_field(name="Sender User ID", value=str(review["senderuserid"]))
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

    for user in users:

        resp = manager.banUser(BOT_TOKEN, user)

        if resp["successful"]:

            embed.add_field(name="Success", value="Banned user with ID:" + user)

        else:

            embed.add_field(name="Fail", value="Failed to ban user with ID:" + user)

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

    embed.add_field(name="Sender User ID", value=str(review["senderuserid"]))

    await ctx.send(embed=embed)


def createEmbed(title, content):

    return discord.Embed(title=title, description=content)


@bot.hybrid_command("stats")
async def stats(ctx, *, userid=None):

    if userid is not None and isinstance(userid, int):

        # instead of implementing just return error :blobcatcozy:

        await ctx.send("Invalid User ID")
        return

    cur = psql.cursor()

    cur.execute("SELECT COUNT(*) FROM userreviews")

    totalReviews = cur.fetchone()

    cur.execute("SELECT COUNT(*) FROM ur_users")

    totalUsers = cur.fetchone()

    embeds = []

    embeds.append(createEmbed("Total Reviews", str(totalReviews[0])))

    embeds.append(createEmbed("Total Users", str(totalUsers[0])))

    embeds.append(
        createEmbed(
            "Seconds since ven did something stupit:", str(random.randint(4, 50))
        )
    )
    await ctx.send(embeds=embeds)
    return


@bot.hybrid_command("sql")
async def sql(ctx, *, query: str):

    if not manager.isUserAdminID(ctx.author.id):
        await ctx.send("You are not authrorized to run sql queries")
        return

    if "drop" in query.lower():
        await ctx.send("You are insane")
        return

    cur = psql.cursor()
    try:
        cur.execute(query)
        await ctx.send(str(cur.fetchall())[0:2000])

    except Exception as e:
        await ctx.send(str(e))


bot.run(BOT_TOKEN)
