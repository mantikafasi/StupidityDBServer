#!/usr/bin/python3.9
from mysqlconnection import Manager
from _secrets import BOT_TOKEN
import discord
import asyncio

manager = Manager()
client = discord.Client(intents=discord.Intents.all())


def getUsers():
    cursor = manager.cursor()
    cursor.execute("SELECT discord_id,username FROM users")
    return cursor.fetchall()


async def main():
    await client.login(BOT_TOKEN)
    print("Logged in!")

    users = getUsers()
    for user in users:
        if user[1].startswith("Deleted User"):
            continue
        
        try:
            user = await fetchUser(user[0])
            if user.id == 1134864775000629298:
                raise IndentationError("NO DONT UPDATE WARNING USER")
            
            if user.name.startswith("Deleted User"):
                revokeToken(user.id)
            else:
                updateDBUser(user)
        except Exception as e:
            print("An Explosion Happened:" + str(e))
    await client.close()


async def fetchUser(userId):
    return await client.fetch_user(userId)

import os
import base64

def generate_token():
    b = os.urandom(64)
    token = base64.urlsafe_b64encode(b).rstrip(b'=').decode('utf-8')  # Encode bytes to base64 and remove padding
    return "rdb." + token

def revokeToken(discordId: str):
    
    manager.cursor().execute(
        "UPDATE users SET token=%s WHERE discord_id=%s", (generate_token(),discordId,)
    )
    print("Revoked Token:" + str(discordId))


def updateDBUser(user: discord.User):
    manager.cursor().execute(
        "UPDATE users SET username=%s,avatar_url=%s WHERE discord_id=%s",
        (
            user.name + ("#" + user.discriminator if user.discriminator != "0" else ""),
            user.avatar.with_size(128).url
            if (user.avatar is not None)
            else str(user.default_avatar) + "?size=128",
            user.id,
        ),
    )
    print("Updated User:" + user.name)


asyncio.get_event_loop().run_until_complete(main())
