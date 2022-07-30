from mysqlconnection import Manager
from _secrets import BOT_TOKEN
import discord
import asyncio
manager = Manager()
client = discord.Client()

def getUsers():
    manager.cursor().execute("SELECT discordid FROM ur_users")
    return manager.cursor().fetchall()


async def main():
    await client.login(BOT_TOKEN)
    print("Logged in!")

    users = getUsers()
    for user in users():
        user  = await fetchUser(user[0])
        updateDBUser(user)

    await client.close()
async def fetchUser(userId):
    return await client.fetch_user(userId)
    
def updateDBUser(user:discord.User):
    manager.cursor().execute("UPDATE ur_users SET username=%s,profile_photo=%s WHERE discordid=%s", (user.name + "#" + user.discriminator, user.avatar_url, user.id))

asyncio.get_event_loop().run_until_complete(main())
