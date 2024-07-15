from os.path import exists, getsize
from bs4 import BeautifulSoup
from typing import List
from environmental_variables import DB_DIRECTORY, DH_DOMAIN
import aiohttp
import json


def main() -> None:
  print(get_topic_id("/apple-iphone-firsatlari-tum-modeller-ana-konu--121084032?isLink=true"))
  print(get_subforum_id("https://forum.donanimhaber.com/egitim-ve-sinavlar-genel-sohbet--f2642"))
  print(clean_link("/apple-iphone-firsatlari-tum-modeller-ana-konu--121084032?isLink=true"))
  # Put your tests here


def get_subforum_id(link: str) -> str:
  """Gets the ID of a forum subforum from a DonanimHaber link

  Args:
      link (str): A DonanimHaber link that leads to a forum subforum

  Raises:
      ValueError: If the ID couldn't be extracted from the link

  Returns:
      str: The ID of the forum subforum
  """
  link = clean_link(link)
  dash_index = link.rfind("--")
  if dash_index == -1:
    raise ValueError("Couldn't extract ID from link")
  return link[dash_index+2:]


def get_topic_id(link: str) -> int:
  """Gets the ID of a forum topic from a DonanimHaber link

  Args:
      link (str): A DonanimHaber link that leads to a forum topic

  Raises:
      ValueError: If the ID couldn't be extracted from the link

  Returns:
      int: The ID of the forum topic
  """
  link = clean_link(link)
  dash_index = link.rfind("-")
  if dash_index == -1:
    raise ValueError("Couldn't extract ID from link")
  return int(link[dash_index+1:])


def clean_link(link: str) -> str:
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


async def is_valid(link: str) -> bool:
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


class DHSubforum():
  """A class to represent a subforum in Donanimhaber."""
  subforum_list: List["DHSubforum"] = []

  def __init__(self, id: str = "", channels: List[int] = [], latest: int = 0, title: str = "") -> None:
    """
      DO NOT USE THIS METHOD TO CREATE NEW OBJECTS. Use the create() method instead.

      This constructor cannot fetch the necessary info from the website.
      Only use this if you're loading the object from a file.
    """
    self.id: str = id
    self.channels: List[int] = channels
    self.latest: int = latest
    self.title: str = title
    
    self.__class__.subforum_list.append(self)


  @classmethod
  async def create(cls, link) -> "DHSubforum":  # Got to use this to create new objects because of stupid async logic
    """Creates a new DHSubforum object from the link of a subforum.

    Args:
        link (str): The link to the subforum page.

    Returns:
        DHSubforum: The created DHSubforum object.
    """
    if await is_valid(link):
      subforum = DHSubforum(id=get_subforum_id(link))

      return subforum
    else:
      raise ValueError("Invalid forum link")
  
  
  @classmethod
  async def get_list(cls, id) -> List["DHSubforum"]:
    """Gets a list of DHSubforum objects that send updates to a specific channel.

    Returns:
        List[DHSubforum]: A list of DHSubforum objects that send alerts to the channel.
    """
    result = []
    for subforum in DHSubforum.subforum_list:
      if id in subforum.channels:
        result.append(subforum)
    
    return result


  async def check_posts(self) -> List["DHTopic"]:
    """The method that checks for new posts in the subforum.

    Returns:
        List[DHTopic]: A list of new posts in the subforum in the form of DHTopic objects.
    """
    posts = []
    latest_ids = []

    async with aiohttp.ClientSession() as session:
      async with session.get(f'https://forum.donanimhaber.com/placeholder--{self.id}') as response:
        soup = BeautifulSoup(await response.text(),"html.parser")

        if self.title is None:
          self.title = soup.title.text[:soup.title.text.find(" Forumları")] # type: ignore

        # Look at the top 15 posts
        post_divs = soup(class_="kl-icerik-satir yenikonu",limit=15)

        for post in post_divs:
          # Get the href, for example: /shopflix-guvenilir-mi--155719413
          post_href = clean_link(post.select_one("a").get("href"))
          
          if get_topic_id(post_href) > self.latest:
            latest_ids.append(get_topic_id(post_href))
            posts.append(await DHTopic.create(post_href))

    if len(latest_ids) != 0:
      self.latest = max(latest_ids)
      DHSubforum.save_subforums()

    return posts


  @classmethod
  async def add_channel(cls, channel_id: int, link: str | None) -> int:
    """Adds a discord channel to the list of channels that receive updates from a subforum.

    Args:
        channel_id (int): The ID of the discord channel that will receive updates.
        link (str | None): The link to the subforum page. Defaults to None.

    Returns:
        int: 0 if the operation is successful, 1 if the link is invalid or a link hasn't been provided, 2 if the channel is already in the list.
    """
    if link is None:
      return 1
    id = get_subforum_id(link)

    for subforum in cls.subforum_list:
      if subforum.id == id:
        if id in subforum.channels:
          return 2
        else:
          subforum.channels.append(channel_id)
          cls.save_subforums()
          return 0

    try:
      await cls.create(link)
      cls.save_subforums()
      return 0
    except ValueError:
      return 1


  @classmethod
  async def remove_channel(cls, channel_id: int, link: str | None = None) -> int:
    """Removes a discord channel from the list of channels that receive updates from a subforum.

    Args:
        channel_id (int): The ID of the discord channel that will be removed.
        link (str | None, optional): The link to the subforum page. Removes all subforums updates from the discord channel if no link is provided. Defaults to None.

    Returns:
        int: _description_
    """
    if link is None:
      for subforum in cls.subforum_list:
        if channel_id in subforum.channels:
          subforum.channels.remove(channel_id)

      cls.save_subforums()
      return 0

    else:
      for subforum in cls.subforum_list:
        if subforum.id == get_subforum_id(link):
          if channel_id in subforum.channels:
            subforum.channels.remove(channel_id)

            cls.save_subforums()
            return 1
    return 2


  @classmethod
  def load_subforums(cls):
    if exists(DB_DIRECTORY) and getsize(DB_DIRECTORY) != 0:        # If the .json file does exist, it loads in the data from that file.
      with open(DB_DIRECTORY,"r") as json_file:
        for subforum_data in json.load(json_file):
          DHSubforum(id=subforum_data['id'],channels=subforum_data['channels'],
                      latest=int(subforum_data['latest']),title=subforum_data['title'])
    else:
      with open(DB_DIRECTORY,"w") as json_file:
        json.dump([],json_file)


  @classmethod
  def save_subforums(cls) -> None:
    save_file = []

    for subforum in DHSubforum.subforum_list:
      save_file.append({"id": subforum.id, "channels": subforum.channels, "latest": subforum.latest, "title": subforum.title})

    with open(DB_DIRECTORY,"w") as json_file:
      json.dump(save_file,json_file, indent=2)


