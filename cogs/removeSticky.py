import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

from stickyCommon import respond


class RemoveStickyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='removesticky', description='Remove the sticky message in the current or specified channel.')
    @app_commands.describe(channel="Channel to target (defaults to this channel)")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.guild_only()
    async def removesticky(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
        target = channel or interaction.channel
        info = self.bot.db.get(target.id)

        if not info or info['guild_id'] != interaction.guild.id:
            await respond(interaction, f"No sticky message found for {target.mention}.", ephemeral=True)
            return

        await self.bot.db.delete_sticky(target.id)
        if info.get('message_id'):
            try:
                old_message = await target.fetch_message(info['message_id'])
                await old_message.delete()
            except (discord.NotFound, discord.Forbidden):
                pass

        await respond(interaction, f"Sticky message removed for {target.mention}.")


async def setup(bot: commands.Bot):
    await bot.add_cog(RemoveStickyCog(bot))
