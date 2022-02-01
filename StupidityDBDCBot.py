import json
from utils.embed import embed
from secrets import BOT_VOTE_TOKEN, token

import discord
import requests
from discord.ext import commands

bot = commands.Bot(command_prefix=".")


@bot.event
async def on_ready():
    print(bot.user.name)
    print("Olarak Giriş Yapıldı")
    print(bot.user.id)
    print("------")
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching, name="Nothing")
    )


@bot.listen()
async def on_message(message):  # legacy
    if not message.content.startswith("{") or not message.content.endswith("}"):
        return
    try:
        vote_dict = json.loads(message.content)
    except json.JSONDecodeError:
        return
    if not all(key in vote_dict.keys() for key in ["stupidity", "discordid"]):
        return
    elif not all(isinstance(vote_dict[key], int) for key in ["stupidity", "discordid"]):
        return
    elif not 0 <= vote_dict[stupidity] <= 100:
        return await ctx.reply(embed=embed.error("Give a valid number dumbass"), mention_author=False)
    elif len(str(vote_dict[discord])) != 18:
        return await ctx.reply(embed=embed.error("Give a valid user id retard"), mention_author=False)

    api_response = requests.post(
        "https://mantikralligi1.pythonanywhere.com/putUser",
        json={
            "discordid": vote_dict[discordid],
            "stupidity": vote_dict[stupidity],
            "senderdiscordid": message.author.id,
            "token": BOT_VOTE_TOKEN,
        }).text

    if api_response == "Successful":
        return await ctx.reply(embed=embed.success("Successfully voted", f"`discordid`: {discordid}\n`stupidity`: {stupidity}"), mention_author=False)
    elif api_response == "Your Vote Updated":
        return await ctx.reply(embed=embed.success("Successfully updated vote", f"`discordid`: {discordid}\n`stupidity`: {stupidity}"), mention_author=False)
    else:
        return await ctx.reply(embed=embed.error("An unexpected error occured"), mention_author=False)


@bot.command()
async def vote(ctx, discordid: str = None, stupidity: str = None):  # new
    if any(param is None for param in [discordid, stupidity]):
        return

    # discordid
    try:
        discordid = int(discordid)
    except ValueError:
        return await ctx.reply(embed=embed.error("Give a valid user id retard"), mention_author=False)
    if len(str(discordid)) != 18:
        return await ctx.reply(embed=embed.error("Give a valid user id retard"), mention_author=False)

    # stupidity
    try:
        stupidity = int(stupidity)
    except ValueError:
        return await ctx.reply(embed=embed.error("Give a valid number dumbass"), mention_author=False)
    if not 0 <= stupidity <= 100:
        return await ctx.reply(embed=embed.error("Number must be between 100-0"), mention_author=False)

    api_response = requests.post(
        "https://mantikralligi1.pythonanywhere.com/putUser",
        json={
            "discordid": discordid,
            "stupidity": stupidity,
            "senderdiscordid": ctx.author.id,
            "token": BOT_VOTE_TOKEN,
        }).text

    if api_response == "Successful":
        return await ctx.reply(embed=embed.success("Successfully voted", f"`discordid`: {discordid}\n`stupidity`: {stupidity}"), mention_author=False)
    elif api_response == "Your Vote Updated":
        return await ctx.reply(embed=embed.success("Successfully updated vote", f"`discordid`: {discordid}\n`stupidity`: {stupidity}"), mention_author=False)
    else:
        return await ctx.reply(embed=embed.error("An unexpected error occured"), mention_author=False)


bot.run(token)
