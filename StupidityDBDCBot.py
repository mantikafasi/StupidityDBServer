# from _mysqlManager import Manager,Vote
import json
from logging import Manager as LogManager
from secrets import BOT_VOTE_TOKEN, token
from threading import Thread

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
        activity=discord.Activity(type=discord.ActivityType.watching, name="Nothing")
    )


@bot.event
async def on_message(message):
    ctx = await bot.get_context(message)
    mesaj = message.content.lower().strip()
    if mesaj.startswith("{"):
        obj = json.loads(mesaj)
        try:
            stupidity = int(obj["stupidity"])
            if (
                stupidity >= 0
                and stupidity <= 100
                and (
                    len(str(obj["discordid"])) <= 19
                    and len(str(obj["discordid"])) >= 17
                )
            ):
                await ctx.send(
                    requests.post(
                        "https://mantikralligi1.pythonanywhere.com/putUser",
                        json={
                            "discordid": obj["discordid"],
                            "stupidity": obj["stupidity"],
                            "senderdiscordid": ctx.author.id,
                            "token": BOT_VOTE_TOKEN,
                        },
                    ).text
                )
            else:
                await ctx.send("An Error occured")
        except Exception as e:
            await ctx.send(e)
            raise Exception(e)


bot.run(token)
