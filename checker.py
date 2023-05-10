from discord.ext import tasks, commands
import dhcheck
import asyncio

class Checker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check.start()

    def cog_unload(self):
        self.check.stop()

    @tasks.loop(seconds=60)
    async def check(self):
        goat = self.bot.get_channel(1100730493319774218)
        await goat.send("60 saniye gecti!")

        task = asyncio.create_task(dhcheck.yenikonu())

        for dict in (await task):
            for channelid in dict["channels"]:
                channel = self.bot.get_channel(channelid)
                for links in dict["links"]:
                    await channel.send(f"{dict['baslik']}forumunda yeni konu! \nLink: https://forum.donanimhaber.com{links}")


    @check.before_loop
    async def before_my_task(self):
        await self.bot.wait_until_ready() 

    @commands.command()
    async def startchecking(self, ctx):
        self.check.start()

    @commands.command()
    async def stopchecking(self, ctx):
        self.check.stop()

    
async def setup(bot):
    await bot.add_cog(Checker(bot))