import discord
from discord.ext import commands, tasks
import logging

from stickyCommon import estimate_weight, post_sticky_message, DEFAULT_THRESHOLD


class StickyListenerCog(commands.Cog):
    """Background sticky behavior: activity-based reposting and a safety-net check.
    Not tied to any single slash command."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def cog_load(self):
        if not self.check_sticky_messages.is_running():
            self.check_sticky_messages.start()

    async def cog_unload(self):
        self.check_sticky_messages.cancel()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or message.guild is None:
            return

        info = self.bot.db.get(message.channel.id)
        if not info or not info.get('active'):
            return

        info['weight'] = info.get('weight', 0) + estimate_weight(message.content)
        if info['weight'] >= info.get('threshold', DEFAULT_THRESHOLD):
            info['weight'] = 0
            try:
                await post_sticky_message(self.bot, message.channel)
            except discord.Forbidden:
                logging.warning(f"Missing permissions to repost sticky in channel {message.channel.id}")
            except Exception as e:
                logging.error(f"Error reposting sticky in channel {message.channel.id}: {e}")

    @tasks.loop(minutes=5)
    async def check_sticky_messages(self):
        """Safety net: repost any sticky whose message was deleted or never posted.
        (Normal reposting is handled by on_message via the weight threshold.)"""
        for channel_id, info in list(self.bot.db.cache.items()):
            if not info.get('active'):
                continue

            channel = self.bot.get_channel(channel_id)
            if channel is None:
                continue

            try:
                if info.get('message_id'):
                    await channel.fetch_message(info['message_id'])
                else:
                    await post_sticky_message(self.bot, channel)
            except discord.NotFound:
                await post_sticky_message(self.bot, channel)
            except discord.Forbidden:
                logging.warning(f"Missing permissions in channel {channel_id} for sticky safety check.")
            except Exception as e:
                logging.error(f"Error in check_sticky_messages for channel {channel_id}: {e}")

    @check_sticky_messages.before_loop
    async def before_check_sticky_messages(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(StickyListenerCog(bot))
