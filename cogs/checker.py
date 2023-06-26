from discord.ext import tasks, commands
from cogs.checker_utils import sitecikar, siteekle, yenikonu
# from time import perf_counter

TEST = 1100730493319774218 # Test kanalı

class Checker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check.start()

    async def cog_unload(self):
        await self.check.cancel()

    @tasks.loop(seconds=60)
    async def check(self):
        # start = perf_counter() Used for speed diagnosis
        goat = self.bot.get_channel(TEST)

        async for yk_dict in yenikonu(): # örnek yk_dict = {"link":yenikonu,"baslik":baslik,"channels":dictvalue["channels"]}

            for yk_channel in yk_dict["channels"]:
                
                try:
                    await self.bot.get_channel(yk_channel).send(f"{yk_dict['baslik']} forumunda yeni konu! \nLink: https://forum.donanimhaber.com{yk_dict['link']}")
                except AttributeError:
                    continue

        await goat.send("Yeni konulara bakıyorum!")

        # print(f"Completed Execution in {perf_counter() - start} seconds")

    @check.before_loop
    async def before_my_task(self):
        await self.bot.wait_until_ready()

    @commands.command()
    async def baslat(self, ctx: commands.Context):
        if ctx.channel.id == TEST:
            try:
                self.check.start()
            except RuntimeError:
                await ctx.send("Checker cog zaten calisiyor.")
            finally:
                await ctx.send("Checker cog baslatildi!")

    @commands.command()
    async def durdur(self, ctx: commands.Context):
        if ctx.channel.id == TEST:
            try:
                self.check.cancel()
            except RuntimeError:
                await ctx.send("Checker cog zaten durdurulmus.")
            finally:
                await ctx.send("Checker cog durduruldu!")

    @commands.command()
    async def ekle(self, ctx: commands.Context, link: str):
        match await siteekle(ctx, link):
            case 0:
                await ctx.send(f"İşlem başarılı! Artık `{link}` forumunda yeni bir konu açıldığında `{ctx.channel.name}` kanalına mesaj atılacak.")
            case 1:
                await ctx.send("Verilen link geçerli bir DonanımHaber linki değil.")
            case 2:
                await ctx.send(f"`{link}` forumu `{ctx.channel.name}` kanalında zaten takip ediliyor!")

    @commands.command()
    async def cikar(self, ctx: commands.Context, link:str= None):
        match await sitecikar(ctx, link):
            case 0:
                await ctx.send(f"İşlem başarılı! Artık `{ctx.channel.name}` kanalında herhangi bir forum takip edilmeyecek.")
            case 1:
                await ctx.send(f"İşlem başarılı! Artık `{ctx.channel.name}` kanalında `{link}` forumu takip edilmeyecek.")
            case 2:
                await ctx.send(f"`{link}` forumu `{ctx.channel.name}` kanalında zaten takip edilmiyor.")



async def setup(bot):
    await bot.add_cog(Checker(bot))
