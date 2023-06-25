import discord
from discord.ext import tasks, commands
from datetime import time, date, timedelta, timezone
from os.path import exists, getsize, abspath, dirname
import json

starttime = [time(hour=5, minute=0, second=0, tzinfo=timezone(timedelta(hours=3)))]

yirmidort_dir = f"{abspath(dirname(dirname(__file__)))}\\yirmidort.json"

if exists(yirmidort_dir) and getsize(yirmidort_dir) != 0:
    with open(yirmidort_dir,"r") as yirmidort_jsonfile:
        yirmidort_values = json.load(yirmidort_jsonfile)
else:
    with open(yirmidort_dir,"w") as yirmidort_jsonfile:
        json.dump({},yirmidort_jsonfile)
        yirmidort_values = {}

class Yirmidort(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.yirmidort_channels: list[discord.TextChannel] = [self.bot.get_channel(int(channel_id)) for channel_id in yirmidort_values.keys()]
        self.yirmidortsil.start()

    async def cog_unload(self):
        await self.yirmidortsil.cancel()

    @tasks.loop(time=starttime)
    async def yirmidortsil(self):

        current_date = date.today()

        if self.yirmidort_channels is not None:

            for yirmidort_channel in self.yirmidort_channels:

                with open(f"arsiv/{yirmidort_channel.name}/{current_date}.txt","+a",encoding="utf-8") as arsiv_dosyasi:

                    arsiv_dosyasi.seek(0, 2)

                    async for message in yirmidort_channel.history(limit=10000):

                        if message.author.global_name is None:
                            author_nickname = f"{message.author.name}#{message.author.discriminator}"
                        else:
                            author_nickname = message.author.global_name

                        if message.edited_at is None:
                            arsiv_dosyasi.write(f"{message.created_at} | {author_nickname}: {message.content}\n")
                        else:
                            arsiv_dosyasi.write(f"{message.created_at} | {author_nickname}: {message.content} (Edited)\n")


                    await yirmidort_channel.purge(bulk=True,limit=10000)

                    await yirmidort_channel.send("Kanal temizlendi :sunrise: :afro:")

    @yirmidortsil.before_loop
    async def before_my_task(self):
        await self.bot.wait_until_ready()
        print("24-saat silme loopu başlıyor")

async def setup(bot):
    await bot.add_cog(Yirmidort(bot))
