import json
import aiohttp
from discord.ext import commands
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from os.path import exists, getsize, abspath, dirname
from time import perf_counter


# ANAHTAR KELIMELER :
# valuesdir: values.json dosyasının absolute path'ı
# valuesjson: values.json dosyasının kendisi
# values: values.json dosyasının içinden belleğe okunmuş veriler
# dictvalue: bellekteki values'in içindeki her bir dictionary

valuesdir = f"{abspath(dirname(dirname(__file__)))}\\values.json"

if exists(valuesdir) and getsize(valuesdir) != 0:
    with open(valuesdir,"r") as valuesjson:
        values = json.load(valuesjson)
else:
    with open(valuesdir,"w") as valuesjson:
        json.dump([],valuesjson)
        values = []


def main() -> None:

    BENCHMARK = 1

    start = perf_counter()

    for _ in range(BENCHMARK):
        print(valuesdir)
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

    with open(valuesdir,"w") as valuesjson:
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
                    with open(valuesdir,"w") as valueswrite:
                        json.dump(values,valueswrite)
                    return 0

        print("link not found!")
        values.append({"link":link,"channels":[ctx.channel.id],"latest":0})
        with open(valuesdir,"w") as valueswrite:
            json.dump(values,valueswrite)
        return 0

    return 1


async def sitecikar(ctx: commands.Context, link:str= None) -> int:
    if link is None:
        for dictvalue in values:

            if ctx.channel.id in dictvalue["channels"]:
                dictvalue["channels"].remove(ctx.channel.id)

        with open(valuesdir,"w") as jsonfile:
            json.dump(values,jsonfile)
        return 0

    else:
        link = getid(link)
        for dictvalue in values:

            if link == dictvalue["link"]:

                if ctx.channel.id in dictvalue["channels"]:
                    dictvalue["channels"].remove(ctx.channel.id)
                    
                    with open(valuesdir,"w") as jsonfile:
                        json.dump(values,jsonfile)
                    return 1
                
                else:
                    return 2

    return 2
        
                        

if __name__ == '__main__':
    main()