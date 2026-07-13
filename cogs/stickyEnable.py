import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

from stickyCommon import respond, post_sticky_message


class StickyEnableCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='stickyenable', description='Re-enable a disabled sticky message.')
    @app_commands.describe(channel="Channel to target (defaults to this channel)")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.guild_only()
    async def stickyenable(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
        target = channel or interaction.channel
        info = self.bot.db.get(target.id)

        if not info or info['guild_id'] != interaction.guild.id:
            await respond(interaction, f"No sticky message set in {target.mention}.", ephemeral=True)
            return

        await self.bot.db.upsert_sticky(target.id, interaction.guild.id, active=1)
        try:
            await post_sticky_message(self.bot, target)
        except discord.Forbidden:
            await respond(interaction, f"Sticky re-enabled, but I don't have permission to send/delete messages in {target.mention}.", ephemeral=True)
            return
        await respond(interaction, f"Sticky message re-enabled in {target.mention}!")


async def setup(bot: commands.Bot):
    await bot.add_cog(StickyEnableCog(bot))
