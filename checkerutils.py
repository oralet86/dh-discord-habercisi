import json
import aiohttp
import asyncio
from discord.ext import commands
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from os.path import exists, getsize
from time import perf_counter

if exists("values.json"):
    if getsize("values.json") != 0:
        with open("values.json","r") as valuesjson:
            values = json.load(valuesjson)
    else:
        with open("values.json","w") as valuesjson:
            json.dump([],valuesjson)
            values = []
else:
    with open("values.json","w") as valuesjson:
        json.dump([],valuesjson)
        values = []

def main() -> None:

    BENCHMARK = 1

    start = perf_counter()

    for _ in range(BENCHMARK):
        asyncio.run(buffer())

    print(f"Completed Execution in {perf_counter() - start} seconds")

async def buffer():
    async for i in yenikonu():
        print(i)


async def isvalid(link) -> bool: # Bağlantı Donanımhaber içindeyse ve başarılıysa True, değilse False geri dönüt verir
    if urlparse(link)[1] == "forum.donanimhaber.com":
        try:
            async with aiohttp.ClientSession().get(link) as response:
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

    for jsondict in values:
        yenikonu_numlar = []

        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://forum.donanimhaber.com/a--{jsondict["link"]}') as response:
                soup = BeautifulSoup(await response.text(),"html.parser")

                baslik = soup.title.text[:soup.title.text.find(" Forumları")]

                konular = soup(class_="kl-icerik-satir yenikonu",limit=15) # En üstteki 15 konuya bakmak için

                for konu in konular:
                    yenikonu = konu.select_one("a").get("href") # Örnek olarak: /shopflix-guvenilir-mi--155719413
                    yenikonu_num = int(getid(yenikonu)) # Sadece sondaki sayıları almak için

                    if yenikonu_num > jsondict["latest"]: 
                        yenikonu_numlar.append(yenikonu_num)
                        yield {"link":yenikonu,"baslik":baslik,"channels":jsondict["channels"]}

                if len(yenikonu_numlar) != 0:
                    jsondict["latest"] = max(yenikonu_numlar)

    with open("values.json","w") as valuesjson:
        json.dump(values,valuesjson)

async def siteekle(ctx: commands.Context, link: str) -> int:
    if isvalid(link): # Verilen linkin gerçekten donanımhaberde geçerli bir siteye gidip gitmediğini test ediyor.
        
        link = getid(link) # Linkin tamamına ihtiyacımız yok, sadece linkin son alfanumerik kısmı yeterli olduğu için onu kaydediyoruz.

        print("searching for link..") # values.json içerisinde uygun dict varsa giriyor.
        for jsondict in values:
            if jsondict["link"] == link:
                print("link found!")
                if ctx.channel.id in jsondict["channels"]: # eklenmeye çalışan kanal id'si eğer zaten listede varsa, eklemeyip eli boş dönüyor. :(
                    return 2

                else:
                    jsondict["channels"].append(ctx.channel.id) # eğer kanal id'si listede yoksa, listeye ekliyor.
                    with open("values.json","w") as valueswrite:
                        json.dump(values,valueswrite)
                    return 0

        print("link not found!")
        values.append({"link":link,"channels":[ctx.channel.id],"latest":0})
        with open("values.json","w") as valueswrite:
            json.dump(values,valueswrite)
        return 0

    return 1
    
async def sitecikar(ctx: commands.Context) -> int:
    with open("values.json","r") as jsonfile:
        data = json.load(jsonfile)

    print("file opened!")

    for jsondict in data:
        if ctx.channel.id in jsondict["channels"]:
            jsondict["channels"].remove(ctx.channel.id)
    with open("values.json","w") as jsonfile:
        json.dump(data,jsonfile)
    return 0
                        

if __name__ == '__main__':
    main()