from os.path import exists, getsize
from bs4 import BeautifulSoup
from typing import List
from environmental_variables import DB_DIRECTORY, DH_DOMAIN
import aiohttp
import json


def main() -> None:
  print(getTopicID("/apple-iphone-firsatlari-tum-modeller-ana-konu--121084032?isLink=true"))
  print(getSubforumID("https://forum.donanimhaber.com/egitim-ve-sinavlar-genel-sohbet--f2642"))
  print(cleanLink("/apple-iphone-firsatlari-tum-modeller-ana-konu--121084032?isLink=true"))
  # Put your tests here


def getSubforumID(link: str) -> str:
  """Gets the ID of a forum subforum from a DonanimHaber link

  Args:
      link (str): A DonanimHaber link that leads to a forum subforum

  Raises:
      ValueError: If the ID couldn't be extracted from the link

  Returns:
      str: The ID of the forum subforum
  """
  link = cleanLink(link)
  dash_index = link.rfind("--")
  if dash_index == -1:
    raise ValueError("Couldn't extract ID from link")
  return link[dash_index+2:]


def getTopicID(link: str) -> int:
  """Gets the ID of a forum topic from a DonanimHaber link

  Args:
      link (str): A DonanimHaber link that leads to a forum topic

  Raises:
      ValueError: If the ID couldn't be extracted from the link

  Returns:
      int: The ID of the forum topic
  """
  link = cleanLink(link)
  dash_index = link.rfind("-")
  if dash_index == -1:
    raise ValueError("Couldn't extract ID from link")
  return int(link[dash_index+1:])


def cleanLink(link: str) -> str:
  """Cleans extra query parameters from the end of a DonanimHaber link

  Args:
      link (str): The link to be cleaned

  Returns:
      str: The cleaned link
  """
  dash_index = link.rfind("--") + 2 # Find end of the link
  question_index = link[dash_index:].find("?")
  if question_index == -1:
    # There are no query parameters
    return link
  else:
    return link[:dash_index+question_index]


async def isValid(link: str) -> bool:
  """Checks if the link leads to a valid DonanimHaber page

  Args:
      link (str): The link to be checked

  Returns:
      bool: True if the link is valid, False otherwise
  """
  if DH_DOMAIN in link:
    try:
      async with aiohttp.ClientSession() as session:
        async with session.get(link) as response:
          return response.status == 200
    except aiohttp.ClientError:
      return False
  return False


