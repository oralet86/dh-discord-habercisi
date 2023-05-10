import asyncio
from discord.ext import tasks, commands
import dhcheck

class Checker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check.start()

    async def cog_unload(self):
        await self.check.cancel()

    @tasks.loop(seconds=60)
    async def check(self):
        goat = self.bot.get_channel(1100730493319774218) # Test kanalı :D
        await goat.send("60 saniye gecti!")

        task = asyncio.create_task(dhcheck.yenikonu())

        for jsondict in (await task):
            for channelid in jsondict["channels"]:
                channel = self.bot.get_channel(channelid)
                for links in jsondict["links"]:
                    await channel.send(f"{jsondict['baslik']}nda yeni konu! \nLink: https://forum.donanimhaber.com{links}")

    @check.before_loop
    async def before_my_task(self):
        await self.bot.wait_until_ready()

    @commands.command()
    async def baslat(self, ctx: commands.Context):
        if ctx.channel.id == 1100730493319774218:
            ctx.send("Checker cog baslatildi!")
            self.check.start()

    @commands.command()
    async def durdur(self, ctx: commands.Context):
        if ctx.channel.id == 1100730493319774218:
            ctx.send("Checker cog durduruldu!")
            self.check.cancel()


async def setup(bot):
    print("Checker cog yükleniyor.")
    await bot.add_cog(Checker(bot))
