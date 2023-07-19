import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv(".env")

TOKEN = os.getenv("TOKEN")

PREFIX = "dh"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents)


def main() -> None:
    run_bot()


def run_bot() -> None:
    @bot.event
    async def on_ready() -> None:
        print(f"{bot.user} is ready!")
        await bot.load_extension("cogs.checker")
        # await bot.load_extension("cogs.yirmidort")
        await bot.load_extension("cogs.doviz")

    @bot.event
    async def on_command_error(ctx, error) -> None:
        print(f"ERROR: {error}")
        await ctx.send(f"Yanlış komut! Geçerli komutları ve kullanımlarını görmek için: {PREFIX}help")

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return

        # print(f"{str(message.author)} said '{str(message.content)}' in {str(message.channel)}")

        await bot.process_commands(message)

    bot.run(TOKEN)

if __name__ == '__main__':
    main()