class Subforum():
  subforum_list: List["Subforum"] = []


  def __init__(self) -> None:
    self.id = None
    self.channels = None
    self.latest = None
    self.title = None
    Subforum.subforum_list.append(self)
  

  def remove(self) -> None:
    Subforum.subforum_list.remove(self)
    del self
    Subforum.save_subforums()


  async def get_subforum_info(self, link, channels=[], latest=0, title=None) -> None:
    if await isValid(link):
      self.id = getSubforumID(link)
      self.channels: List[int] = channels
      self.latest: int = latest
      self.title: str = title                                          # Title is actually loaded when checking for new posts so we don't request the same page twice
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
        
        try:
          # Look at the top 15 posts
          post_divs = soup(class_="kl-icerik-satir yenikonu",limit=15)
        except Exception as e:
          raise Exception(f"check_posts/creating post divs/{e}")

        for post in post_divs:
          try:
            # Get the href, for example: /shopflix-guvenilir-mi--155719413
            post_href = cleanLink(post.select_one("a").get("href"))
          except Exception as e:
            raise Exception(f"check_posts/creating post divs/{e}")
          
          if getTopicID(post_href) > self.latest:
            try:
              latest_ids.append(getTopicID(post_href))
              posts.append(await ForumPost.create(post_href))
            except Exception as e:
              raise Exception(f"check_posts/\"{self.id}{post_href}\"/{e}")

          # This is for diagnostics
          # print(f"post href: {getid(post_href)}, self.latest: {self.latest}, should the post be added: {int(getid(post_href))>self.latest}")



    if len(latest_ids) != 0:
      self.latest = max(latest_ids)
      Subforum.save_subforums()

    return posts


  async def add_channel(channel_id, link) -> int:
    if link is None:
      return 1
    id = getSubforumID(link)

    for subforum in Subforum.subforum_list:
      if subforum.id == id:
        if id in subforum.channels:
          return 2
        else:
          subforum.channels.append(channel_id)
          Subforum.save_subforums()
          return 0

    try:
      await Subforum.create(link)
      Subforum.save_subforums()
      return 0
    except ValueError:
      return 1


  async def remove_channel(channel_id, link:str= None) -> int:
    if link is None:
      for subforum in Subforum.subforum_list:
        if channel_id in subforum.channels:
          subforum.channels.remove(channel_id)

      Subforum.save_subforums()
      return 0

    else:
      for subforum in Subforum.subforum_list:
        if subforum.id == getSubforumID(link):
          if channel_id in subforum.channels:
            subforum.channels.remove(channel_id)

            Subforum.save_subforums()
            return 1

    return 2


  @classmethod
  def load_from_file(cls, id, channels=[], latest=0, title=None) -> None:
    subforum = Subforum()
    subforum.id = id
    subforum.channels = channels
    subforum.latest = latest
    subforum.title = title


  @classmethod
  def load_subforums(cls) -> list["Subforum"]:
    if exists(DB_DIRECTORY) and getsize(DB_DIRECTORY) != 0:        # If the .json file does exist, it loads in the data from that file.
      with open(DB_DIRECTORY,"r") as json_file:
        for subforum_data in json.load(json_file):
          Subforum.load_from_file(id=subforum_data['id'],channels=subforum_data['channels'],
                  latest=int(subforum_data['latest']),title=subforum_data['title'])
    else:
      with open(DB_DIRECTORY,"w") as json_file:
        json.dump([],json_file)


  @classmethod
  def save_subforums(cls) -> None:
    save_file = []

    for subforum in Subforum.subforum_list:
      save_file.append({"id": subforum.id, "channels": subforum.channels, "latest": subforum.latest, "title": subforum.title})

    with open(DB_DIRECTORY,"w") as json_file:
      json.dump(save_file,json_file, indent=2)
  

  @classmethod
  async def create(cls, link) -> None:  # Got to use this to create new objects because of stupid async logic
    subforum = Subforum()
    await subforum.get_subforum_info(link=link)
    return subforum
  
  
  @classmethod
  async def get_list(cls, id) -> List["Subforum"]:
    result = []
    for subforum in Subforum.subforum_list:
      if id in subforum.channels:
        result.append(subforum)
    
    return result


class ForumPost():
  def __init__(self, href) -> None:
    self.href = href
    self.title = None
    self.author = None
    self.avatar = None
    self.content = None


  @classmethod
  async def create(cls, href) -> None:  # Got to use this to create new objects because of stupid async logic x2
    forumpost = ForumPost(href)
    await forumpost.get_post_info()
    return forumpost


  async def get_post_info(self) -> None:
    async with aiohttp.ClientSession() as session:
      async with session.get(f'https://forum.donanimhaber.com{self.href}') as response:
        try:
          soup = BeautifulSoup(await response.text(),"html.parser")
        except Exception as e:
          raise Exception(f"ForumPost/{e}")
        
        try:
          self.title = soup.find("h1",class_="kl-basligi upInfinite").text.strip()
        except Exception as e:
          raise Exception(f"ForumPost/title/{e}")
        
        try:
          author_info = soup.find("aside",class_="ki-cevapsahibi")
        except Exception as e:
          raise Exception(f"ForumPost/author_info/{e}")
        
        try:
          if author_info is not None:
            self.author = author_info.find("div",class_="ki-kullaniciadi member-info").find("a").find("b").text
        except Exception as e:
          raise Exception(f"ForumPost/author/{e}")

        try:
          self.avatar = author_info.find("div",class_="content-holder").find("a",class_="ki-avatar").find("img").attrs["src"]
        except AttributeError:
          pass

        try:
          # The easiest way to get the post content seems to be through this element, but this element consists of a very large json file
          # And since it wouldn't make sense to parse everything just to get one thing we just use string manipulation
          # The added +14 and -3 are to remove some extra characters that index() leaves in
          content_jsons = soup.findAll(name="script",type="application/ld+json")
          content_json = content_jsons[-1].text
          content_start = content_json.index("articleBody")+14
          content_end =  content_json.index("articleS")-3
          self.content = content_json[content_start:content_end].strip()

        except Exception as e:
          raise Exception(f"ForumPost/content/{e}")


if __name__ == '__main__':
  main()