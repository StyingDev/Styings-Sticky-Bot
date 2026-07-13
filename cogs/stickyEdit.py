import discord
from discord import app_commands
from discord.ext import commands
import datetime

from stickyCommon import respond, post_sticky_message


class StickyEditCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='stickyedit', description='Edit the text of the existing sticky in this channel.')
    @app_commands.describe(message="The new sticky message content")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.channel_id)
    async def stickyedit(self, interaction: discord.Interaction, message: str):
        if self.bot.db.get(interaction.channel.id) is None:
            await respond(interaction, "No sticky message set in this channel. Use `/setsticky` or `/setstickyembed` first.", ephemeral=True)
            return

        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        await self.bot.db.upsert_sticky(interaction.channel.id, interaction.guild.id, message=message, updated_by=interaction.user.id, updated_at=now)
        try:
            await post_sticky_message(self.bot, interaction.channel)
        except discord.Forbidden:
            await respond(interaction, "Sticky message updated, but I don't have permission to send/delete messages in this channel.", ephemeral=True)
            return
        await respond(interaction, "Sticky message updated!")


async def setup(bot: commands.Bot):
    await bot.add_cog(StickyEditCog(bot))
