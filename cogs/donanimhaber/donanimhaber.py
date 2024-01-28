from discord.ext import tasks, commands
import discord
try:
  import cogs.donanimhaber.forum as forum
except ModuleNotFoundError:
  import forum

# from time import perf_counter

TEST = 1100730493319774218 # Test channel

forum.Subforum.load_subforums() # Used to load subforum data from the json

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
    try:
      test_channel = self.bot.get_channel(TEST)
      await test_channel.send("Yeni konulara bakıyorum!")
    except Exception as e:
      print(f"\"Yeni konulara bakıyorum!\" Mesajı gönderilirken bir hata oluştu: {e}")

    try:
      for subforum in forum.Subforum.subforum_list:
        new_posts = await subforum.check_posts()

        for new_post in new_posts:
          embed = make_embed(new_post)
          view = make_view(new_post)

          for channel_id in subforum.channels:
            channel: discord.TextChannel = self.bot.get_channel(channel_id)

            await channel.send(embed=embed,view=view)
    except Exception as e:
      print(f"Hata: {e}")
      await test_channel.send(f"Hata: {e}")


    # print(f"Completed Execution in {perf_counter() - start} seconds")


  @check.before_loop
  async def before_my_task(self) -> None:
    await self.bot.wait_until_ready()

  @commands.command()
  async def ekle(self, ctx: commands.Context, link:str=None) -> None:
    result = await forum.Subforum.add_channel(ctx.channel.id, link)
    match result:
      case 0:
          await ctx.send(f"İşlem başarılı! Artık `{link}` forumunda yeni bir konu açıldığında `{ctx.channel.name}` kanalına mesaj atılacak.")
      case 1:
          await ctx.send("Verilen link geçerli bir DonanımHaber linki değil.")
      case 2:
          await ctx.send(f"`{link}` forumu `{ctx.channel.name}` kanalında zaten takip ediliyor!")


  @commands.command()
  async def cikar(self, ctx: commands.Context, link:str=None) -> None:
    result = await forum.Subforum.remove_channel(ctx.channel.id, link) 
    match result:
      case 0:
          await ctx.send(f"İşlem başarılı! Artık `{ctx.channel.name}` kanalında herhangi bir forum takip edilmeyecek.")
      case 1:
          await ctx.send(f"İşlem başarılı! Artık `{ctx.channel.name}` kanalında `{link}` forumu takip edilmeyecek.")
      case 2:
          await ctx.send(f"`{link}` forumu `{ctx.channel.name}` kanalında zaten takip edilmiyor.")
  

  @commands.command()
  async def liste(self, ctx: commands.Context) -> None:
    result = await forum.Subforum.get_list(ctx.channel.id)
    return_str = f"Bu sohbette takip edilen altforum sayısı: {len(result)}"

    for subforum in result:
      return_str+=f"\n- Başlık: `{subforum.title}`, Link: `https://forum.donanimhaber.com/burasi-aslinda-onemsiz--{subforum.id}`"
    
    return_str+=f"\nHerhangi bir altforumu takip etmeyi 'dhcikar `forum linki`' komutu ile bırakabilirsiniz."
    
    await ctx.send(return_str)


def make_embed(post: forum.ForumPost) -> discord.Embed:
  try:
    embed = discord.Embed(title="Yeni Konu!", color=discord.Colour.blurple(), description=post.author)
    value = post.content if len(post.content) < 512 else f"{post.content[:512]}..."    # Crop any content over 512 characters to save screenspace
    embed.add_field(name=post.title,value=value)
    if post.avatar is not None:
      embed.set_thumbnail(url=post.avatar)
    return embed
  except Exception as e:
    raise Exception(f"make_embed/{e}")


def make_view(post) -> discord.ui.View:
  try:
    computer_button = discord.ui.Button(style=discord.ButtonStyle.link, label="PC Link",url=f"https://forum.donanimhaber.com{post.href}")
    mobile_button = discord.ui.Button(style=discord.ButtonStyle.link, label="Mobil Link",url=f"https://mobile.donanimhaber.com{post.href}")
    view = discord.ui.View()
    view.add_item(computer_button)
    view.add_item(mobile_button)
    return view
  except Exception as e:
    raise Exception(f"make_view/{e}")


if __name__ == '__main__':
  main()

else:
  async def setup(bot) -> None:
    await bot.add_cog(ForumChecker(bot))