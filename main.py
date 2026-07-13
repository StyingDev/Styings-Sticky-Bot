import discord
from discord import app_commands
from discord.ext import commands
import os
import logging
import asyncio
from dotenv import load_dotenv

from database import Database
from stickyCommon import respond

load_dotenv()
TOKEN = os.getenv("TOKEN")

logging.basicConfig(level=logging.WARNING)

# Only request what's actually needed
intents = discord.Intents.default()
intents.message_content = True

# Slash commands only: prefix is unused since no prefix/hybrid commands are registered
bot = commands.Bot(command_prefix=commands.when_mentioned, intents=intents)
bot.db = Database()


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="linktr.ee/Stying"))
    print(f'Logged in as {bot.user.name}')
    if not getattr(bot, 'synced', False):
        await bot.tree.sync()
        bot.synced = True


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    """Handle slash command errors for every cog's commands."""
    error = getattr(error, 'original', error)

    if isinstance(error, app_commands.MissingPermissions):
        await respond(interaction, "You do not have the required permissions to run this command.", ephemeral=True)
    elif isinstance(error, app_commands.NoPrivateMessage):
        await respond(interaction, "This command can only be used inside a server.", ephemeral=True)
    elif isinstance(error, app_commands.CommandOnCooldown):
        await respond(interaction, f"This command is on cooldown. Try again in {error.retry_after:.1f}s.", ephemeral=True)
    elif isinstance(error, discord.Forbidden):
        await respond(interaction, "I don't have permission to do that in this channel.", ephemeral=True)
    else:
        logging.error(f"Error occurred in command {interaction.command}: {error}")
        await respond(interaction, "An unexpected error occurred while running that command.", ephemeral=True)


async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("_"):
            await bot.load_extension(f"cogs.{filename[:-3]}")
            print(f"Loaded cog: {filename[:-3]}")


async def main():
    await bot.db.connect()
    try:
        async with bot:
            await load_cogs()
            await bot.start(TOKEN)
    finally:
        await bot.db.close()


if __name__ == "__main__":
    asyncio.run(main())
