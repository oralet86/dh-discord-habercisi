from urllib.parse import urlparse
from os.path import exists, getsize
from time import perf_counter
from discord.ext import tasks, commands
from bs4 import BeautifulSoup
import asyncio
import json
import aiohttp
# from time import perf_counter

TEST = 1100730493319774218 # Test kanalı


class ForumChecker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check.start()

    async def cog_unload(self):
        await self.check.cancel()

    @tasks.loop(seconds=60)
    async def check(self):
        # start = perf_counter() Used for speed diagnosis
        test_channel = self.bot.get_channel(TEST)

        async for yk_dict in yenikonu(): # örnek yk_dict = {"link":yenikonu,"baslik":baslik,"channels":dictvalue["channels"]}

            for yk_channel in yk_dict["channels"]:

                try:
                    await self.bot.get_channel(yk_channel).send(f"{yk_dict['baslik']} forumunda yeni konu! \nLink: https://forum.donanimhaber.com{yk_dict['link']}")
                except AttributeError:
                    continue

        await test_channel.send("Yeni konulara bakıyorum!")

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
    await bot.add_cog(ForumChecker(bot))


# ANAHTAR KELIMELER :
# values_abs: values.json dosyasının absolute path'ı
# values_json: values.json dosyasının kendisi
# values: values.json dosyasının içinden belleğe okunmuş veriler
# dictvalue: bellekteki values'in içindeki her bir dictionary

values_abs = f"values.json"

if exists(values_abs) and getsize(values_abs) != 0:
    with open(values_abs,"r") as values_json:
        values = json.load(values_json)
else:
    with open(values_abs,"w") as values_json:
        json.dump([],values_json)
        values = []


def main() -> None:

    BENCHMARK = 1

    start = perf_counter()

    for _ in range(BENCHMARK):
        print(values_abs)
    print(f"Completed Execution in {perf_counter() - start} seconds")


async def isvalid(link) -> bool: # Bağlantı Donanımhaber içindeyse ve başarılıysa True, değilse False geri dönüt verir
    if urlparse(link)[1] == "forum.donanimhaber.com":
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(link) as response:
                    if response.status == 200:
                        return True
        except aiohttp.ClientError:
            return False

    return False


def getid(link: str) -> int:
    idlocation = link.rfind("-")
    if idlocation != -1:
        return (link[idlocation+1:])


async def yenikonu():

    for dictvalue in values:
        yenikonu_numlar = []

        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://forum.donanimhaber.com/a--{dictvalue["link"]}') as response:
                soup = BeautifulSoup(await response.text(),"html.parser")

                baslik = soup.title.text[:soup.title.text.find(" Forumları")]

                konular = soup(class_="kl-icerik-satir yenikonu",limit=15) # En üstteki 15 konuya bakmak için

                for konu in konular:
                    yenikonu = konu.select_one("a").get("href") # Örnek olarak: /shopflix-guvenilir-mi--155719413
                    yenikonu_num = int(getid(yenikonu)) # Sadece sondaki sayıları almak için

                    if yenikonu_num > dictvalue["latest"]:
                        yenikonu_numlar.append(yenikonu_num)
                        yield {"link":yenikonu,"baslik":baslik,"channels":dictvalue["channels"]}

                if len(yenikonu_numlar) != 0:
                    dictvalue["latest"] = max(yenikonu_numlar)

    with open(values_abs,"w") as valuesjson:
        json.dump(values,valuesjson)


async def siteekle(ctx: commands.Context, link: str) -> int:

    if await isvalid(link): # Verilen linkin gerçekten donanımhaberde geçerli bir siteye gidip gitmediğini test ediyor.
        link = getid(link) # Linkin tamamına ihtiyacımız yok, sadece linkin son alfanumerik kısmı yeterli olduğu için onu kaydediyoruz.

        print("searching for link..") # valuesdir içerisinde uygun dict varsa giriyor.
        for dictvalue in values:
            if dictvalue["link"] == link:
                print("link found!")
                if ctx.channel.id in dictvalue["channels"]: # eklenmeye çalışan kanal id'si eğer zaten listede varsa, eklemeyip eli boş dönüyor. :(
                    return 2

                else:
                    dictvalue["channels"].append(ctx.channel.id) # eğer kanal id'si listede yoksa, listeye ekliyor.
                    with open(values_abs,"w") as valueswrite:
                        json.dump(values,valueswrite)
                    return 0

        print("link not found!")
        values.append({"link":link,"channels":[ctx.channel.id],"latest":0})
        with open(values_abs,"w") as valueswrite:
            json.dump(values,valueswrite)
        return 0

    return 1


async def sitecikar(ctx: commands.Context, link:str= None) -> int:
    if link is None:
        for dictvalue in values:

            if ctx.channel.id in dictvalue["channels"]:
                dictvalue["channels"].remove(ctx.channel.id)

        with open(values_abs,"w") as jsonfile:
            json.dump(values,jsonfile)
        return 0

    else:
        link = getid(link)
        for dictvalue in values:

            if link == dictvalue["link"]:

                if ctx.channel.id in dictvalue["channels"]:
                    dictvalue["channels"].remove(ctx.channel.id)

                    with open(values_abs,"w") as jsonfile:
                        json.dump(values,jsonfile)
                    return 1

                else:
                    return 2

    return 2


if __name__ == '__main__':
    asyncio.run(main())

else:
    async def setup(bot) -> None:
        await bot.add_cog(ForumChecker(bot))
