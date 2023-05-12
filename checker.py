from discord.ext import tasks, commands
from checkerutils import sitecikar, siteekle, yenikonu
from time import perf_counter

TEST = 1100730493319774218 # Test kanalı

class Checker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check.start()

    async def cog_unload(self):
        await self.check.cancel()

    @tasks.loop(seconds=60)
    async def check(self):
        start = perf_counter()
        goat = self.bot.get_channel(TEST)

        async for i in yenikonu():
            for ch in i["channels"]:
                await self.bot.get_channel(ch).send(f"{i['baslik']} forumlarında yeni konu! \nLink: https://forum.donanimhaber.com{i['link']}")

        await goat.send("60 saniye gecti!")

        print(f"Completed Execution in {perf_counter() - start} seconds")

    @check.before_loop
    async def before_my_task(self):
        await self.bot.wait_until_ready()

    @commands.command()
    async def baslat(self, ctx: commands.Context):
        if ctx.channel.id == TEST:
            ctx.send("Checker cog baslatildi!")
            self.check.start()

    @commands.command()
    async def durdur(self, ctx: commands.Context):
        if ctx.channel.id == TEST:
            ctx.send("Checker cog durduruldu!")
            self.check.cancel()

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
    async def cikar(self, ctx: commands.Context):
        match await sitecikar(ctx):
            case 0:
                await ctx.send(f"İşlem başarılı! Artık `{ctx.channel.name}` kanalında herhangi bir forum takip edilmeyecek.")



async def setup(bot):
    print("Checker cog yükleniyor...")
    await bot.add_cog(Checker(bot))
