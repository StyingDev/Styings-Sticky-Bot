import discord
from discord import app_commands
from discord.ext import commands
import datetime
from typing import Optional

from stickyCommon import respond, post_sticky_message, DEFAULT_THRESHOLD


class SetStickyEmbedCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='setstickyembed', description='Set a sticky message with an embed.')
    @app_commands.describe(message="The sticky message content", color="Hex color, e.g. #5865F2", title="Embed title", image="Image URL")
    @app_commands.checks.has_permissions(manage_messages=True)
    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: i.channel_id)
    async def setstickyembed(self, interaction: discord.Interaction, message: str, color: Optional[str] = None, title: Optional[str] = None, image: Optional[str] = None):
        parsed_color = 0x747c8b
        if color:
            try:
                parsed_color = int(color.lstrip('#'), 16)
            except ValueError:
                await respond(interaction, "Invalid color. Use a hex code like `#5865F2`.", ephemeral=True)
                return

        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        await self.bot.db.upsert_sticky(
            interaction.channel.id, interaction.guild.id,
            message=message, message_id=None, is_embed=1, active=1,
            threshold=(self.bot.db.get(interaction.channel.id) or {}).get('threshold', DEFAULT_THRESHOLD),
            embed_color=f"{parsed_color:06x}", embed_title=title or "Sticky Message", embed_image=image,
            created_by=interaction.user.id, created_at=now, updated_by=interaction.user.id, updated_at=now,
        )
        try:
            await post_sticky_message(self.bot, interaction.channel)
        except discord.Forbidden:
            await respond(interaction, "Sticky embed saved, but I don't have permission to send/delete messages in this channel.", ephemeral=True)
            return
        await respond(interaction, "Sticky embed message set!")


async def setup(bot: commands.Bot):
    await bot.add_cog(SetStickyEmbedCog(bot))
