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