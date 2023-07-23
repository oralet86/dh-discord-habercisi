from discord.ext import tasks, commands
import discord
try:
  import cogs.forum as forum
except ModuleNotFoundError:
   import forum

# from time import perf_counter

TEST = 1100730493319774218 # Test channel

forum.load_subforums() # Used to load subforum data from the json

def main() -> None:
  for sf in forum.Subforum.subforum_list:
    print(f"ID: {sf.id}, Channels: {sf.channels}, Latest: {sf.latest}")


class ForumChecker(commands.Cog):
  def __init__(self, bot) -> None:
    self.bot = bot
    self.check.start()


  async def cog_unload(self) -> None:
    await self.check.cancel()


  @tasks.loop(seconds=60)
  async def check(self) -> None:
    # start = perf_counter() Used for speed diagnosis
    test_channel = self.bot.get_channel(TEST)

    await test_channel.send("Yeni konulara bakıyorum!")

    for subforum in forum.Subforum.subforum_list:
      new_posts = await subforum.check_posts()

      for new_post in new_posts:
        for channel_id in subforum.channels:
          channel: discord.TextChannel = self.bot.get_channel(channel_id)

          await channel.send(f"{subforum.title} Forumlarında yeni konu!\nLink: https://forum.donanimhaber.com{new_post.href}")
      

    # print(f"Completed Execution in {perf_counter() - start} seconds")


  @check.before_loop
  async def before_my_task(self) -> None:
    await self.bot.wait_until_ready()


  @commands.command()
  async def ekle(self, ctx: commands.Context, link:str=None) -> None:
    match await forum.Subforum.add_channel(ctx.channel.id, link):
      case 0:
          await ctx.send(f"İşlem başarılı! Artık `{link}` forumunda yeni bir konu açıldığında `{ctx.channel.name}` kanalına mesaj atılacak.")
      case 1:
          await ctx.send("Verilen link geçerli bir DonanımHaber linki değil.")
      case 2:
          await ctx.send(f"`{link}` forumu `{ctx.channel.name}` kanalında zaten takip ediliyor!")


  @commands.command()
  async def cikar(self, ctx: commands.Context, link:str= None) -> None:
    match await forum.Subforum.remove_channel(ctx.channel.id, link):
      case 0:
          await ctx.send(f"İşlem başarılı! Artık `{ctx.channel.name}` kanalında herhangi bir forum takip edilmeyecek.")
      case 1:
          await ctx.send(f"İşlem başarılı! Artık `{ctx.channel.name}` kanalında `{link}` forumu takip edilmeyecek.")
      case 2:
          await ctx.send(f"`{link}` forumu `{ctx.channel.name}` kanalında zaten takip edilmiyor.")


if __name__ == '__main__':
  main()

else:
  async def setup(bot) -> None:
    await bot.add_cog(ForumChecker(bot))
