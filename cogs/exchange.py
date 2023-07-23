import discord
from discord.ext import commands
from bs4 import BeautifulSoup
import aiohttp


class Exchange(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def doviz(self, ctx: commands.Context):

        url = "https://dovizborsa.com/"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    soup = BeautifulSoup(await response.text(),"html.parser")

                else:
                    ctx.send("Döviz verisine erişilemedi.")
                    return 0

        keys = ["435","200","751"] # ID's of dollar, euro, and gold

        values = []

        for key in keys:
            alimsatim = soup.find("div",id=key).find("div",class_="-x1").find_all("span")
            for value in alimsatim:
                values.append(value.get_text(strip=True)[:-2])

        embed = discord.Embed(title="Döviz", color=discord.Colour.blurple())

        embed.add_field(name="Dolar",value=f"Alım: {values[1]}\nSatım: {values[0]}", inline=True)
        embed.add_field(name="Euro",value=f"Alım: {values[3]}\nSatım: {values[2]}", inline=True)
        embed.add_field(name="Altın (gr)",value=f"Alım: {values[5]}\nSatım: {values[4]}", inline=True)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Exchange(bot))