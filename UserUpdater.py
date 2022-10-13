#!/usr/bin/python3.9
from mysqlconnection import Manager
from _secrets import BOT_TOKEN
import discord
import asyncio
manager = Manager()
client = discord.Client(intents=discord.Intents.all())

def getUsers():
    cursor = manager.cursor()
    cursor.execute("SELECT discordid FROM ur_users")
    return cursor.fetchall()


async def main():
    await client.login(BOT_TOKEN)
    print("Logged in!")

    users = getUsers()
    for user in users:
        try:
            user  = await fetchUser(user[0])
            updateDBUser(user)
        except Exception as e :
            print("An Explosion Happened:" + str(e))
    await client.close()

async def fetchUser(userId):
    return await client.fetch_user(userId)
    
def updateDBUser(user:discord.User):
    manager.cursor().execute("UPDATE ur_users SET username=%s,profile_photo=%s WHERE discordid=%s", (user.name + "#" + user.discriminator, user.avatar.with_size(128).url if (user.avatar is not None) else str(user.default_avatar_url) +"?size=128" , user.id))
    print("Updated User:"+ user.name)
asyncio.get_event_loop().run_until_complete(main())
