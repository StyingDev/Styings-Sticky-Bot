import discord
from discord import app_commands
from discord.ext import commands
import datetime

from stickyCommon import respond, post_sticky_message, DEFAULT_THRESHOLD


class SetStickyCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='setsticky', description='Set a sticky message in this channel.')
    @app_commands.describe(message="The sticky message content")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.channel_id)
    async def setsticky(self, interaction: discord.Interaction, message: str):
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        await self.bot.db.upsert_sticky(
            interaction.channel.id, interaction.guild.id,
            message=message, message_id=None, is_embed=0, active=1,
            threshold=(self.bot.db.get(interaction.channel.id) or {}).get('threshold', DEFAULT_THRESHOLD),
            embed_color=None, embed_title=None, embed_image=None,
            created_by=interaction.user.id, created_at=now, updated_by=interaction.user.id, updated_at=now,
        )
        try:
            await post_sticky_message(self.bot, interaction.channel)
        except discord.Forbidden:
            await respond(interaction, "Sticky message saved, but I don't have permission to send/delete messages in this channel.", ephemeral=True)
            return
        await respond(interaction, "Sticky message set!")


async def setup(bot: commands.Bot):
    await bot.add_cog(SetStickyCog(bot))
