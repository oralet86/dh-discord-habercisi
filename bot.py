import discord
from discord.ext import commands
import dhcheck
import json
import re
import os.path

with open("token.txt") as token:
    TOKEN = token.read()

if not (os.path.exists("values.json")):
    with open("values.json","w") as f:
        json.dump([],f)


prefix = "dh"

dhregex = "(\w+)$"

HELP = f"**{prefix}help** -> Get help about commands."

embed = discord.Embed(title="Commands", description=HELP, color=discord.Color.blurple())
embed.add_field(name="cs gelcek varmi :))", value="9:59 Tekel", inline=True)
embed.add_field(name="Yok", value="Bana 2 bremen lütfen !", inline=True)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=prefix, intents=intents, help_command=None)


def main():
    run_bot()


def run_bot():

    @bot.event
    async def on_ready():
        print(f"{bot.user} is ready!")
        
        await bot.load_extension("checker")


    @bot.command()
    async def help(ctx: commands.Context):
        await ctx.send(embed=embed)

    @bot.command()
    async def ekle(ctx: commands.Context, link: str):
        match await siteekle(ctx, link):
            case 0:
                await ctx.send(f"İşlem başarılı! Artık `{link}` forumunda yeni bir konu açıldığında `{ctx.channel.name}` kanalına mesaj atılacak.")
            case 1:
                await ctx.send(f"Verilen link geçerli bir DonanımHaber linki değil.")
            case 2:
                await ctx.send(f"`{link}` forumu `{ctx.channel.name}` kanalında zaten takip ediliyor!")

    @bot.command()
    async def cikar(ctx: commands.Context):
        match await sitecikar(ctx):
            case 0:
                await ctx.send(f"İşlem başarılı! Artık `{ctx.channel.name}` kanalında herhangi bir forum takip edilmeyecek.")

    @bot.event
    async def on_command_error(ctx, error):
        print(f"ERROR: {error}")
        await ctx.send(f"Yanlış komut! Geçerli komutları ve kullanımlarını görmek için: {prefix}help")

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return
        
        print(f"{str(message.author)} said '{str(message.content)}' in {str(message.channel)}")

        # if message.content[:3] == f"{prefix}" and (message.guild is None or message.guild.name != "quotes"):
        #     await message.channel.send("Bot test aşamasında! Şuan genel kullanıma kapalı.")
        #     return

        await bot.process_commands(message)
        
    bot.run(TOKEN)
    

# Bunları @bot.commands altına eklemek yerine, düzgün şekilde test edebilmek için ayrı fonksiyonlar yaptım.
    
async def siteekle(ctx: commands.Context, link: str) -> int:
    if (dhcheck.isvalid(link)): # Verilen linkin gerçekten donanımhaberde geçerli bir siteye gidip gitmediğini test ediyor.
        link = re.search("(\w+)$",link).group() # Linkin tamamına ihtiyacımız yok, sadece linkin son alfanumerik kısmı yeterli olduğu için onu kaydediyoruz. 
        with open("values.json","r") as f:
            data = json.load(f)
            print("file opened!")

        print("searching for link..") # values.json içerisinde uygun dict varsa giriyor.
        for dict in data:
            if dict["link"] == link: # 
                print("link found!")
                if ctx.channel.id in dict["channels"]: # eklenmeye çalışan kanal id'si eğer zaten listede varsa, eklemeyip eli boş dönüyor. :( 
                    return 2
                        
                else:
                    dict["channels"].append(ctx.channel.id) # eğer kanal id'si listede yoksa, listeye ekliyor.
                    with open("values.json","w") as f:
                        json.dump(data,f)
                    return 0

        print("link not found!")    
        data.append({"link":link,"channels":[ctx.channel.id],"latest":0})
        with open("values.json","w") as f:
            json.dump(data,f)
        return 0
    
    else:    
        return 1
    
async def sitecikar(ctx: commands.Context) -> int:
    with open("values.json","r") as f:
            data = json.load(f)
            print("file opened!")

    for dict in data:
        if ctx.channel.id in dict["channels"]:
            dict["channels"].remove(ctx.channel.id)
    with open("values.json","w") as f:
        json.dump(data,f)
    return 0

        

if __name__ == '__main__':
    main()
