from os.path import exists, getsize
from bs4 import BeautifulSoup
from typing import List
import asyncio
import aiohttp
import json

DOMAIN = "donanimhaber.com"
FORUMS_FILE_NAME = "forums.json"


def main() -> None:
  pass
  # Put your tests here


def getid(link: str) -> int:
  id_location = link.rfind("-")

  if id_location != -1:
    return (link[id_location+1:])


class Subforum():
  subforum_list = []

  def __init__(self, link, channels=[], latest=0, is_startup=0, title=None) -> None:
    if is_startup or asyncio.run(isvalid(link)):
      self.id = link if is_startup else getid(link)               # Since the id is already stored,
      self.channels = channels                                    # link is actually an id if it's loading up data from a json file
      self.latest = latest
      self.title = title                                          # Title is actually loaded when checking for new posts so we don't request the same page twice
      Subforum.subforum_list.append(self)
    else:
      raise ValueError("Invalid forum link")


  async def check_posts(self) -> List["ForumPost"]:
    posts = []
    latest_ids = []

    async with aiohttp.ClientSession() as session:
      async with session.get(f'https://forum.donanimhaber.com/placeholder--{self.id}') as response:
        soup = BeautifulSoup(await response.text(),"html.parser")

        if self.title is None:
          self.title = soup.title.text[:soup.title.text.find(" Forumları")]

        post_divs = soup(class_="kl-icerik-satir yenikonu",limit=15) # Look at the top 15 posts
        for post in post_divs:
          post_href = post.select_one("a").get("href")               # Get the href, for example: /shopflix-guvenilir-mi--155719413

          # This is for diagnostics
          # print(f"post href: {getid(post_href)}, self.latest: {self.latest}, should the post be added: {int(getid(post_href))>self.latest}")

          if int(getid(post_href)) > self.latest:
            latest_ids.append(int(getid(post_href)))
            posts.append(await ForumPost.create(post_href))

    if len(latest_ids) != 0:
      self.latest = max(latest_ids)
      Subforum.save_subforums()

    return posts


  async def add_channel(channel_id, link):
    if link is None:
      return 1
    id = getid(link)

    for subforum in Subforum.subforum_list:
      if subforum.id == id:
        if id in subforum.channels:
          return 2
        else:
          subforum.channels.append(channel_id)
          Subforum.save_subforums()
          return 0

    try:
      new_subforum = Subforum(link)
      Subforum.save_subforums()
      return 0
    except ValueError:
      return 1


  async def remove_channel(channel_id, link:str= None):
    if link is None:
      for subforum in Subforum.subforum_list:
        if channel_id in subforum.channels:
          subforum.channels.remove(channel_id)

      Subforum.save_subforums()
      return 0

    else:
      for subforum in Subforum.subforum_list:
        if subforum.id == getid(link):
          if channel_id in subforum.channels:
            subforum.channels.remove(channel_id)

            Subforum.save_subforums()
            return 1

    return 2


  @classmethod
  def load_subforums(cls) -> list["Subforum"]:
    if exists(FORUMS_FILE_NAME) and getsize(FORUMS_FILE_NAME) != 0:        # If the .json file does exist, it loads in the data from that file.
      with open(FORUMS_FILE_NAME,"r") as json_file:
        for subforum_data in json.load(json_file):
          subforum = Subforum(link=subforum_data['id'],channels=subforum_data['channels'],
                              latest=int(subforum_data['latest']),is_startup=1,title=subforum_data['title'])
    else:
      with open(FORUMS_FILE_NAME,"w") as json_file:
        json.dump([],json_file)


  @classmethod
  def save_subforums(cls) -> None:
    save_file = []

    for subforum in Subforum.subforum_list:
      save_file.append({"id": subforum.id, "channels": subforum.channels, "latest": subforum.latest, "title": subforum.title})

    with open(FORUMS_FILE_NAME,"w") as json_file:
      json.dump(save_file,json_file, indent=2)


class ForumPost():
  def __init__(self, href) -> None:
    self.href = href
    self.title = None
    self.author = None
    self.avatar = None
    self.content = None


  @classmethod
  async def create(cls, href) -> None:  # Got to use this to create new objects because of stupid async logic
    forumpost = ForumPost(href)
    await forumpost.get_post_info()
    return forumpost


  async def get_post_info(self) -> None:
    async with aiohttp.ClientSession() as session:
      async with session.get(f'https://forum.donanimhaber.com{self.href}') as response:
        soup = BeautifulSoup(await response.text(),"html.parser")

        self.title = soup.find("h1",class_="kl-basligi upInfinite").text.strip()
        author_info = soup.find("aside",class_="ki-cevapsahibi")
        self.author = author_info.find("div",class_="ki-kullaniciadi member-info").find("a").find("b").text
        try:
          self.avatar = author_info.find("div",class_="content-holder").find("a",class_="ki-avatar").find("img").attrs["src"]
        except AttributeError:
          pass
        content_json = soup.find("script",type="application/ld+json").text    # The easiest way to get the post content seems to be through this element
        content_start = content_json.index("articleBody")+15                  # But this element consists of a very large json file
        content_end =  content_json.index("articleS")-4                       # And since it wouldn't make sense to parse everything just to get one thing
        self.content = content_json[content_start:content_end]                # We just use string manipulation
                                                                              # The +15 and -4 is to remove some extra characters that index() leaves in


async def isvalid(link) -> bool:  # Checks if the link leads to a valid DonanımHaber forum
  if DOMAIN in link:
    try:
      async with aiohttp.ClientSession() as session:
        async with session.get(link) as response:
          return response.status == 200

    except aiohttp.ClientError:
      return False

  return False

if __name__ == '__main__':
  main()