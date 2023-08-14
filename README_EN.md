# Donanimhaber Discord Habercisi

This bot sends messages to a selected Discord channel when it detects a new post in the specified donanimhaber forums.
# Getting Started

    Clone the repository to your local machine.
    Install the dependencies with pip install -r requirements.txt.
    Create a Discord bot and add it to your server.
    Copy the bot's token and paste it into the TOKEN variable in '.env'.
    Run the bot with python 'main.py'.

# Usage

The bot will automatically start monitoring the specified donanimhaber forums for new posts. When it detects a new post, it will send a message to the Discord channel that you specified. The message will include the title of the post, the author's name, the avatar of the author (if possible), the content of the post (If the post content is longer than 512 characters, the bot will automatically shorten it) and two links that lead to post in mobile.donanimhaber.com and forum.donanimhaber.com respectively.

# Configuration

The bots prefix is 'dh' by default, you can change it by editing the PREFIX variable in 'main.py'. You can use the following commands to use the bot:

    ekle 'link': Adds the forum linked to the discord channels watch list, any new post in that forum will be sent to that channel.
    cikar 'link' (Optional): Removes the forum linked from the discord channels watch list. If no link is provided, all the added forums are removed.   

# Troubleshooting

If you have any problems with the bot, please open an issue on the GitHub repository.