class DHTopic():
  """A class to represent a topic in Donanimhaber."""
  def __init__(self, href: str) -> None:
    self.href = href
    self.title: str = ""
    self.author: str | None = None
    self.avatar: str | None = None
    self.content: str = ""


  @classmethod
  async def create(cls, href) -> "DHTopic":  # Got to use this to create new objects because of stupid async logic x2
    forumpost = DHTopic(href)
    await forumpost.get_topic_info()
    return forumpost


  async def get_topic_info(self) -> None:
    """Gets the necessary information about the topic.

    Raises:
        Exception: If any one part of the information can't be fetched. (Except for the avatar, since it's optional)
    """
    async with aiohttp.ClientSession() as session:
      async with session.get(f'https://forum.donanimhaber.com{self.href}') as response:
        try:
          soup = BeautifulSoup(await response.text(),"html.parser")
        except Exception as e:
          raise Exception(f"Coudln't parse the html: {e}")
        
        try:
          self.title = soup.find("h1",class_="kl-basligi upInfinite").text.strip() # type: ignore
        except Exception as e:
          raise Exception(f"Couldn't fetch the title: {e}")
        
        try:
          author_info = soup.find("aside",class_="ki-cevapsahibi")
        except Exception as e:
          raise Exception(f"Couldn't fetch the author info: {e}")
        
        try:
          if author_info is not None:
            self.author = author_info.find("div", class_="ki-kullaniciadi member-info").find("a").find("b").text # type: ignore
        except Exception as e:
          raise Exception(f"Couldn't fetch the author: {e}")

        try:
          self.avatar = author_info.find("div",class_="content-holder").find("a",class_="ki-avatar").find("img").attrs["src"] # type: ignore
        except AttributeError as e:
          print(f"Couldn't fetch the avatar: {e}")
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
          raise Exception(f"Couldn't fetch the content: {e}")


if __name__ == '__main__':
  main()