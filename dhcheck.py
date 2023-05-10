import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse
import aiohttp
import asyncio
import re


def main() -> None:
    print(asyncio.run(yenikonu()))


def isvalid(link) -> bool: # Bağlantı Donanımhaber içindeyse ve başarılıysa True, değilse False geri dönüt verir
    if urlparse(link)[1] == "forum.donanimhaber.com":
        try:
            response = requests.head(link, allow_redirects=True)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    else:
        return False
    
async def yenikonu():

    return_value = [] # Her şeyin sonunda geri verilecek liste

    async with aiohttp.ClientSession() as session:

        with open("values.json","r") as data:
            dicts = json.load(data)

            for dict in dicts:

                async with session.get(f'https://forum.donanimhaber.com/a--{dict["link"]}') as response:

                    soup = BeautifulSoup(await response.text(),"html.parser")

                    baslik = re.search(("^([\w\s]+)|"),soup.title.text).group()

                    konular = soup(class_="kl-icerik-satir yenikonu",limit=15) # En üstteki 15 konuya bakmak için

                    yenikonu_numlar = []
                    yenikonular = []

                    for konu in konular:
                        yenikonu = konu.select_one("a").get("href") # Örnek olarak: /shopflix-guvenilir-mi--155719413
                        yenikonu_num = int(re.search("(\w+)$",yenikonu).group()) # Sadece sondaki sayıları almak için

                        if yenikonu_num > dict["latest"]: 
                            yenikonu_numlar.append(yenikonu_num)
                            yenikonular.append(yenikonu)

                    return_value.append({"links":yenikonular,"baslik":baslik,"channels":dict["channels"]})

                    if len(yenikonu_numlar) != 0:
                        dict["latest"] = max(yenikonu_numlar)

        with open("values.json","w") as data:
            json.dump(dicts,data)
        
    return return_value
                        

if __name__ == '__main__':
    main()